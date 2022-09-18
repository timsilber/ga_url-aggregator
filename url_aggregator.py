import csv
import pandas as pd

path_to_import ='/Users/timsilber/repos/ga_url-aggregator/2022AUG_sessions.csv'

col_names = ['Page', 'Sessions']
csv_dict =  pd.read_csv(path_to_import, header= 5, usecols=col_names).to_dict(orient='split')
csv_data = csv_dict['data']

aggregate_dict = {}

for item in csv_data:
    page = item[0]
    try: 
        sessions = int(item[1].replace(',', ''))
    except:
        continue
    
    try:
        slug = page.split('/')[-1]
        if slug not in aggregate_dict:
            aggregate_dict[slug] = sessions
        else: 
            aggregate_dict[slug] = aggregate_dict[slug] + sessions
    except:
        continue 

sorted_keys = sorted(aggregate_dict, key=aggregate_dict.get, reverse=True)

csv_columns = ['Page','Sessions']
output_file = "aggregated_sessions_per_page.csv"

with open(output_file, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=csv_columns)
    writer.writeheader()
    for key in sorted_keys:
        output_file.write("%s,%s\n"%(key,aggregate_dict[key]))



# for key, value in csv_dict.items():
#      print(key, ' : ', value)