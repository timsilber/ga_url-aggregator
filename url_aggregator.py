import csv
import pandas as pd
from pathlib import Path
import time 
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def csv_to_dataframe(csv_path, columns):
    #choose column from Analytics CSV based on user input and turn into dictionary
    csv_dict =  pd.read_csv(csv_path, header= 5, usecols=columns).to_dict(orient='split')
    csv_data = csv_dict['data']
    
    return csv_data

def dataframe_to_dict(dataframe):

    aggregate_dict = {}

    for item in dataframe: 
        page = item[0]
        
        #remove commas from numbers to turn into integers to perform operations in next try/except
        try: 
            sessions = int(item[1].replace(',', ''))
        except:
            continue
        
        #split URL by /, take the last item which should be slug that matches
        try:
            slug = page.split('/')[-1]
            if slug not in aggregate_dict:
                aggregate_dict[slug] = sessions
            else: 
                aggregate_dict[slug] = aggregate_dict[slug] + sessions #if matching slug, add metric to existing data
        except:
            continue
    
    return aggregate_dict

def get_sort_keys(dict):
    sorted_keys = sorted(dict, key=dict.get, reverse=True)
    return sorted_keys

def dict_to_sorted_csv(dict, columns):
    #sort dictionary by pageviews
    sorted_keys = sorted(dict, key=dict.get, reverse=True)
    #write data to CSV output on Desktop
    output_file = str(Path.home() / "Downloads") + "/" + time.strftime('%Y-%m-%d') + "_" + columns[0].lower()+"_aggregated_" + columns[1].lower() + "_per_page.csv"
    with open(output_file, 'w') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=columns)
        writer.writeheader()
        for key in sorted_keys:
            output_file.write("%s,%s\n"%(key, dict[key]))

    print(f"\nExported {columns[0]} x {columns[1]} data to a CSV in your Downloads folder.")

def call_API():
    CATEGORY_KEY = 'b801d463-4046-4873-8d80-d61e5577954c'
    url = "https://apihub.document360.io/v2/categories/" + CATEGORY_KEY

    payload={}
    headers = {'api_token': os.getenv('PROJECT_API_KEY')}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    response_json = response.json()
    integrations_IA = response_json["data"]["child_categories"]

    return integrations_IA

def parse_IA(parent_categories, dict, flattened = {}):

    for category in parent_categories:

        if category["hidden"]:
            continue

        flattened[category["name"]] = {} # creates a dict entry for each parent category
        parent_dict = flattened[category["name"]]
        # print(parent_dict)

        child_categories = category["child_categories"]

        for article in category["articles"]:
            if article["slug"] not in dict:
                continue

            article_value = dict[article["slug"]]
            parent_dict[article["title"]] = article_value
            # print(category["name"], article["slug"], dict[article["slug"]])

        if child_categories:
            parse_IA(child_categories, dict,  parent_dict)
            # print("\n", "\n", category["name"], "\n", "\n")

    return flattened
    
def sum_dict_recursive(data):
        sum = 0
        for key, value in data.items():
            if isinstance(value, dict):
                sum += sum_dict_recursive(value)
            else:
                sum += value
        return sum

def sum_nested_dict(nested_dict):

    output_dict = {}

    for item in nested_dict:
        for sub_item in nested_dict[item]:
            if not isinstance(nested_dict[item][sub_item], dict):
                output_dict[sub_item] = nested_dict[item][sub_item]
            else: 
                output_dict[sub_item] = sum_dict_recursive(nested_dict[item][sub_item])
    
    return output_dict

def print_top_fives(csv_dict, integrations_dict):

    sort_keys = get_sort_keys(csv_dict)
    sort_keys.remove('')
    sort_keys.remove('about-g2-integrations')

    unwanted_articles = ['', 'about-g2-integrations']

    top_five_articles = {k: csv_dict[k] for k in list(sort_keys)[:5] if k not in unwanted_articles}
    print("\n\nTop five articles:\n")
    for item in top_five_articles:
        print(item, top_five_articles[item])
    print("\n")
    
    sort_keys = get_sort_keys(integrations_dict)
    top_five_integrations = {k: integrations_dict[k] for k in list(sort_keys)[:5]}
    print("Top five integrations: ")
    for item in top_five_integrations:
            print(item, top_five_integrations[item])
    print("\n")

if __name__ == "__main__":
    #get file path
    path_to_import =input("\nDrop Google Analytics Report CSV here: \n\n    ")
    path_to_import = path_to_import.replace('\'', '').replace('"','') #handle terminal wrapping file paths in strings

    #get metric to sort pages
    metric = input("\nWhat metric do you want to sort by? \n\n    ")
    metric = metric[0].upper() + metric[1:].lower() # handle case-sensitive user input
    col_names = ['Page', metric]

    #sort aggregated article data and export to CSV
    df = csv_to_dataframe(path_to_import, col_names)
    csv_dict = dataframe_to_dict(df)
    dict_to_sorted_csv(csv_dict, col_names)

    #use doc360 API to map article data to integration categories
    data = call_API()
    integrations_dict = sum_nested_dict(parse_IA(data, csv_dict))

    #sort integration data and export to CSV
    dict_to_sorted_csv(integrations_dict, ['Integration', 'Sessions'])

    #print top 5 articles and integrations
    print_top_fives(csv_dict, integrations_dict)

