import sys
import random
from cards import Cards
from hands import Hands

def make_cards():
	cards = []
	for value in range(13):
		for suit in range(4):
			cards.append((value, suit))
	return cards

def convert_to_real_cards(card):
	suit_dict = {0 : "HEARTS", 1 : "DIAMONDS", 2 : "SPADES", 3 : "CLUBS"}
	value, suit = card

	return Cards(value + 2, suit_dict[suit])

def run_flush_test(cards):
	test_cards = cards[:]
	random.shuffle(test_cards)

	dealer_hand = []
	current_value, goal_suit = test_cards.pop()
	player_hand = [current_value, 1]

	while True:
		current_card = test_cards.pop()
		current_value, current_suit = current_card
		if current_suit == goal_suit:
			player_hand[1] += 1
			if current_value > player_hand[0]:
				player_hand[0] = current_value
			if player_hand[1] == 5:
				break
		else:
			dealer_hand.append(current_card)

	for _ in range(8 - len(dealer_hand)):
		dealer_hand.append(test_cards.pop())

	real_dealer_cards = [convert_to_real_cards(card) for card in dealer_hand]
	real_dealer_hand = Hands.get_highest_hand(real_dealer_cards)
	return Hands("FLUSH", (player_hand[0],)).get_tup_value() > real_dealer_hand.get_tup_value()


def run_royal_flush_test(cards):
	test_cards = cards[:]
	random.shuffle(test_cards)

	dealer_hand = {}
	num_dealer_cards = 0
	current_value, goal_suit = test_cards.pop()
	while current_value > 4:
		current_value, goal_suit = test_cards.pop()
	player_hand = 1

	for suit in range(4):
		if suit != goal_suit:
			dealer_hand[suit] = 0

	while True:
		current_value, current_suit = test_cards.pop()
		if current_value < 5:
			if current_suit == goal_suit:
				player_hand += 1
				if player_hand == 5:
					break
			else:
				num_dealer_cards += 1
				dealer_hand[current_suit] += 1
				if dealer_hand[current_suit] == 5:
					return False
		else:
			num_dealer_cards += 1

	for _ in range(8 - num_dealer_cards):
		current_value, current_suit = test_cards.pop()
		if current_value < 5:
			dealer_hand[current_suit] += 1
			if dealer_hand[current_suit] == 5:
				return False

	return True

STRATEGY_SUITE = {"royal-flush": run_royal_flush_test, "flush": run_flush_test}

def run_tests(test, power):
	cards = make_cards()
	
	total_tests = 0.
	wins = 0
	next_power = 1
	for i in range(10 ** power):
		total_tests += 1
		if test(cards):
			wins += 1
		if total_tests == (10 ** next_power):
			print("WIN-RATE ESTIMATE AFTER " + str(10 ** next_power) + ": " + str(wins / total_tests))
			next_power += 1

if __name__ == "__main__":
	strategy = sys.argv[1].lower()
	power = int(sys.argv[2])
	try:
		test = STRATEGY_SUITE[strategy]
		run_tests(test, power)
	except KeyError:
		print("Testing not supported for this strategy")
