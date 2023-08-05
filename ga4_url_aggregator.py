import argparse
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import csv

load_dotenv() #make sure you have python-dotenv installed, your .env is in the root directory and has PROJECT_API_KEY defined
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

def sum_nested_dicts(data):
    total = 0
    for key, value in data.items():
        if isinstance(value, dict):
            total += sum_nested_dicts(value)
        elif isinstance(value, int):
            total += value
    return total

def flatten_dict(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sum_nested_dicts(value)
        elif isinstance(value, int):
            result[key] = value
    return result

def flatten_and_sort_dict(data):
    # Flatten the dictionary
    flattened_data = flatten_dict(data)
    
    # Sort the dictionary by value in descending order
    sorted_data = dict(sorted(flattened_data.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_data

def write_dict_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Integration', 'Sessions', 'Percentage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        total_sessions = sum(data.values())
        for key, value in data.items():
            percentage = (value / total_sessions) * 100
            writer.writerow({'Integration': key, 'Sessions': value, 'Percentage': percentage})

        # Write total sessions as a separate row
        writer.writerow({'Integration': 'Total', 'Sessions': total_sessions, 'Percentage': 100.0})

def aggregate_sessions(input_file):
    # Load the CSV file, skipping the initial metadata lines
    data = pd.read_csv(input_file, skiprows=10)

    # Extract the article slug from the URL
    data['article_slug'] = data['Page path and screen class'].apply(lambda x: x.split('/')[-1])

    # Remove the root directory
    data = data[data['article_slug'] != '']

    # Group by the 'article_slug' and aggregate the 'Sessions'
    # Convert the resulting series to a dictionary
    aggregated_sessions = data.groupby('article_slug')['Sessions'].sum().to_dict()

    # Sort the dictionary by values in descending order and create a new dictionary
    sorted_sessions = {k: v for k, v in sorted(aggregated_sessions.items(), key=lambda item: item[1], reverse=True)}

    return sorted_sessions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Path to the input CSV file')
    args = parser.parse_args()

    aggregated_session_dict = aggregate_sessions(args.input)

    # Export the DataFrame to a CSV file
    df_sorted_sessions = pd.DataFrame(list(aggregated_session_dict.items()), columns=['article_slug', 'Sessions'])
    df_sorted_sessions.to_csv('export/aggregated_sessions.csv', index=False)

    data = call_API()
    integrations_dict = flatten_and_sort_dict(parse_IA(data, aggregated_session_dict))
    write_dict_to_csv(integrations_dict, 'export/aggregated_integration_sessions.csv')


