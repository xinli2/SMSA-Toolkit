import pandas as pd
import numpy as np
import os
from textblob import TextBlob


from vaderSentiment.vaderSentiment import  SentimentIntensityAnalyzer


# reedit data
d1 = pd.read_csv('./data/roblox.csv')
d2 = pd.read_csv('./data/roblox-comments.csv')

# stackoverflow
d3 = pd.read_csv('./data/questions.csv')
d4 = pd.read_csv('./data/answers.csv')

a=os.listdir('./tweeter_data')
file_name=a[0]
file_location='./tweeter_data'+'/'+file_name
data=pd.read_csv(file_location)
print(data.columns)

def sentiment_scores(sentence):
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer
    # object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(sentence)

    print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", sentiment_dict['neg'] * 100, "% Negative")
    print("sentence was rated as ", sentiment_dict['neu'] * 100, "% Neutral")
    print("sentence was rated as ", sentiment_dict['pos'] * 100, "% Positive")

    print("Sentence Overall Rated As", end=" ")

    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05:
        print("Positive")

    elif sentiment_dict['compound'] <= - 0.05:
        print("Negative")

    else:
        print("Neutral")

str1='good boy'
str2='silly bitch'
sentiment_scores(str1)
sentiment_scores(str2)


text=str1+str2
blob = TextBlob(text)

for sentence in blob.sentences:
    print(sentence.sentiment.polarity)

sid_obj = SentimentIntensityAnalyzer()
data_all_vader=pd.DataFrame()
k=0
for file_name in os.listdir('./tweeter_data'):
    try:
        file_location='./tweeter_data'+'/'+file_name
        data=pd.read_csv(file_location)
        data=data['text']
        data.index=range(len(data))
        total_sentiment=0
        total_sentiment_textblob=0
        for j in range(len(data)):
            sentence=data[j]
            sentiment_dict = sid_obj.polarity_scores(sentence)
            total_sentiment=total_sentiment+sentiment_dict['compound']

        if total_sentiment>0:
            data_all_vader.loc[k,'sentiment']='positive'
        elif total_sentiment<0:
            data_all_vader.loc[k,'sentiment']='negative'
        else:
            data_all_vader.loc[k,'sentiment']='neutral'

        k=k+1
        print(str(k)+ ' is ok')
    except Exception as e:
        pass


