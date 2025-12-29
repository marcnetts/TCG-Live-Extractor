import json
import os
from datetime import datetime, timedelta
import glob
from pathlib import Path
import re

LOCALIZATION_DIRECTORY = 'localization-cache'
CONFIG_CACHE_FOLDER = 'config-cache'
CARD_DATA_FOLDER = 'config-cache-json'
LADDER_FILES_GLOB = 'season_[0-9]*.json'
LOCALIZATION_LANG = 'en'
CARD_DATABASE_FILES_FORMATTER = 'card-database-{}_0_{}_0.0_contents.json'
ITEMSET_DB_FILE = 'config-cache/item-set-database_0.0.json'

LADDER_OUTPUT_FILE = "ladder_seasons.txt"

AVATAR_ITEMS_LAZY_COMPARISON = {
    'sh': 'Shoe',
    'lo': 'Lower',
    'up': 'Upper',
    'ha': 'Hat'
}

def sanitize_set_name_from_item(booster_name: str):
    return re.sub(r'^.*?<i>(.+?—)?(.+?)<\/i> (.+?)$', r'\2', booster_name)

def sanitize_item_type_from_item(booster_name: str):
    return re.sub(r'^.*?<i>(.+?—)?(.+?)<\/i> (.+?)$', r'\3', booster_name).replace('Collector\'s', 'Collector')

def get_localization():
    print('Fetching localization...')
    localization = {}
    for filename in os.scandir(LOCALIZATION_DIRECTORY):
        if filename.is_dir:
            for langfile in os.scandir(LOCALIZATION_DIRECTORY+'\\'+filename.name):
                if langfile.is_file():
                    print('Loaded ' + langfile.path)
                    with open(langfile.path, 'r', encoding="utf8") as f:
                        localization = {**localization, **json.load(f)}
    return localization

def get_card_data_from_folder(card_id: str, localization):
    card_set = re.sub(r'_.+?$', '', card_id)
    file_path = Path(CARD_DATA_FOLDER, CARD_DATABASE_FILES_FORMATTER.format(card_set, LOCALIZATION_LANG))
    if file_path.is_file():
        with file_path.open("r", encoding="utf-8") as f:
            contents = json.load(f)
            return {
                "name": contents[card_id]["EN Card Name"],
                "type": contents[card_id]["EN Format"],
                "pokemonType": contents[card_id]["EN Type"],
                "number": contents[card_id]["CompSea Card Number"],
                "setCount": contents[card_id]["EN Expansion Denominator"],
                "setName": sanitize_set_name_from_item(localization['booster-'+card_set.replace('a', '')])
            }
    else:
        return card_id

def get_itemset_data():
    print('Fetching itemset data...')
    with Path(ITEMSET_DB_FILE).open("r", encoding="utf-8") as f:
        return json.loads(json.load(f)['keys']['itemsets']['contentString'])

def get_ladder_data():
    print('Fetching ladder data...')
    ladder_data_list = []
    for ladder_file in glob.glob(f"{CONFIG_CACHE_FOLDER}\\{LADDER_FILES_GLOB}"):
        if Path(ladder_file).is_file():
            print('Getting ' + ladder_file)
            with Path(ladder_file).open("r", encoding="utf-8") as f:
                ladder_data = json.load(f)['keys']  
                ladder_data_list.append(json.loads(ladder_data[next(iter(ladder_data))]['contentString']))

    deduplicated_list = {d['seasonID']: d for d in ladder_data_list}.values()
    return list(deduplicated_list)

def convert_card_data_into_mediawiki_link(card_data):
    if type(card_data) == 'str': return card_data
    else:
        return f"[[{card_data['name']} ({card_data['setName']} {card_data['number'].lstrip('0')})]]"

