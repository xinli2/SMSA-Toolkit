import pandas as pd
import json
from numpy import NAN

file_name = './merged_data/tweets-all.csv'

df = pd.read_csv(file_name)
df1 = df['entities']
df2 = df['text']

tag_dict = {}
tag_list = []
for i in range(len(df1)):
    tag = df1.iloc[i]
    if(type(tag)==str):
        line = str(df2.iloc[i])
        line = line.split( )
        for word in line:
            if word[0]=='@' or word[0] =='#':
                tag_list.append(word)
       
        #print(f'{type(df1.iloc[i])} --> {df1.iloc[i]}')

        tag = tag.replace("\'", "\"")

        tag = json.loads(tag)
        if('hashtags' in tag):
            tag = tag['hashtags'][0]
            tag = tag['tag']
            tag_list.append(tag)
            tag_set = set(tag_list)

            # print(f'{tag}\n')
            for k in tag_set:
                if k in tag_dict:
                    tag_dict[k] +=1
                else:
                    tag_dict[k] = 1
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