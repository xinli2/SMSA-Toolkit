#!/usr/bin/env python
# coding: utf-8

# In[280]:


import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import time
import re
import nltk
from wordcloud import WordCloud,STOPWORDS
from nltk.sentiment import SentimentIntensityAnalyzer
keyword_game=['Minecraft','Cubic Castles','Minetest','KoGaMa','Fortnite','8BitMMO','Growtopia']
keyword_adj=['Safe','Security','Script','Model','Data stores','Plugin']


# In[162]:


def traverse(directory,keyword=None):
    lst=[]
    for root,dirs,files in os.walk(directory):
        for file in files:
            if isinstance(keyword,str):
                if keyword in file:
                    lst.append(os.path.join(root,file))
            else:
                lst.append(os.path.join(root,file))
    return lst


# In[202]:


def txt_preprocess(directory,keyword):
    ## preprocessing scalping data
    paths=traverse(directory,keyword=keyword)
    ## combining thematic data from all sources
    texts=np.array([])
    for path in paths:
        try:
            temp=pd.read_csv(path,dtype=object).values.flatten()
            texts=np.append(texts,temp)
        except:
            pass

    ## getting rid of abnormal characters
    Bool=np.repeat(True,len(texts))
    for i in range(len(texts)):
        e=texts[i]
        if not isinstance(e,str):
            Bool[i]=False
        if str(e).isnumeric():
            Bool[i]=False
        if '[]' in str(e):
            Bool[i]=False
        if 'http' in str(e):
            Bool[i]=False
        if 'EDT' in str(e):
            Bool[i]=False

    return texts[Bool]    


# In[345]:


def sia_method(str_seq):
    ## calculate sentiment scores on each msg from str_seq
    sia = SentimentIntensityAnalyzer()
    lst_neg=[];lst_neu=[];lst_pos=[];lst_compound=[];lst_msg=[]
    for msg in str_seq:
        scores=sia.polarity_scores(msg)
        if (scores['neu']<1)&(scores['pos']<1)&(scores['neg']<1):
            ## excluding possible meaningless sequence
            lst_neg.append(scores['neg'])
            lst_neu.append(scores['neu'])
            lst_pos.append(scores['pos'])
            lst_compound.append(scores['compound'])
            lst_msg.append(msg)

    return pd.DataFrame([lst_msg,lst_neg,lst_neu,lst_pos,lst_compound],
                        index=['msg','neg','neu','pos','compound']).T


# In[279]:


## filtering data to only have words
game=keyword_game[-1]
temp=txt_preprocess(os.getcwd(),game)
temp=' '.join(temp).split(' ')
words_onlyletters = [w for w in temp if w.isalpha()]
## additional filters
stopwords = set(STOPWORDS)
stopwords.update(["br", "href","en","EDT","https","game"])
## crossing out presupplied keywords
stopwords.update(keyword_adj,'data','stores')
## crossing out game names
stopwords.update(keyword_game)
words_onlyletters = [w for w in words_onlyletters if w.lower() not in stopwords]
texts=' '.join(words_onlyletters)
## creating wordclouds from cleansed data
#wordcloud = WordCloud(stopwords=stopwords).generate(texts)
#plt.imshow(wordcloud,interpolation='bilinear')
#plt.axis("off")
#plt.savefig('wordcloud_'+str(game)+'.png')


lst_word=[];lst_num=[]
for word, freq in nltk.Text(words_onlyletters).vocab().items():
    lst_word.append(word);lst_num.append(freq)
df_sort=pd.DataFrame([lst_word,lst_num],index=['w','n']).T.sort_values('n',ascending=False)

labels = df_sort.w.values[:7] 
sizes = df_sort.n.values[:7] 
explode = (0.18,0,0,0,0,0,0) 
patches,text1,text2 = plt.pie(sizes,
                      explode=explode,
                      labels=labels,
                      autopct = '%3.0f%%',
                      shadow = False, 
                      startangle =90, 
                      pctdistance = 0.6) 

plt.axis('off')
plt.savefig('pie_'+str(game)+'.png')


# In[352]:


game=keyword_game[i]
temp=txt_preprocess(os.getcwd(),game)
## use VADER analyzer to generate sentiment scores
df=sia_method(temp).drop_duplicates()
## use scores to rank useful comments 
df.sort_values('neu',ascending=False).head(10).to_csv('neutop10_'+str(game)+'.csv',index=False)
df.sort_values('compound',ascending=False).head(10).to_csv('compoundtop10_'+str(game)+'.csv',index=False)

