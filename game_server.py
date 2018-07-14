import sys, socket
from cards import Cards
from hands import Hands

MSG_SIZE = 512
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


class Game_Server:
    def __init__(self, host, port, p_list, p_dict):
        self.host = host
        self.port = port
        self.player_list = p_list
        self.player_to_funds = p_dict
        self.player_to_client = {}

    @staticmethod
    def check_player_name(client, players_needed):
        attempts = 3
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
        return None


    def serve(self):
        players_needed = set(self.player_to_funds.keys())
        
        game_server = socket.socket()
        game_server.bind((self.host, self.port))
        game_server.listen(1)

        print("Waiting for players to join...")

        try:
            while len(players_needed) > 0:
                client, addr = game_server.accept()
                ip, port = addr

                player_name = Game_Server.check_player_name(client, players_needed)
                if player_name != None:
                    print("%s CONNECTED AT %s:%d" % (player_name, ip, port))

                    players_needed.remove(player_name)

        finally:
            game_server.close()
            print("\nGOODBYE\n")

if __name__ == "__main__":
    port = int(sys.argv[1])
    host = socket.gethostbyname(socket.gethostname())
    print("Welcome to Texas Holdem!\nWe will be playing on %s:%d\n" %(host, port))
    player_list, player_dict = init_players()
    server = Game_Server(host, port, player_list, player_dict)
    server.serve()