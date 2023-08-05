import csv
import pandas as pd
from pathlib import Path
import time 
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv() #make sure you have python-dotenv installed, your .env is in the root directory and has PROJECT_API_KEY defined

def csv_to_dataframe(csv_path, columns):
    #choose column from Analytics CSV based on user input and turn into dictionary
    csv_dict =  pd.read_csv(csv_path, header= 9, usecols=columns).to_dict(orient='split')
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

    # for line in aggregate_dict:
    #     print(line, aggregate_dict[line])
    
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
    url = "https://apihub.document360.io/v2/Categories/" + CATEGORY_KEY

    payload={}
    headers = {'api_token': os.getenv('PROJECT_API_KEY')}
    
    max_retries = 10
    retry_delay = 6

    for i in range(max_retries):
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            response_json = response.json()
            integrations_IA = response_json["data"]
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 429:
                print(f'Server is overloaded. Waiting for {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                print(error.response)
                print(f'Other API error. Waiting for {retry_delay} seconds...')
                time.sleep(retry_delay)

    return integrations_IA


def parse_IA(data, dict, flattened = {}):

    child_articles = data["articles"]

    for article in child_articles:
        if article["hidden"]:
            continue
        if article["slug"] not in dict:
            continue
        else:
            article_title = article["title"]
            article_value = dict[article["slug"]]
            flattened[article_title] = article_value
            # print(article_title, article_value)

    if "child_categories" in data:

        for category in data["child_categories"]:
            if category["hidden"]:
                continue
            parent_category = category["name"]
            flattened[parent_category] = {}
            parent_dict = flattened[parent_category]
            parse_IA(category, dict, parent_dict)

    return flattened
    
def sum_dict_recursive(data):
        sum = 0
        for _, value in data.items():
            if isinstance(value, dict):
                sum += sum_dict_recursive(value)
            else:
                sum += value
        return sum

def sum_nested_dict(nested_dict):

    output_dict = {}

    for item in nested_dict:
        if not isinstance(nested_dict[item], dict):
            output_dict[item] = nested_dict[item]
        else: 
            output_dict[item] = sum_dict_recursive(nested_dict[item])
    
    return output_dict

def print_top_fives(csv_dict, integrations_dict):

    sort_keys = get_sort_keys(csv_dict)
    sort_keys.remove('')
    # try:
    #     sort_keys.remove('about-g2-integrations')
    # except:
    #     return

    unwanted_articles = ['', 'about-g2-integrations']

    top_five_articles = {k: csv_dict[k] for k in list(sort_keys)[:5] if k not in unwanted_articles}
    print("\n\nTop five articles:\n")
    for item in top_five_articles:
        print(item, top_five_articles[item])
    print("\n")
    
    sort_keys = get_sort_keys(integrations_dict)
    top_five_integrations = {k: integrations_dict[k] for k in list(sort_keys)[:5]}
    print("Top five integrations:\n")
    for item in top_five_integrations:
            print(item, top_five_integrations[item])
    print("\n")

if __name__ == "__main__":
    #get Analytics CSV file path
    path_to_import =input("\nDrop Google Analytics Report CSV here: \n\n    ")
    path_to_import = path_to_import.replace('\'', '').replace('"','') #handle terminal wrapping file paths in strings
    # path_to_import = 'test/today_demo.csv'

    #get metric to sort articles
    metric = input("\nWhat metric do you want to sort by? \n\n    ")
    metric = metric[0].upper() + metric[1:].lower() # handle case-sensitive user input
    col_names = ['Page path and screen class', metric]
    # col_names = ['Page', 'Sessions']

    #sort aggregated article data and export to CSV
    df = csv_to_dataframe(path_to_import, col_names)
    csv_dict = dataframe_to_dict(df)
    dict_to_sorted_csv(csv_dict, col_names)

    #use doc360 API to map article data to integration categories
    data = call_API()
    integrations_dict = sum_nested_dict(parse_IA(data, csv_dict))

    # sort integration data and export to CSV
    dict_to_sorted_csv(integrations_dict, ['Integration', 'Sessions'])

    # print top 5 articles and integrations
    print_top_fives(csv_dict, integrations_dict)

