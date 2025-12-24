import json
import os
import csv
from datetime import datetime

directory = 'localization-cache'
localization = {}
non_shop_items = set()
AVATAR_ITEMS = ['glasses_', 'upper_m', 'upper_f', 'lower_m', 'lower_f', 'hat_m', 'hat_f', 'shoe_m', 'shoe_f']

for subfolder in os.scandir(directory):
    if subfolder.is_dir:
        for filename in os.scandir(directory+"\\"+subfolder.name):
            if filename.is_file():
                print('Loading ' + filename.path + '...')
                with open(filename.path, 'r', encoding='utf8') as f:
                    data = json.load(f)
                    transformed_data = {
                        key: {"name": value, "date": subfolder.name} for key, value in data.items() if key not in localization
                    }
                    localization = {**localization, **transformed_data}
print(localization)

directory = 'config-cache'
with open('cachedavatars.csv', 'w', newline='') as outputfile:
    csvwriter = csv.writer(outputfile, delimiter='\t')

    for filename in os.scandir(directory):
        if filename.is_dir:
            if filename.is_file() and filename.path != directory + '\\' + 'item-set-database-avatar_0.0.json':
                print(f'Looking at {filename.path}...')
                with open(filename.path, 'r', encoding='utf8') as f:
                    jsonfile = json.load(f)
                    # print(jsonfile['keys'])
                    if jsonfile['keys'] and jsonfile['keys'].get('itemsets'):
                        item_set_database = json.loads(jsonfile['keys']['itemsets']['contentString'])
                        for key in item_set_database:
                            itemSetName = str(key)
                            date = item_set_database[key]['date']['from']
                            cost = item_set_database[key]['costs']['soft']
                            for item in item_set_database[key]['itemSet']:
                                clientId = item['clientId'] if 'clientId' in item else ''
                                if item['clientId'].lower().startswith(tuple(AVATAR_ITEMS)):
                                    print(clientId)
                                    non_shop_items.add(clientId)
                                    # csvwriter.writerow([clientId, (localization[clientId]['name'] if clientId in localization else ''), itemSetName, ('Shop Item' if cost else (localization[itemSetName]['name'] if itemSetName in localization else '')), date[:10]])


with open('cachedavatars3.csv', 'w', newline='') as outputfile:
    csvwriter = csv.writer(outputfile, delimiter='\t')

    filename_path = 'config-cache\item-set-database-avatar_0.0.json'
    print(f'Looking at {filename_path}...')
    with open(filename_path, 'r', encoding='utf8') as f:
        jsonfile = json.load(f)
        # print(jsonfile['keys'])
        if jsonfile['keys'] and jsonfile['keys'].get('itemsets'):
            avatar_compendium = json.loads(jsonfile['keys']['itemsets']['contentString'])
            for key in avatar_compendium:
                itemSetName = str(key)
                date = avatar_compendium[key]['date']['from']
                cost = avatar_compendium[key]['costs']['soft']
                for item in avatar_compendium[key]['itemSet']:
                    clientId = item['clientId'] if 'clientId' in item else ''
                    if clientId.startswith(tuple(AVATAR_ITEMS)) and not clientId in non_shop_items:
                        # csvwriter.writerow([clientId, (localization[clientId]['name'] if clientId in localization else ''), itemSetName, ('Shop Item' if cost else (localization[itemSetName]['name'] if itemSetName in localization else '')), date[:10]])
                        csvwriter.writerow([clientId, (localization[clientId]['name'] if clientId in localization else ''), itemSetName, ('Shop Item' if cost else (localization[itemSetName]['name'] if itemSetName in localization else '')), datetime.strptime(localization[clientId]['date'], "%Y%m%d_%H%M").strftime("%Y-%m-%d")])