# expects an itemSet item from cache_config
def convert_itemset(item, localization):
    match item['itemType']:
        case 0:
            return f"{item['amount']}× Coins"
        case 1:
            return f"{item['amount']}× Crystals"
        case 2:
            card_info = get_card_data_from_folder(item['clientId'], localization)
            return f"{item['amount']}× {convert_card_data_into_mediawiki_link(card_info)}"
        case 3:
            return f"{item['amount']}× {{{{TCG|{sanitize_set_name_from_item(localization[item['clientId']])}}}}} {sanitize_item_type_from_item(localization[item['clientId']])}"
        case 4:
            return f"{localization[item['clientId']]} (Deck)"
        case 5:
            return f"{localization[item['clientId']]} (Coin)"
        case 7:
            return f"{item['amount']}× Credits"
        case 9:
            return f"{localization[item['clientId']]} (Card Sleeve)"
        case 10:
            return f"{localization[item['clientId']]} (Deck box)"
        case 11:
            return f"{localization[item['clientId']].strip()} (Avatar {AVATAR_ITEMS_LAZY_COMPARISON[item['clientId'][:2]]})"
        case 12:
            return f"{localization[item['clientId']]} (Battle Deck)"
        case _:
            return f"{item['amount']} × {localization[item['clientId']] or item['clientId']}"

def itemset_to_mediawiki (itemset, localization):
    sanitized_items = []
    unique_avatar_items = {}
    if itemset:
        for item in itemset:
            converted_itemset = convert_itemset(item, localization).strip()
            if item['itemType'] == 11:
                if converted_itemset not in sanitized_items:
                    sanitized_items.append(converted_itemset)
                    unique_avatar_items[converted_itemset] = item['clientId']
                else:
                    del unique_avatar_items[converted_itemset]
            else:
                sanitized_items.append(converted_itemset)
        
        for key, value in unique_avatar_items.items():
            avatar_item_index = sanitized_items.index(key)
            sanitized_items[avatar_item_index] += '{{tt|*|Male}}' if '_m_' in value else '{{tt|*|Female}}'

        return "<br>".join(sanitized_items)
    else: return ''

def convert_ladder_data_to_mediawiki_row(row, itemset_data, localization, tiers_to_fetch: list[str], next_start_date: str):
    TABLE_ROW_TEMPLATE = """|- style="background: #FFF;"
|rowspan="2"| {0}
|rowspan="2"| {1}
| {2}
| {4}
| {6}
| {8}
| {10}
| {12}
|- style="background: #FFF;"
| (Ladder End)<br>{3}
| (Ladder End)<br>{5}
| (Ladder End)<br>{7}
| (Ladder End)<br>{9}
| (Ladder End)<br>{11}
| (Ladder End)<br>{13}

"""
    # print(tiers_to_fetch)
    # print(itemset_data)
    season_items = row['seasonEndRewardsContent' if 'seasonEndRewardsContent' in row else 'seasonRewardsConfigContent']['seasonRewards']
    first_league_items = itemset_data[season_items[tiers_to_fetch[0]][0]['prizeID']]['itemSet']
    second_league_items = itemset_data[season_items[tiers_to_fetch[1]][0]['prizeID']]['itemSet']
    third_league_items = itemset_data[season_items[tiers_to_fetch[2]][0]['prizeID']]['itemSet']
    fourth_league_items = itemset_data[season_items[tiers_to_fetch[3]][0]['prizeID']]['itemSet']
    fifth_league_items = itemset_data[season_items[tiers_to_fetch[4]][0]['prizeID']]['itemSet']
    sixth_league_items = itemset_data[season_items[tiers_to_fetch[5]][0]['prizeID']]['itemSet']
    first_league_end_items = itemset_data[season_items[tiers_to_fetch[0]][1]['prizeID']]['itemSet']
    second_league_end_items = itemset_data[season_items[tiers_to_fetch[1]][1]['prizeID']]['itemSet']
    third_league_end_items = itemset_data[season_items[tiers_to_fetch[2]][1]['prizeID']]['itemSet']
    fourth_league_end_items = itemset_data[season_items[tiers_to_fetch[3]][1]['prizeID']]['itemSet']
    fifth_league_end_items = itemset_data[season_items[tiers_to_fetch[4]][1]['prizeID']]['itemSet']
    sixth_league_end_items = itemset_data[season_items[tiers_to_fetch[5]][1]['prizeID']]['itemSet']

    return (TABLE_ROW_TEMPLATE.format(
        datetime.fromisoformat(next_start_date or row['seasonTitleDate'].replace('z', '')).strftime("%B %d, %Y"),
        datetime.fromisoformat(row['endDate'].replace('z', '')).strftime("%B %d, %Y"),
        itemset_to_mediawiki(first_league_items, localization),
        itemset_to_mediawiki(first_league_end_items, localization),
        itemset_to_mediawiki(second_league_items, localization),
        itemset_to_mediawiki(second_league_end_items, localization),
        itemset_to_mediawiki(third_league_items, localization),
        itemset_to_mediawiki(third_league_end_items, localization),
        itemset_to_mediawiki(fourth_league_items, localization),
        itemset_to_mediawiki(fourth_league_end_items, localization),
        itemset_to_mediawiki(fifth_league_items, localization),
        itemset_to_mediawiki(fifth_league_end_items, localization),
        itemset_to_mediawiki(sixth_league_items, localization),
        itemset_to_mediawiki(sixth_league_end_items, localization),
    ).replace('<i>', '').replace('</i>', ''))

