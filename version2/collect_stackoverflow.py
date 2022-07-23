# coding: utf-8

# https://stackapi.readthedocs.io/en/latest/
# https://github.com/AWegnerGitHub/stackapi
# https://stackoverflow.com/questions/59339862/retrieving-text-body-of-answers-and-comments-using-stackexchange-api

import sys, csv,os
import pandas as pd
import datetime as dt
from stackapi import StackAPI
import json

def search_stack():
    APP_KEY = ""
    ACCESS_TOKEN = ""
    SITE = StackAPI('stackoverflow', key=APP_KEY, access_token=ACCESS_TOKEN)
    '''
    SITE = StackAPI("stackoverflow")
    #API can have up to 100 pages
    SITE.max_pages = 1

    #API call can have up to 100 results
    SITE.page_size = 1
    '''
    tag = 'roblox'
    questions = SITE.fetch('questions', taged=tag, filter='withbody', max_pages=10000000, page_size=100 )
    comments = SITE.fetch('comments', taged=tag, filter='withbody', max_pages=10000000, page_size=100)
    return questions,comments

with open('questions_csv_file','w') as f:
    write = csv.writer(f)
    #print (questions)
    for questions_line in questions:
        #print(questions_line)
        write.writerow(questions_line)

with open('comments_csv_file','w') as f:
    write = csv.writer(f)
    for comments_line in comments:
        print(comments_line)
        write.writerow(comments_line)
#(T0DO: How to write data into CSV file.)
        

