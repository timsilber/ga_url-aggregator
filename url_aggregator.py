import csv
import pandas as pd
from pathlib import Path

path_to_import =input("\n Drop Google Analytics Report CSV here: ")
metric = input("\n What metric do you want to sort by? ")

metric = metric[0].upper() + metric[1:]
print(metric)

col_names = ['Page', metric]
csv_dict =  pd.read_csv(path_to_import[1:-1], header= 5, usecols=col_names).to_dict(orient='split')
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
output_file = str(Path.home() / "Desktop") + "/aggregated_" + metric.lower() + "_per_page.csv"

with open(output_file, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=csv_columns)
    writer.writeheader()
    for key in sorted_keys:
        output_file.write("%s,%s\n"%(key,aggregate_dict[key]))

print("\nDone. Check your Desktop.\n")