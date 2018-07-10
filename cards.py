SUITS = set(["HEARTS", "DIAMONDS", "SPADES", "CLUBS"])

class Cards:	
	def __init__(self, suit, value):
		assert (suit in SUITS)
		if type(value) == int:
			assert (value > 1 and value < 15)
		elif type(value) == str:
			assert (value.lower() in set(['J', 'Q', 'K', 'A']))
		else:
			assert (False)
		
		self.suit = suit
		self.value = Cards.convert_to_str(value)

	@staticmethod
	def convert_to_str(value):
		face_card_lookup = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
		assert (value > 1)
		return face_card_lookup.get(value, str(value))

	@staticmethod
	def sort(card_list):
		face_card_lookup = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
		def get_value(card):
			return face_card_lookup.get(card.value, int(value))
		return sorted(card_list, key=lambda x: get_value(x), rev=True)

	@staticmethod
	def suit_sort(card_list):
		output = {}
		for suit in SUITS:
			output[suit] = filter(lambda x: x.suit == suit, card_list)
		return output

	@staticmethod
	def make_deck():
		deck = []
		for suit in SUITS:
			for value in range(2, 15):
				deck.append(Cards(suit, value))
		return deck

	def __repr__(self):
		return str(self)

	def __str__(self):
		return self.value + " of " + self.suit

HANDS = {"ROYAL FLUSH": 9,
		"STRAIGHT FLUSH": 8,
		"FOUR OF A KIND": 7,
		"FULL HOUSE": 6,
		"FLUSH": 5,
		"STRAIGHT": 4,
		"THREE OF A KIND": 3,
		"TWO PAIR": 2,
		"PAIR": 1,
		"HIGH CARD": 0}

class Hands:
	def __init__(self, hand, high):
		assert (hand in HANDS)
		self.hand = hand
		self.high = high

	@staticmethod


	def __repr__(self):
		return str(self)

	def __str__(self):
		hand_string = self.hand
		high_string = ",".join([str(elt) for elt in self.high])
		suffix = "HIGH"
		return " ".join([hand_string, high_string, suffix])