from cards import Cards

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

NUM_AVAIL_CARDS = 7

class Hands:
    def __init__(self, hand, high):
        assert (hand in HANDS)
        self.hand = hand
        self.high = high

    @staticmethod
    def sort(hand_list):
        return sorted(hand_list, key=lambda x: x.get_tup_value(), reverse=True)

    # [card_list] must be sorted in descending order
    @staticmethod
    def check_straight(card_list):
        first_card = card_list[0]
        highest_value = first_card.get_int_value()
        last_value = highest_value
        straight_length = 1
        for card in card_list:
            card_value = card.get_int_value()
            if card_value == last_value - 1:
                last_value = card_value
                straight_length += 1
                if straight_length == 5:
                    return highest_value
            elif card_value < last_value:
                highest_value = card_value
                last_value = card_value
                straight_length = 1
        return None

    @staticmethod
    def get_highest_hand(card_list):
        assert(len(card_list) == NUM_AVAIL_CARDS)
        
        sorted_list = Cards.sort(card_list)
        
        # check for hands including flushes
        suit_dict = Cards.suit_sort(sorted_list)
        for suit in suit_dict:
            suited_set = suit_dict[suit]
            if len(suited_set) >= 5:
                high_straight = Hands.check_straight(suited_set)
                if high_hand == 14:
                    return Hands("ROYAL FLUSH", ())
                elif high_hand != None:
                    return Hands("STRAIGHT FLUSH", (high_hand,))
                else:
                    highest_value = suited_set[0].get_int_value()
                    return Hands("FLUSH", (highest_value,))

        # check for normal straight
        high_straight = Hands.check_straight(sorted_list)
        if high_straight != None:
            return Hands("STRAIGHT", (high_straight,))

        # check for sets
        value_dict = Cards.value_sort(sorted_list)
        reverse_dict = {}
        for value in value_dict:
            count = value_dict[value]
            old_value = reverse_dict.get(count, [])
            old_value.append(value)
            reverse_dict[count] = old_value
        
        biggest_set = max(reverse_dict)
        if biggest_set == 4:
            set_value = reverse_dict[biggest_set]
            kicker = Cards.highest_value_without(sorted_list, set(set_value))
            return Hands("FOUR OF A KIND", (set_value[0], kicker))
        elif biggest_set == 3:
            if len(reverse_dict[biggest_set]) == 2:
                set_value = max(reverse_dict[biggest_set])
                kicker = min(reverse_dict[biggest_set])
                return Hands("FULL HOUSE", (set_value, kicker))
            else:
                set_value = reverse[biggest_set]
                if 2 in reverse_dict:
                    pair_value = max(reverse_dict[2])
                    return Hands("FULL HOUSE", (set_value[0], pair_value))
                else:
                    kicker = Cards.highest_value_without(sorted_list, set(set_value))
                    return Hands("THREE OF A KIND", (set_value[0], kicker))
        elif biggest_set == 2:
            if len(reverse_dict[biggest_set]) > 1:
                high_pair = max(reverse_dict[biggest_set])
                reverse_dict[biggest_set].remove(high_pair)
                low_pair = max(reverse_dict[biggest_set])
                kicker = Cards.highest_value_without(sorted_list, set([high_pair, low_pair]))
                return Hands("TWO PAIR", (high_pair, low_pair, kicker))
            else:
                high_pair = reverse_dict[biggest_set]
                kicker = Cards.highest_value_without(sorted_list, set(high_pair))
                return Hands("PAIR", (high_pair, kicker))
        else:
            high_card = max(value_dict)
            return Hands("HIGH CARD", (high_card,))

    def get_tup_value(self):
        face_card_lookup = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        high_tup = tuple([face_card_lookup.get(elt, elt) for elt in self.high])
        hand_tup = (HANDS[self.hand],)
        return hand_tup + high_tup

    def __repr__(self):
        return str(self)

    def __str__(self):
        hand_string = self.hand
        high_string = ",".join([str(elt) for elt in self.high])
        suffix = "HIGH"
        return " ".join([hand_string, high_string, suffix])

# card_list = [Cards(8, "SPADES"), Cards("A", "HEARTS"), Cards(8, "DIAMONDS"),
# Cards("A", "CLUBS"), Cards(7, "DIAMONDS"), Cards(5, "DIAMONDS"), Cards(2, "DIAMONDS")]
# print Hands.get_highest_hand(card_list)