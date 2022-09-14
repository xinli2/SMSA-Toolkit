#!/usr/bin/env python
# coding: utf-8

# #### See the link for details on v2 Tweet object
# https://blog.twitter.com/developer/en_us/topics/tips/2020/understanding-the-new-tweet-payload
# 
# - Specify "Entity for URLS and mentions
# - "data" in the response contains tweet details
# - "include" in the response contains 
#  - user details
#  - location info
#  - whether the tweet was quoted
# - "public_metrics" nested in tweet object contains retweets, likes, etc.
# - "public_metrics" nested in user object contains followers, followes, etc.
# - "non_public_metrics" nested in tweet object contains impressions, video view, etc.
# - "context_annotations" in nested in tweet provides contextual information to help you understand what the Tweet is about without needing to do custom entity recognition.
#  - Each object within context_annotations contains a ‘domain’ object and an ‘entity’ object, and each of those have an id and name property. The domain indicates the high level category or topic under which the Tweet falls, and the entity indicates the person, place, or organization that is recognized from the Tweet text. More details on available annotations can be found on our [documentation page](https://developer.twitter.com/en/docs/labs).
#  
# See here for details of tweet object: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet

# In[6]:


import tweepy
from twitter_authentication import bearer_token
import pandas as pd
import datetime
import time, os, sys, traceback
import csv
client = tweepy.Client(bearer_token, wait_on_rate_limit=True)

user_fields = ['username', 'public_metrics', 'description', 'location', 
                'protected', 'verified', 'entities', 'url']
tweet_fields = ['id', 'text', 'author_id', 'created_at', 'geo', 
                'public_metrics', 'lang', 
                'conversation_id', # id of the first tweet in a thread, if different then id, then id refers to a reply tweet
                'entities', #includes tags, mentions, urls
                'referenced_tweets', 'context_annotations', 
                'attachments', 'possibly_sensitive',
                'withheld', 'reply_settings', 'source'
                #'organic_metrics', #'promoted_metrics', #'non_public_metrics',
                ]
expansions = ['author_id', 
                'referenced_tweets.id', # refers to the tweet id in reply to which the current tweet was posted
                'referenced_tweets.id.author_id',
                'in_reply_to_user_id', 'attachments.media_keys',
                'entities.mentions.username']
place_fields=['full_name', 'id']
media_fields=['type', 'url', 'alt_text', 'public_metrics', 'duration_ms']


def media_to_df(response):
    '''
    Converts Media objects returned with tweets to a dataframe.
    '''
    media = []
    for m in response:
        media.append(
            { 
              'media_key': m.media_key,
              'media_type': m.type, 
              'alt_text': m.alt_text,
              'duration_ms': m.duration_ms
             })
    df = pd.DataFrame(media)
    df.set_index("media_key", inplace=True)
    return df

def users_to_df(response):
    '''
    Converts Users objects returned with tweets to a dataframe.
    '''
    users = []
    # Take all of the users, and put them into a dictionary of dictionaries with the info we want to keep
    for user in response:
        users.append(
            { 
            'userid': user.id,
            'username': user.username, 
            'followers': user.public_metrics['followers_count'],
            'tweets': user.public_metrics['tweet_count'],
            'profile_desc': user.description,
            'location': user.location,
            'verified': user.verified,
            'entities': user.entities
             })
    df = pd.DataFrame(users)
    df.set_index("userid", inplace=True)
    return df

def tweet_to_row(tweet):
    tweet_dict = \
    {
        'tweetid': tweet.id,
        'author_id': tweet.author_id, 
        'text': tweet.text,
        'created_at': tweet.created_at,
        'geo': tweet.geo,
        'retweets': tweet.public_metrics['retweet_count'],
        'replies': tweet.public_metrics['reply_count'],
        'likes': tweet.public_metrics['like_count'],
        'quote_count': tweet.public_metrics['quote_count'],
        'lang':tweet.lang,
        'conversation_id': tweet.conversation_id,
        'context_annotations': tweet.context_annotations,
        'entities': tweet.entities,
        'attachments': tweet.attachments,
        'possibly_sensitive': tweet.possibly_sensitive,
        'withheld' : tweet.withheld,
        'reply_settings': tweet.reply_settings,
        'source':tweet.source
    }
    if tweet.entities:
        tweet_dict['mentions']: [] if 'mentions' not in tweet.entities \
                                else tweet.entities['mentions']
        tweet_dict['urls']: [] if 'urls' not in tweet.entities \
                                else tweet.entities['urls']
        tweet_dict['hashtags']: [] if 'hashtags' not in tweet.entities \
                                else tweet.entities['hashtags']
        tweet_dict['referenced_tweets']: [] if 'referenced_tweets' \
                not in tweet.entities else tweet.entities['referenced_tweets']
    return tweet_dict

