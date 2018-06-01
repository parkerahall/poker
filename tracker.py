# TRACKS REAL-LIFE POKER GAME BEING PLAYED

def start_game():
    player_list, player_dict = init_players()
    small_blind, big_blind = init_blinds()
    
    playing = True
    button = 0

    while playing:
        playing = play_hand(player_list, player_dict, button, small_blind, big_blind)
        button += 1

    print_players(player_dict)

def init_players():
    player_list = []
    player_dict = {}

    print("Please input players starting from the left of the dealer and rotating clockwise")

    next_player = raw_input("Input player name: ").lower()
    while next_player != "":
        if next_player in player_dict:
            print("Player already entered")
        else:
            bad_amount = True
            while bad_amount:
                try:
                    buy_in = float(raw_input("Buy-in amount: "))
                    bad_amount = False
                except:
                    print("Please enter a positive number")
            player_list.append(next_player)
            player_dict[next_player] = buy_in
        next_player = raw_input("Input player name: ").lower()

    return player_list, player_dict

def init_blinds():
    bad_small = True
    while bad_small:
        try:
            small_blind = float(raw_input("Small blind amount: "))
            bad_small = False
        except:
            print("Please enter a positive number")

    bad_big = True
    while bad_big:
        try:
            big_blind = float(raw_input("Big blind amount: "))
            if big_blind <= small_blind:
                print("Please enter a number greater than the small blind")
            else:
                bad_big = False
        except:
            print("Please enter a positive number")

    return small_blind, big_blind

def play_hand(player_list, player_dict, button, small_blind, big_blind):
    bet_dict = {player : 0 for player in player_list}

    sb = player_list[button]
    player_dict[sb] -= small_blind
    pot += small_blind
    bet_dict[sb] = small_blind

    bb = player_list[button + 1]
    player_dict[bb] -= big_blind
    pot += big_blind
    bet_dict[bb] = big_blind

    pot = small_blind + big_blind

    playing, add_pot = betting_round(player_list, player_dict, button, bets=bet_dict, off=2)
    if playing:
        pot = 
        playing = betting_round(player_list, player_dict, button)
        if playing:
            playing = betting_round(player_list, player_dict, button)


def print_players(player_dict):
    for name in player_dict:
        print(name + "\t" + str(player_dict[name]))

if __name__ == "__main__":
    start_game()