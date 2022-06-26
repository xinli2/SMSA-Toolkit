import pandas as pd
import json
from numpy import NAN

file_name = './data_new/tweets-all.csv'

df = pd.read_csv(file_name)
df = df['entities']

tag_dict = {}


for i in range(len(df)):
    tag = df.iloc[i]
    if(type(tag)==str):
        # print(f'{type(df.iloc[i])} --> {df.iloc[i]}')
        tag = tag.replace("\'", "\"")

        tag = json.loads(tag)
        if('hashtags' in tag):
            tag = tag['hashtags'][0]
            tag = tag['tag']
            

            # print(f'{tag}\n')
            if tag in tag_dict:
                tag_dict[tag] +=1
            else:
                tag_dict[tag] = 1
print(tag_dict)



