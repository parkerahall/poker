# TRACKS REAL-LIFE POKER GAME BEING PLAYED

# TODO: immediate win case after folding all around
# TODO: immediately end betting round after everyone calls

NUM_BETTING_ROUNDS = 3
ACTIONS = set(["check", "raise", "call", "fold"])

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

	pot = small_blind + big_blind
	offset = 2
	current_player_list = player_list

	for _ in range(NUM_BETTING_ROUNDS):
		new_player_set, new_pot = betting_round(current_player_list, player_dict, button, bet_dict, offset)
		pot += new_pot

		if new_player_set == None and new_pot == None:
			return False
		elif len(new_player_set) == 1:
			winner = new_player_set.pop()
			player_dict[winner] += pot
			return True

		current_player_list = []
		for i in range(num_players):
			check_player = player_list[(i + button) % num_players]
			if check_player in new_player_set:
				current_player_list.append(check_player)
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
	current_player_list = player_list
	max_bet = max([bet_dict[key] for key in bet_dict])

	new_pot = 0
	can_check = True

	while True:
		num_players = len(current_player_list)
		new_player_list = []
		for i in range(len(current_player_list)):
			current_player = current_player_list[(start_index + i) % num_players]
			print_bets(bet_dict)
			action, bad_action = player_action(current_player, can_check)

			while bad_action:
				print("Please enter 'check', 'call', 'fold' or 'raise NUM'")
				action, bad_action = player_action(current_player, can_check)

			add_to_pot, add_to_max = handle_action(current_player, action, player_dict, bet_dict, max_bet)
			new_pot += add_to_pot
			max_bet += add_to_max

			keyword = action[0].lower()
			if keyword != "fold":
				new_player_list.append(current_player)
			if keyword == "raise":
				can_check = False

		done = True
		in_for = bet_dict[new_player_list[0]]
		for player in new_player_list:
			if bet_dict[player] != in_for:
				done = False
				break
		
		if done:
			return set(new_player_list), new_pot
		current_player_list = new_player_list
		start_index = 0


def player_action(current_player, can_check):
	action = raw_input("Action " + current_player.upper() + ": ").split(' ')
	keyword = action[0].lower()
	bad_keyword = keyword not in ACTIONS
	bad_check = ((keyword == "check") and (not can_check))
	bad_action = bad_keyword or bad_check
	return action, bad_action

def handle_action(current_player, action, player_dict, bet_dict, max_bet):
	keyword = action[0].lower()
	if keyword == "raise":
		bad_num = True
		while bad_num:
			try:
				max_diff = int(action[1])
				bad_num = False
			except:
				action[1] = raw_input("Please enter a positive integer: ")
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