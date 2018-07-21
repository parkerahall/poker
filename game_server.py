import sys, socket
from cards import Cards
from hands import Hands

MSG_SIZE = 512
NUM_CARDS_DEALT = 2
NUM_BETTING_ROUNDS = 4
ACTIONS = set(["check", "raise", "call", "fold", "chop"])
ROUND_DICT = {0: "PRE-FLOP", 1: "POST_FLOP", 2: "POST-TURN", 3: "POST-RIVER"}

def init_players():
    player_list = []
    player_dict = {}

    print("Please input players starting from the left of the dealer and rotating clockwise")

    next_player = raw_input("Input player name: ").upper()
    while next_player != "":
        if next_player in player_dict:
            print("Player already entered")
        else:
            bad_amount = True
            while bad_amount:
                try:
                    buy_in = int(raw_input("Buy-in amount: "))
                    bad_amount = False
                except:
                    print("Please enter a positive number")
            player_list.append(next_player)
            player_dict[next_player] = buy_in
        next_player = raw_input("Input player name: ").upper()

    return player_list, player_dict

def init_blinds():
    bad_small = True
    while bad_small:
        try:
            small_blind = int(raw_input("Small blind amount: "))
            bad_small = False
        except:
            print("Please enter a positive number")

    bad_big = True
    while bad_big:
        try:
            big_blind = int(raw_input("Big blind amount: "))
            if big_blind <= small_blind:
                print("Please enter a number greater than the small blind")
            else:
                bad_big = False
        except:
            print("Please enter a positive number")

    return small_blind, big_blind

def action_to_string(action):
    if len(action) == 1:
        return action[0]
    else:
        return action[0] + " " + str(action[1])

