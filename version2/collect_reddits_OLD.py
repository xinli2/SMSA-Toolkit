#!/usr/bin/env python
# coding: utf-8

# https://praw.readthedocs.io/en/stable/tutorials/comments.html
# https://praw.readthedocs.io/en/stable/code_overview/other/subredditstream.html#praw.models.reddit.subreddit.SubredditStream.comments
# 
# https://github.com/mattpodolak/pmaw#submissions


import sys, csv,os
import pandas as pd
import datetime as dt
from pmaw import PushshiftAPI
api = PushshiftAPI()

# Pushshift API documentation: https://github.com/mattpodolak/pmaw


def collect_subreddit(subreddit, outdir):
    # Step 1: collect posts under a subreddit
    print("Collecting posts on subreddit: {}".format(subreddit))
    submissions = api.search_submissions(subreddit=subreddit, limit=None)
    sub_df = pd.DataFrame(submissions)
    sub_ids = list(sub_df.loc[:, 'id']) 
    print("Collected {} posts".format(len(sub_df)))
    
    sub_df.to_csv('{}/{}.csv'.format(outdir, subreddit))

    # Step 2: retrieve comment ids for submissions
    print("Collecting comment ids")
    comment_ids = api.search_submission_comment_ids(ids=sub_ids) 
    comment_ids = list(comment_ids)
    print("Total {} comment ids found".format(len(comment_ids)))

    # Step 3 retrieve comments by id
    print("Collecting comments")
    comments = api.search_comments(ids=comment_ids)
    comments_df = pd.DataFrame(comments)
    print("Total {} comments collected (out of {} comment ids)".format(len(comments_df), len(comment_ids)))
    
    comments_df.to_csv('{}/{}-comments.csv'.format(outdir, subreddit))






def collect_reddits(outdir, subredditfile):
    # outdir = sys.argv[1]
    # subredditfile=sys.argv[2]

    if not os.path.exists(outdir):
            os.makedirs(outdir)
            
    with open(subredditfile) as csv_file:
        reader = csv.reader(csv_file)
        tags = set(list(reader)[0])

    tags =  set([t.strip().lower() for t in tags])
    print("tags: ", len(tags))
        
    # donetags = set([])
    # if os.path.isfile('donetags.csv'): 
    #     with open('donetags.csv') as csv_file:
    #         reader = csv.reader(csv_file)
    #         donetags = set(list(reader)[0])

    # donetags =  set([t.strip().lower() for t in donetags])
    # tags = tags.difference(donetags)
    # print("donetags:{}, tags:{} ".format(len(donetags), len(tags)))

    i=1
    for tag in tags:
        tag = tag.strip()
    #   print("Starting search for tag no:{} of {}, tag:{}".format(i, len(tags),tag))
        i+=1
    #     start_time = '2006-03-21T00:00:00Z'
    #     since_id = None
    #     if os.path.isfile('{}/tweet-stat-{}.json'.format(stat_dir, tag)):
    #         with open('{}/tweet-stat-{}.json'.format(stat_dir, tag), 'r') as fp:
    #             latest_tweet = json.loads(json.load( fp))
    #             since_id = latest_tweet['tweetid']

        collect_subreddit(tag, outdir)

    #     donetags.add(tag)
    #     with open('donetags.csv', 'w') as csv_file:  
    #         writer = csv.writer(csv_file)
    #         writer.writerow(donetags)



# def main():
#     posts = api.search_submissions(subreddit="science", limit=10)
#     post_list = [post for post in posts]
#     print(len(post_list))
#     for p in post_list:
#         print(f'\n\n{p}\n\n')
    

# if __name__=='__main__':
#     main()