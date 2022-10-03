import csv
import pandas as pd
from pathlib import Path
import time 

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

def sort_dict_by_value(dict):
    #sort dictionary by pageviews
    sorted_keys = sorted(dict, key=dict.get, reverse=True)
    for key in sorted_keys:
        print(key, dict[key])
    return sorted_keys

def sorted_dict_to_csv(sorted_keys, dict, columns):
    #write data to CSV output on Desktop
    output_file = str(Path.home() / "Downloads") + "/" + time.strftime('%Y-%m-%d') + "_aggregated_" + columns[1].lower() + "_per_page.csv"
    with open(output_file, 'w') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=columns)
        writer.writeheader()
        for key in sorted_keys:
            output_file.write("%s,%s\n"%(key, dict[key]))

    print("\nDone. Check your Downloads folder.\n")
    
if __name__ == "__main__":
    #get file path
    path_to_import =input("\n Drop Google Analytics Report CSV here: ")
    path_to_import = path_to_import.replace('\'', '').replace('"','') #handle terminal wrapping file paths in strings

    #get metric to sort pages
    metric = input("\n What metric do you want to sort by? ")
    metric = metric[0].upper() + metric[1:].lower() # handle case-sensitive user input
    col_names = ['Page', metric]

    df = csv_to_dataframe(path_to_import, col_names)
    csv_dict = dataframe_to_dict(df)
    sorted_dict = sort_dict_by_value(csv_dict)

    sorted_dict_to_csv(sorted_dict, csv_dict, col_names)
    
