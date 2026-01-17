
CARD_SCORES= {
    'Black 3': 5,
    '4': 5,
    '5': 5,
    '6': 5,
    '7': 5,
    '8': 10,
    '9': 10,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'A': 20,
    '2': 20,
    'JOKER': 50
}

def meld_score(base_card, base_count, twos, jokers):
    
    base = (CARD_SCORES[base_card] * base_count) + (CARD_SCORES['2'] * twos) + (CARD_SCORES['JOKER'] * jokers)
    
    if twos == 0 and jokers == 0 and base_count >= 7:
        bonus = 500
        
    elif twos + jokers + base_count >= 7:
        bonus = 300
        
    else:
        bonus = 0
        
    return base + bonus

def red_threes(count):

    if count < 4:
        return count*100
    
    else:
        return count*200


    