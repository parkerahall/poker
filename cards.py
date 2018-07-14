SUITS = set(["HEARTS", "DIAMONDS", "SPADES", "CLUBS"])

class Cards:	
	def __init__(self, value, suit):
		assert (suit in SUITS)
		if type(value) == int:
			assert (value > 1 and value < 15)
		elif type(value) == str:
			assert (value.upper() in set(['J', 'Q', 'K', 'A']))
		else:
			assert (False)
		
		self.suit = suit
		self.value = Cards.convert_to_str(value)

	@staticmethod
	def convert_to_str(value):
		face_card_lookup = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
		assert (value > 1)
		return face_card_lookup.get(value, str(value))

	# [card_list] must be sorted in descending order
	@staticmethod
	def highest_value_without(card_list, without):
		for card in card_list:
			card_value = card.value
			if card_value not in without:
				return card_value

	@staticmethod
	def sort(card_list):
		return sorted(card_list, key=lambda x: x.get_int_value(), reverse=True)

	@staticmethod
	def suit_sort(card_list):
		output = {}
		for suit in SUITS:
			output[suit] = filter(lambda x: x.suit == suit, card_list)
		return output

	@staticmethod
	def value_sort(card_list):
		output = {}
		for card in card_list:
			card_value = card.value
			old_count = output.get(card_value, 0)
			output[card_value] = old_count + 1
		return output

	@staticmethod
	def make_deck():
		deck = []
		for suit in SUITS:
			for value in range(2, 15):
				deck.append(Cards(suit, value))
		return deck

	def get_int_value(self):
		face_card_lookup = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
		if self.value in face_card_lookup:
			return face_card_lookup[self.value]
		else:
			return int(self.value)

	def __repr__(self):
		return str(self)

	def __str__(self):
		return self.value + " of " + self.suit