class Game_Server:
    def __init__(self, host, port, p_list, p_dict, sb, bb):
        self.host = host
        self.port = port
        
        self.player_list = p_list
        self.player_to_funds = p_dict
        self.player_to_hand = {player : None for player in self.player_list}
        self.player_to_client = {}
        
        self.small_blind = sb
        self.big_blind = bb        
        
        self.deck = Cards.make_deck()
        self.board = []

    def check_player_name(self, client, players_needed):
        attempts = 3
        players_string = ", ".join(self.player_list)
        client.send("Texas Holdem game with %s\n" % (players_string))
        client.send("Small blind at %d, big blind at %d\n" %(self.small_blind, self.big_blind))
        while attempts > 0:
            client.send("Please enter your name: ")
            name = client.recv(MSG_SIZE).strip().upper()
            if name in players_needed:
                client.send("Welcome!\n")
                return name
            else:
                client.send("Name not recognized\n")
                attempts -= 1
        client.send("Too many failed attempts. Please restart and try again.\n")
        client.close()
        return None

    def deal_cards(self, button):
        num_players = len(self.player_list)
        for i in range(num_players):
            current_player = self.player_list[(button + i) % num_players]
            self.player_to_hand[current_player] = [self.deck.pop()]
        for j in range(num_players):
            current_player = self.player_list[(button + j) % num_players]
            self.player_to_hand[current_player].append(self.deck.pop())

            client = self.player_to_client[current_player]
            client.send("Your hand: %s\n" % (str(self.player_to_hand[current_player])))

    def send_to_players(self, string):
        for player in self.player_to_client:
            self.player_to_client[player].send(string)

    def print_players(self):
        for name in self.player_to_funds:
            player_string = name + ":\t" + str(self.player_to_funds[name])
            print(player_string)
            self.send_to_players(player_string + "\n")

    def check_bet(self, player, bet_dict, max_bet, amount):
        client = self.player_to_client[player]
        try:
            extra = int(amount)
        except:
            client.send("Please enter an integer NUM for 'raise NUM'\n")
            return True
        if extra < 0:
            client.send("Please enter a positive integer NUM for 'raise NUM'\n")
            return True
        needed = max_bet + extra - bet_dict[player]
        bad_bet = self.player_to_funds[player] < needed
        if bad_bet:
            client.send("Not enough funds")
        return bad_bet

    def check_chop(self, player, bet_dict):
        client = self.player_to_client[player]
        players_remaining = sum([bet_dict[p] != "FOLD" for p in bet_dict])
        bad_chop = players_remaining != 2
        if bad_chop:
            client.send("Can only chop with two players remaining\n")
        return bad_chop

    def player_action(self, player, bet_dict, max_bet):
        client = self.player_to_client[player]
        client.send("Action to you: ")
        action = client.recv(MSG_SIZE).strip().split(' ')
        keyword = action[0].lower()
        if keyword == "":
            return None, None
        bad_keyword = keyword not in ACTIONS
        can_check = bet_dict[player] == max_bet
        bad_check = ((keyword == "check") and (not can_check))
        if keyword == "raise":
            not_allowed = self.check_bet(player, bet_dict, max_bet, action[1])
        elif keyword == "call":
            not_allowed = self.check_bet(player, bet_dict, max_bet, 0)
        elif keyword == "chop":
            not_allowed = self.check_chop(player, bet_dict)
        else:
            not_allowed = False
        bad_action = bad_keyword or bad_check or not_allowed
        return action, bad_action

    def handle_action(self, player, action, bet_dict, max_bet):
        keyword = action[0].lower()
        if keyword == "raise":
            max_diff = int(action[1])
            old_bet = bet_dict[player]
            pot_diff = max_bet + max_diff - old_bet
            self.player_to_funds[player] -= pot_diff
            bet_dict[player] += pot_diff

            return pot_diff, max_diff

        elif keyword == "call":
            old_bet = bet_dict[player]
            pot_diff = max_bet - old_bet
            self.player_to_funds[player] -= pot_diff
            bet_dict[player] += pot_diff

            return pot_diff, 0

        else:
            return 0, 0

    def betting_round(self, button, player_list, bet_dict, offset):
        start_index = button + offset
        num_players = len(player_list)
        max_bet = max([bet_dict[key] for key in bet_dict])

        new_pot = 0

        have_played = 0
        num_folded = 0

        while True:
            for i in range(len(player_list)):
                current_player = player_list[(start_index + i) % num_players]
                if bet_dict[current_player] != "FOLD":
                    if num_players - num_folded == 1:
                        return [current_player], new_pot

                    amount_to_call = max_bet - bet_dict[current_player]
                    client = self.player_to_client[current_player]
                    client.send("Amount to call: %d\n" % (amount_to_call))

                    action, bad_action = self.player_action(current_player, bet_dict, max_bet)

                    if action == None:
                        return action, action

                    while bad_action:
                        self.player_to_client[current_player].send("Please enter 'check', 'call', 'fold', or 'raise NUM'\n")
                        action, bad_action = self.player_action(current_player, bet_dict, max_bet)

                    action_string = action_to_string(action)
                    self.send_to_players("%s: %s\n" % (current_player, action_string))

                    add_to_pot, add_to_max = self.handle_action(current_player, action, bet_dict, max_bet)
                    new_pot += add_to_pot
                    max_bet += add_to_max

                    keyword = action[0].lower()
                    if keyword == "fold":
                        bet_dict[current_player] = "FOLD"
                        num_folded += 1
                    elif keyword == "chop":
                        current_bet = bet_dict[current_player]

                        self.player_to_funds[current_player] += current_bet
                        new_pot -= current_bet
                        bet_dict[current_player] = "FOLD"
                        winner = [p for p in bet_dict if bet_dict[p] != "FOLD"]
                        return winner, new_pot

                    have_played += 1

                    done = True
                    if have_played >= num_players:
                        new_player_list = []
                        for player in player_list:
                            in_for = bet_dict[player]
                            if in_for == max_bet:
                                new_player_list.append(player)
                            elif in_for != "FOLD":
                                done = False
                                break
                    else:
                        done = False

                    if done:
                        return new_player_list, new_pot

            start_index = 0

    def calculate_final_hands(self, player_list):
        hand_to_player = {}
        for player in player_list:
            cards = self.board + self.player_to_hand[player]
            hand = Hands.get_highest_hand(cards)
            
            hand_string = "%s: %s" % (player, hand)
            print(hand_string)
            self.send_to_players(hand_string + "\n")

            hand_tup = hand.get_tup_value()
            if hand_tup in hand_to_player:
                hand_to_player[hand_tup].append(player)
            else:
                hand_to_player[hand_tup] = [player]
        return hand_to_player

    def play_hand(self, button):
        pot = 0
        num_players = len(player_list)
        bet_dict = {player : 0 for player in player_list}

        sb = self.player_list[button % num_players]
        self.player_to_funds[sb] -= self.small_blind
        pot += self.small_blind
        bet_dict[sb] = self.small_blind

        bb = self.player_list[(button + 1) % num_players]
        self.player_to_funds[bb] -= self.big_blind
        pot += self.big_blind
        bet_dict[bb] = self.big_blind

        small_blind_string = "%s: bets %d (small blind)\n" % (sb, self.small_blind)
        big_blind_string = "%s: bets %d (big blind)\n" % (bb, self.big_blind)

        self.send_to_players(small_blind_string)
        self.send_to_players(big_blind_string)

        self.deal_cards(button)

        offset = 2
        current_player_list = self.player_list

        for i in range(NUM_BETTING_ROUNDS):
            print(ROUND_DICT[i])
            self.send_to_players(ROUND_DICT[i] + "\n")

            if i > 0:
                self.deck.pop()
                if i == 1:
                    self.board = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
                else:
                    self.board.append(self.deck.pop())
                self.send_to_players(str(self.board) + "\n")

            new_player_list, new_pot = self.betting_round(button, current_player_list, bet_dict, offset)

            if new_player_list == None and new_pot == None:
                self.player_to_funds[sb] += small_blind
                self.player_to_funds[bb] += big_blind
                return False

            pot += new_pot
            if len(new_player_list) == 1:
                winner = new_player_list[0]
                self.player_to_funds[winner] += pot
                winner_string = "WINNER: %s/n" % (winner)
                print(winner_string)
                self.send_to_players(winner_string + "\n")
                return True

            if i == 0:
                current_player_list = []
                new_player_set = set(new_player_list)
                for j in range(num_players):
                    check_player = player_list[j]
                    if check_player in new_player_set:
                        current_player_list.append(check_player)
            else:
                current_player_list = new_player_list
            bet_dict = {player : 0 for player in current_player_list}
            offset = 0

        hands_dict = self.calculate_final_hands(current_player_list)
        best_hand_tup = max(hands_dict)
        best_hand = Hands.from_tuple(best_hand_tup)

        num_winners = len(hands_dict[best_hand_tup])
        portion = pot / num_winners
        for winner in hands_dict[best_hand_tup]:
            winner_string = "WINNER: %s with %s" % (winner, str(best_hand))
            print(winner_string)
            self.send_to_players(winner_string + "\n")

            self.player_to_funds[winner] += portion
            pot -= portion

        if pot > 0:
            recipient = raw_input("Give remaining %d to: " % (pot)).upper()
            while recipient not in self.player_to_funds:
                print("Please enter a player's name")
                recipient = raw_input("Give remaining %d to: " % (pot)).upper()
            self.player_to_funds[recipient] += pot

        return True

    def start_game(self):
        playing = True
        button = 0

        while playing:
            Cards.shuffle(self.deck)
            playing = self.play_hand(button)
            print(self.player_to_funds)
            button += 1

        self.print_players()

    def serve(self):
        players_needed = set(self.player_to_funds.keys())
        
        game_server = socket.socket()
        game_server.bind((self.host, self.port))
        game_server.listen(1)

        print("Waiting for players to join...")

        while len(players_needed) > 0:
            client, addr = game_server.accept()
            ip, port = addr

            player_name = self.check_player_name(client, players_needed)
            if player_name != None:
                print("%s CONNECTED AT %s:%d" % (player_name, ip, port))

                self.player_to_client[player_name] = client
                players_needed.remove(player_name)

        self.start_game()

if __name__ == "__main__":
    port = int(sys.argv[1])
    host = socket.gethostbyname(socket.gethostname())
    print("Welcome to Texas Holdem!\nWe will be playing on %s:%d\n" %(host, port))
    player_list, player_dict = init_players()
    small_blind, big_blind = init_blinds()
    server = Game_Server(host, port, player_list, player_dict, small_blind, big_blind)
    server.serve()