import sqlite3
import json
from json import JSONEncoder

dblocation = 'C:\\Users\\Erzz\\AppData\\LocalLow\\Cygames\\umamusume\\master\\master.mdb'

class Card():
    card_id = 0
    limit_break = -1
    # Speed, Stamina, Power, Guts, Int, Skill Points, Energy
    event_gain = [0,0,0,0,0,0,0]
    # Speed, Stamina, Power, Guts, Int
    starting_stats = []
    race_bonus = 0
    starting_bond = 0
    # Speed, Stamina, Power, Guts, Int, Skill Points
    stat_bonus = []
    specialty_rate = 0
    training_bonus = 0
    friendship_bonus = 0
    motivation_bonus = 0
    unique_friendship_bonus = 0
    wisdom_recovery = 0
    effect_size_up = 0
    energy_up = 0
    energy_discount = 0
    fail_rate_down = 0
    card_type = 0

def GetValue(data, lb, rarity):
    base_value = -1
    base_lb = lb
    index = lb + rarity + 5
    while index >= 2:
        base_value = int(data[index])
        if base_value == -1:
            index -= 1
            base_lb -= 1
        else:
            break

    if base_lb == lb:
        return base_value
    
    if base_value == -1:
        return 0

    max_value = -1
    max_lb = lb
    index = lb + rarity + 5
    while index <= 12:
        max_value = int(data[index])
        if max_value == -1:
            index += 1
            max_lb += 1
        else:
            break
    
    if max_value == -1:
        return base_value

    if base_lb == max_lb:
        return base_value
        
    return int(base_value + (max_value - base_value) * ((lb - base_lb) / (max_lb - base_lb)))

def AddEffectToCard(card, effect_type, effect_value):
    if effect_type == 1: 
        card.friendship_bonus += effect_value / 100
    elif effect_type == 2:
        card.motivation_bonus += effect_value / 100
    elif effect_type == 3:
        card.stat_bonus[0] += effect_value
    elif effect_type == 4:
        card.stat_bonus[1] += effect_value
    elif effect_type == 5:
        card.stat_bonus[2] += effect_value
    elif effect_type == 6:
        card.stat_bonus[3] += effect_value
    elif effect_type == 7:
        card.stat_bonus[4] += effect_value
    elif effect_type == 8:
        card.training_bonus += effect_value  / 100
    elif effect_type == 9:
        card.starting_stats[0] += effect_value
    elif effect_type == 10:
        card.starting_stats[1] += effect_value
    elif effect_type == 11:
        card.starting_stats[2] += effect_value
    elif effect_type == 12:
        card.starting_stats[3] += effect_value
    elif effect_type == 13:
        card.starting_stats[4] += effect_value
    elif effect_type == 14:
        card.starting_bond += effect_value
    elif effect_type == 15:
        card.race_bonus += effect_value
    elif effect_type == 19:
        card.specialty_rate += effect_value
    elif effect_type == 25:
        card.energy_up += effect_value / 100
    elif effect_type == 26:
        card.effect_size_up += effect_value / 100
    elif effect_type == 27:
        card.fail_rate_down += effect_value / 100
    elif effect_type == 28:
        card.energy_discount += effect_value / 100
    elif effect_type == 30:
        card.stat_bonus[5] += 1
    elif effect_type == 31:
        card.wisdom_recovery += effect_value

cards = []

with sqlite3.connect(dblocation) as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM support_card_data')
    card_data = cursor.fetchall()

    for data in card_data:
        # 0 id | 1 chara_id | 2 rarity | 3 exchange_item_id | 4 effect_table_id | 5 unique_effect_id | 6 command_type
        # 7 command_id | 8 support_card_type | 9 skill_set_id | other stuff
        cursor.execute('SELECT * FROM support_card_effect_table WHERE id=%s' % data[0])
        effects = cursor.fetchall()

        for i in range(5):
            current_card = Card()
            current_card.id = data[0]
            current_card.type = int(data[7])
            current_card.limit_break = i
            current_card.starting_stats = [0,0,0,0,0]
            current_card.stat_bonus = [0,0,0,0,0,0]
            current_card.event_gain = [0,0,0,0,0,0,0]
            current_card.race_bonus = 0
            current_card.starting_bond = 0
            current_card.specialty_rate = 0
            current_card.training_bonus = 1
            current_card.friendship_bonus = 1
            current_card.motivation_bonus = 1
            current_card.unique_friendship_bonus = 1
            current_card.wisdom_recovery = 0
            current_card.effect_size_up = 1
            current_card.energy_up = 1
            current_card.energy_discount = 0
            current_card.fail_rate_down = 0

            for effect in effects:
                # 0 id | 1 type | 2 init | 3 limit_lv_5 | ... | 12 limit_lv_50
                effect_type = int(effect[1])
                AddEffectToCard(current_card, effect_type, GetValue(effect, i, int(data[2])))

            cursor.execute('SELECT * FROM support_card_unique_effect WHERE id = %s' % data[0])
            # 0 id | 1 lv | 2 type_0 | 3 value_0 | 4 type_1 | 5 value_1
            unique = cursor.fetchone()
            if unique is not None:
                for u in range(0,3,2):
                    type_0 = int(unique[2 + u])
                    if type_0 == 1:
                        current_card.unique_friendship_bonus += int(unique[3 + u]) / 100
                    else:
                        AddEffectToCard(current_card, type_0, int(unique[3 + u]))
            cards.append(current_card)

card_strings = []
for card in cards:
    card_strings.append(json.dumps(card.__dict__))

json_string = 'const cards = [%s];\n\nexport default cards;' % ",".join(card_strings)

with open("./cards.js", "w", encoding="utf-8") as f:
    f.write(json_string)