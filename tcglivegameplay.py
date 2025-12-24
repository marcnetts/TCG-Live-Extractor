import json
import os
import csv

directory = 'localization-cache'
localization = {}
for filename in os.scandir(directory):
    if filename.is_dir:
        for langfile in os.scandir(directory+'\\'+filename.name):
            if langfile.is_file():
                print('Loaded ' + langfile.path)
                with open(langfile.path, 'r') as f:
                    localization = {**localization, **json.load(f)}

# print(localization)
# print(localization['sm3_league_s2'])

GAMEPLAY_ITEMS = ['db_', 'cs_', 'cn_']
GAMEPLAY_DEFAULT_ITEM = 'tcgl-default'

with open('config-cache.json', 'r') as f:
    config_cache_data = json.load(f)['documents']


with open('cachedata.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t')
    
    items = json.loads(config_cache_data['item-set-database_0.0']['keys']['itemsets']['contentString'])
    for item in items:
        cost = items[item]['costs']
        for itemSet in items[item]['itemSet']:
            if itemSet['clientId'].lower().startswith(tuple(GAMEPLAY_ITEMS)):
                csvwriter.writerow([item, (localization[item] if item in localization else ''), itemSet['clientId'], (localization[itemSet['clientId']] if itemSet['clientId'] in localization else '')])
                # print(item + '\t' + (localization[item] if item in localization else '') + '\t' + itemSet['clientId'] + '\t' + (localization[itemSet['clientId']] if itemSet['clientId'] in localization else ''))

    deck_manifest = json.loads(config_cache_data['deck-definition-manifest_0.0']['keys']['decks']['contentString'])['definitions']
    print(deck_manifest)
    for deck in deck_manifest:
        items = json.loads(config_cache_data[deck]['keys']['decks']['contentString'])
        for item in items:
            item['deckBoxId'] = item['deckBoxId'].lower()
            item['sleeveId'] = item['sleeveId'].lower()
            item['coinId'] = item['coinId'].lower()
            if item['deckBoxId'].startswith(tuple(GAMEPLAY_ITEMS)) and item['deckBoxId'].find(GAMEPLAY_DEFAULT_ITEM) == -1:
                csvwriter.writerow([item['id'], (localization[item['id']] if item['id'] in localization else ''), item['deckBoxId'], (localization[item['deckBoxId']] if item['deckBoxId'] in localization else '')])
            if item['sleeveId'].startswith(tuple(GAMEPLAY_ITEMS)) and item['sleeveId'].find(GAMEPLAY_DEFAULT_ITEM) == -1:
                csvwriter.writerow([item['id'], (localization[item['id']] if item['id'] in localization else ''), item['sleeveId'], (localization[item['sleeveId']] if item['sleeveId'] in localization else '')])
            if item['coinId'].startswith(tuple(GAMEPLAY_ITEMS)) and item['coinId'].find(GAMEPLAY_DEFAULT_ITEM) == -1:
                csvwriter.writerow([item['id'], (localization[item['id']] if item['id'] in localization else ''), item['coinId'], (localization[item['coinId']] if item['coinId'] in localization else '')])
    
    items = json.loads(config_cache_data['item-set-database-deck-customization_0.0']['keys']['itemsets']['contentString'])
    for item in items:
        cost = items[item]['costs']['soft']
        if cost > 0:
            csvwriter.writerow([item, (localization[item] if item in localization else ''), '', 'Store item'])
            # print(item + '\t' + (localization[item] if item in localization else '') + '\t' + itemSet['clientId'] + '\t' + (localization[itemSet['clientId']] if itemSet['clientId'] in localization else ''))
