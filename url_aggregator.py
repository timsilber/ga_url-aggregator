import csv
import pandas as pd

path_to_import ='/Users/timsilber/repos/ga_url-aggregator/2022AUG_sessions.csv'

import_file =  pd.read_csv(path_to_import, index_col=0, header=7, squeeze=True).to_dict()

print(import_file)

columns = ['Page, Sessions']


# pd.read_csv(path_to_import,usecols=columns).to_csv('selected.csv', index=False)