def write_ladder_data_to_mediawiki_format(ladder_data_list, itemset_data, localization, skip_unused_seasons = True):
    TABLE_HEADER_WITH_ARCEUS_LEAGUE = """{| class="roundy" style="background: #{{bulba color}}; padding: 2px; text-align: center;"
|-
! Begin Date
! Finish Date
! Quick League
! Poké League
! Great League
! Ultra League
! Master League
! Arceus League

"""

    TABLE_HEADER_WITH_NEST_LEAGUE = """{| class="roundy" style="background: #{{bulba color}}; padding: 2px; text-align: center;"
|-
! Begin Date
! Finish Date
! Nest League
! Quick League
! Poké League
! Great League
! Ultra League
! Master League
"""

    TABLE_FOOTER = "|}"

    seasons_with_arceus_league = []
    seasons_with_nest_league = []
    for row in ladder_data_list:
        season_items = row['seasonEndRewardsContent' if 'seasonEndRewardsContent' in row else 'seasonRewardsConfigContent']['seasonRewards']
        try:
            _ = season_items['arceus_league'][0]
            seasons_with_arceus_league.append(row)
        except (KeyError, TypeError):
            seasons_with_nest_league.append(row)

    tiers_with_arceus_league = ['quick_league', 'poke_league', 'great_league', 'ultra_league', 'master_league', 'arceus_league']
    tiers_with_nest_league = ['nest_league', 'quick_league', 'poke_league', 'great_league', 'ultra_league', 'master_league']
    next_start_date = ''

    with open(LADDER_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('==List of Rewards==\n\n===Before March 2025===\n\n')
        f.write(TABLE_HEADER_WITH_ARCEUS_LEAGUE)

        for row in seasons_with_arceus_league:
            if not skip_unused_seasons or row['endDate'] > '2022-02-23':
                f.write(convert_ladder_data_to_mediawiki_row(row, itemset_data, localization, tiers_with_arceus_league, next_start_date))
                next_start_date = str(datetime.fromisoformat(row['endDate'].replace('z', '')) + timedelta(days=1))
        
        f.write(TABLE_FOOTER)

    with open(LADDER_OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write('\n\n===After March 2025===\n\n')
        f.write(TABLE_HEADER_WITH_NEST_LEAGUE)

        for row in seasons_with_nest_league:
            f.write(convert_ladder_data_to_mediawiki_row(row, itemset_data, localization, tiers_with_nest_league, next_start_date))
            next_start_date = str(datetime.fromisoformat(row['endDate'].replace('z', '')) + timedelta(days=1))
        
        f.write(TABLE_FOOTER)


if __name__ == "__main__":
    ladder_data = get_ladder_data()
    itemset_data = get_itemset_data()
    localization = get_localization()
    write_ladder_data_to_mediawiki_format(ladder_data, itemset_data, localization, skip_unused_seasons = True)