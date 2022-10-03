import csv
import pandas as pd
from pathlib import Path
import time 

#get file path
path_to_import =input("\n Drop Google Analytics Report CSV here: ")
path_to_import = path_to_import.replace('\'', '').replace('"','') #handle terminal wrapping file paths in strings

#get metric to sort pages
metric = input("\n What metric do you want to sort by? ")
metric = metric[0].upper() + metric[1:] # handle case-sensitive user input

#choose column from Analytics CSV based on user input and turn into dictionary
col_names = ['Page', metric]
csv_dict =  pd.read_csv(path_to_import, header= 5, usecols=col_names).to_dict(orient='split')
csv_data = csv_dict['data']

aggregate_dict = {}

for item in csv_data: 
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

#sort dictionary by pageviews
sorted_keys = sorted(aggregate_dict, key=aggregate_dict.get, reverse=True)

#write data to CSV output on Desktop
csv_columns = ['Page', metric]
output_file = str(Path.home() / "Downloads") + "/" + time.strftime('%Y-%m-%d') + "_aggregated_" + metric.lower() + "_per_page.csv"
with open(output_file, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=csv_columns)
    writer.writeheader()
    for key in sorted_keys:
        output_file.write("%s,%s\n"%(key,aggregate_dict[key]))

print("\nDone. Check your Downloads folder.\n")