def included_tweets_to_df(response):
    result = []
    for tweet in response:
        result.append(tweet_to_row(tweet))

    df = pd.DataFrame(result)
    df.set_index('tweetid', inplace=True)
    return df

def tweets_to_df(response):
    result = []
    if len(response.data)==0:
        return None
    for tweet in response.data:
        result.append(tweet_to_row(tweet))

    df = pd.DataFrame(result)
    df.set_index('tweetid', inplace=True)
    return df

def search_users(uids):
    start = 0
    results = []
    while start<len(uids):
        try:
            res=client.get_users(ids=uids[start:start+100], user_fields=user_fields)
            results.append(res)
            print('batch size: {}, total: {}'.format(len(res.data)))
        except Exception as e:
            print('failed to get data')
        start+=100
    return results

def search_tweets(query, start_time, since_id, outdir, count):
    if since_id is not None:
        start_time=None
        
    print('query:{}, start: {}, id:{}'.format(query, start_time, since_id))

    tweet_count = 0
    try:
        for response in tweepy.Paginator(
                client.search_all_tweets, 
                query = query + " -is:retweet",
                user_fields = user_fields,
                tweet_fields = tweet_fields,
                expansions = expansions,
                start_time = start_time,
                since_id = since_id,
        #         end_time = '2021-01-21T00:00:00Z',
                place_fields= place_fields,
                media_fields= media_fields,
                max_results=100):

            tweet_count+=len(response.data)
            print('query: {} ({}), tweets: {}, total: {}'.format(
                query, count, len(response.data), tweet_count))

            if response.data==None or len(response.data)==0:
                print('no response found for: {}\n'.format(query))
                continue

            user_df = users_to_df(response.includes['users'])
            tweet_df = tweets_to_df(response)
            media_df, included_tweet_df = None, None
            if "media" in response.includes:
                media_df = media_to_df(response.includes['media'])
            if "tweets" in response.includes:
                included_tweet_df = included_tweets_to_df(response.includes['tweets'])


            if user_df is not None:
                user_df.to_csv("{}/users-search-{}-{}.csv".format(
                outdir, query, 
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
            if tweet_df is not None:
                tweet_df.to_csv("{}/tweets-search-{}-{}.csv".format(
                outdir, query, 
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
            if included_tweet_df is not None:
                included_tweet_df.to_csv("{}/inc-tweets-search-{}-{}.csv".format(
                outdir, query, 
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
            if media_df is not None:
                media_df.to_csv("{}/media-search-{}-{}.csv".format(
                outdir, query, 
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))

            time.sleep(5)

        return True

    except Exception as e:
        print("Exception for query:{}.\nError:{}".format(query, traceback.format_exc()))
        with open('exceptions.txt', 'a') as file:
            file.write("query:{}, exception:{}\n".format(query, e))
        return False


def collect_tweets(outdir, tagfile, stat_dir):
    if not os.path.exists(outdir):
            os.makedirs(outdir)
            
    with open(tagfile) as csv_file:
        reader = csv.reader(csv_file)
        tags = set(list(reader)[0])

    tags =  set([t.strip().lower() for t in tags])
    print("tags: ", len(tags))
        
    donetags = set([])
    if os.path.isfile('donetags.csv'): 
        with open('donetags.csv') as csv_file:
            reader = csv.reader(csv_file)
            donetags = set(list(reader)[0])

    donetags =  set([t.strip().lower() for t in donetags])
    tags = tags.difference(donetags)
    print("donetags:{}, tags:{} ".format(len(donetags), len(tags)))

    i=1
    for tag in tags:
        tag = tag.strip()
        print("Starting search for tag no:{} of {}, tag:{}".format(i, len(tags),tag))
        i+=1
        '''
        Retrieve the latest tweet collected before
        '''
        start_time = '2006-03-21T00:00:00Z'
        since_id = None
        if os.path.isfile('{}/tweet-stat-{}.json'.format(stat_dir, tag)):
            with open('{}/tweet-stat-{}.json'.format(stat_dir, tag), 'r') as fp:
                latest_tweet = json.loads(json.load( fp))
                since_id = latest_tweet['tweetid']


        success = search_tweets(tag, start_time, since_id,outdir, i)

        if success:
            donetags.add(tag)
            with open('donetags.csv', 'w') as csv_file:  
                writer = csv.writer(csv_file)
                writer.writerow(donetags)