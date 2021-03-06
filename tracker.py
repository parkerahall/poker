# TRACKS REAL-LIFE POKER GAME BEING PLAYED

NUM_BETTING_ROUNDS = 4
ACTIONS = set(["check", "raise", "call", "fold", "chop"])

ROUND_DICT = {0: "PRE-FLOP", 1: "POST-FLOP", 2: "POST-TURN", 3: "POST-RIVER"}

def start_game():
	player_list, player_dict = init_players()
	small_blind, big_blind = init_blinds()
	
	playing = True
	button = 0

	while playing:
		playing = play_hand(player_list, player_dict, button, small_blind, big_blind)
		print(player_dict)
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
					buy_in = int(raw_input("Buy-in amount: "))
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

def play_hand(player_list, player_dict, button, small_blind, big_blind):
	pot = 0
	num_players = len(player_list)
	bet_dict = {player : 0 for player in player_list}

	sb = player_list[button % num_players]
	player_dict[sb] -= small_blind
	pot += small_blind
	bet_dict[sb] = small_blind

	bb = player_list[(button + 1) % num_players]
	player_dict[bb] -= big_blind
	pot += big_blind
	bet_dict[bb] = big_blind

	offset = 2
	current_player_list = player_list

	for i in range(NUM_BETTING_ROUNDS):
		print(ROUND_DICT[i])
		new_player_list, new_pot = betting_round(current_player_list, player_dict, button, bet_dict, offset)
		pot += new_pot

		if new_player_list == None and new_pot == None:
			player_dict[sb] += small_blind
			player_dict[bb] += big_blind
			return False
		elif len(new_player_list) == 1:
			winner = new_player_list[0]
			player_dict[winner] += pot
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

	winner = raw_input("Winner: ").lower()
	while (winner != "split" and winner not in player_dict):
		print("Please enter a player's name or 'split'")
		winner = raw_input("Winner: ").lower()

	if winner == "split":
		num_winners = len(current_player_list)
		portion = pot / num_winners
		for w in current_player_list:
			player_dict[w] += portion
		leftover = pot - num_winners * portion
		if leftover != 0:
			recipient = raw_input("Give remaining to: ").lower()
			while recipient not in player_dict:
				print("Please enter a player's name")
				recipient = raw_input("Give remaining to: ").lower()
			player_dict[recipient] += leftover
	else:
		player_dict[winner] += pot
	
	return True

def betting_round(player_list, player_dict, button, bet_dict, offset):
	start_index = button + offset
	num_players = len(player_list)
	max_bet = max([bet_dict[key] for key in bet_dict])

	new_pot = 0
	can_check = True

	have_played = 0
	num_folded = 0

	while True:
		for i in range(len(player_list)):
			current_player = player_list[(start_index + i) % num_players]
			if bet_dict[current_player] != "FOLD":
				if num_players - num_folded == 1:
					return [current_player], new_pot

				print_bets(bet_dict)
				action, bad_action = player_action(current_player, player_dict, bet_dict, can_check, max_bet)

				if action == None:
					return action, action

				while bad_action:
					print("Please enter 'check', 'call', 'fold' or 'raise NUM'")
					action, bad_action = player_action(current_player, player_dict, bet_dict, can_check, max_bet)

				add_to_pot, add_to_max = handle_action(current_player, action, player_dict, bet_dict, max_bet)
				new_pot += add_to_pot
				max_bet += add_to_max

				keyword = action[0].lower()
				if keyword == "fold":
					bet_dict[current_player] = "FOLD"
					num_folded += 1
				elif keyword == "raise":
					can_check = False
				elif keyword == "chop":
					current_bet = bet_dict[current_player]
					
					player_dict[current_player] += current_bet
					new_pot -= current_bet
					bet_dict[current_player] = "FOLD"
					winner = [player for player in bet_dict if bet_dict[player] != "FOLD"]
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


def player_action(current_player, player_dict, bet_dict, can_check, max_bet):
	action = raw_input("Action " + current_player.upper() + ": ").split(' ')
	keyword = action[0].lower()
	if keyword == "":
		return None, None
	bad_keyword = keyword not in ACTIONS
	bad_check = ((keyword == "check") and (not can_check))
	if keyword == "raise":
		not_allowed = check_raise(current_player, player_dict, bet_dict, max_bet, action)
	elif keyword == "call":
		not_allowed = check_call(current_player, player_dict, bet_dict, max_bet)
	elif keyword == "chop":
		not_allowed = check_chop(current_player, bet_dict)
	else:
		not_allowed = False
	bad_action = bad_keyword or bad_check or not_allowed
	return action, bad_action

def check_raise(current_player, player_dict, bet_dict, max_bet, action):
	try:
		extra = int(action[1])
	except:
		print("Please enter an integer NUM for 'raise NUM'")
		return True
	if extra < 0:
		print("Please enter a positive integer NUM for 'raise NUM'")
		return True
	needed = max_bet + extra - bet_dict[current_player]
	bad_raise = player_dict[current_player] < needed
	if bad_raise:
		print("Not enough funds")
	return bad_raise

def check_call(current_player, player_dict, bet_dict, max_bet):
	bad_call = player_dict[current_player] < (max_bet - bet_dict[current_player])
	if bad_call:
		print("Not enough funds")
	return bad_call

def check_chop(current_player, bet_dict):
	players_remaining = sum([bet_dict[player] != "FOLD" for player in bet_dict])
	bad_chop = players_remaining != 2
	if bad_chop:
		print("Can only chop with two players remaining")
	return bad_chop

def handle_action(current_player, action, player_dict, bet_dict, max_bet):
	keyword = action[0].lower()
	if keyword == "raise":
		max_diff = int(action[1])
		old_bet = bet_dict[current_player]
		pot_diff = max_bet + max_diff - old_bet
		player_dict[current_player] -= pot_diff
		bet_dict[current_player] += pot_diff
		
		return pot_diff, max_diff
	
	elif keyword == 'call':
		old_bet = bet_dict[current_player]
		pot_diff = max_bet - old_bet
		player_dict[current_player] -= pot_diff
		bet_dict[current_player] += pot_diff

		return pot_diff, 0

	else:
		return 0, 0

def print_players(player_dict):
	for name in player_dict:
		print(name + "\t" + str(player_dict[name]))

def print_bets(bet_dict):
	for name in bet_dict:
		print(name + "\t" + str(bet_dict[name]))

if __name__ == "__main__":
	start_game()