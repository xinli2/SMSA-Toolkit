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



'''
{
    'urls': [{
        'start': 47, 
        'end': 70, 
        'url': 'https://t.co/IFDpnq1cwh', 
        'expanded_url': 'https://youtube.com/channel/UCklyxTTBB0WuTmHRcWbw9IQ/live', 
        'display_url': 'youtube.com/channel/UCklyx‚Ä¶', 
        'status': 200, 
        'title': 'üî¥ JOGANDO COM OS INSCRITOS | ROBLOX AO VIVO | ROBUX - YouTube', 
        'description': 'üî∏Para ver a descri√ß√£o, clique em: MOSTRAR MAIS.Participe do sorteio de robux, lendo a descri√ß√£o para saber mais. E ganhar robux gr√°tis em nossa liveVisite o...', 
        'unwound_url': 'https://www.youtube.com/channel/UCklyxTTBB0WuTmHRcWbw9IQ/live'}], 
    'mentions': [{
        'start': 79, 
        'end': 86, 
        'username': 'Roblox', 
        'id': '16745055'
        }], 
    'hashtags': [{
        'start': 87, 
        'end': 94, 
        'tag': 'Roblox'
        }]
    }
'''