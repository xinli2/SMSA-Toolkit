# coding: utf-8
###############################################################################
# Collect data from Stackoverflow
###############################################################################
# How to get access_token
# Make sure "Client Side Flow Is Enabled"
# Replace the client_id 123456 with your own id
# Open https://stackexchange.com/oauth/dialog?client_id=23959&scope=read_inbox,no_expiry&redirect_uri=https://stackexchange.com/oauth/login_success
# The access token is in the redirected link: https://stackexchange.com/oauth/login_success#access_token=AAAAAAA
#23959
#D(vBwKNLxTSaYCo7gIYnUw))
import requests
import time
import json
import pandas as pd
from requests.adapters import HTTPAdapter, Retry
import random

key = 'lv0TzW20Umtr0jZ3BeIBEQ(('
access_token_list = ['D(vBwKNLxTSaYCo7gIYnUw))']
# file of scaped data
post_file = 'posts.json'
# Specify search term
term = 'roblox'
# Specify start page
page = 1



try:
    with open(post_file, 'r') as fp:
        posts = json.load(fp)
except IOError:
    print('Posts file not found, will create a new one.')
    posts = {'questions': [],
             'answers': []}

access_token_idx = 0
has_more = 0


s = requests.Session()
retries = Retry(total=3, backoff_factor=1)
s.mount('https://', HTTPAdapter(max_retries=retries))


def check_quota(res):
    global access_token_idx
    if res['quota_remaining'] < 1:
        print(
            f'access_token {access_token_list[access_token_idx]} has no more quota')
        if access_token_idx == len(access_token_idx) - 1:
            print('No more available access token. Program stops!!!')
            raise
        else:
            access_token_idx += 1


def get_comment(post_id):
    global access_token_idx
    comment_url = f'https://api.stackexchange.com/2.3/posts/{post_id}/comments?access_token={access_token_list[access_token_idx]}&key={key}&order=desc&sort=creation&site=stackoverflow&filter=!nKzQURB9EO'
    try:
        res = s.get(comment_url)
        time.sleep(random.uniform(0, 1))
    except requests.exceptions.RequestException as err:
        print(f"Error when fetching comment for {post_id}, skip.")
        return
    if (res.status_code == 200):
        res = res.json()
        # check application must wait
        if 'backoff' in res:
            time.sleep(res['backoff'] + 2)
        # check the remaining quota
        check_quota(res)
        # return comments
        return res['items']
    else:
        print(res.json())


def get_answers(question_id):
    global access_token_idx
    answers_url = f'https://api.stackexchange.com/2.3/questions/{question_id}/answers?access_token={access_token_list[access_token_idx]}&key={key}&order=desc&sort=creation&site=stackoverflow&filter=!nKzQURF6Y5'
    try:
        res = s.get(answers_url)
        time.sleep(random.uniform(0, 1))
    except requests.exceptions.RequestException as err:
        print(f"Error when fetching answer for question {question_id}")
        raise SystemExit(err)
    if (res.status_code == 200):
        res = res.json()
        # check application must wait
        if 'backoff' in res:
            time.sleep(res['backoff'] + 2)
        # check the remaining quota
        check_quota(res)
        # check comments for each answer
        items = res['items']
        for item in items:
            item['comment'] = get_comment(item['answer_id'])
            posts['answers'].append(item)
        return True
    else:
        print(res.json())
        return False


def search_questions(term, page):
    global access_token_idx
    global has_more
    pagesize = 40
    while True:
        print(f"Getting page {page}, pagesize {pagesize}")
        search_url = f'https://api.stackexchange.com/2.3/search/advanced?access_token={access_token_list[access_token_idx]}&key={key}&page={page}&pagesize={pagesize}&order=desc&sort=creation&q={term}&site=stackoverflow&filter=!nKzQUR3Egv'
        try:
            res = s.get(search_url)
            time.sleep(random.uniform(0, 1))
        except requests.exceptions.RequestException as err:
            print("OOps: Internet error", err)
            raise SystemExit(err)
        if (res.status_code == 200):
            res = res.json()
            # check application must wait
            if 'backoff' in res:
                time.sleep(res['backoff'] + 2)
            # check the remaining quota
            check_quota(res)
            # check returns questions
            question_ids = [i['question_id'] for i in posts['questions']]
            for item in res['items']:
                # if question already in current questions list, skip
                if item['question_id'] in question_ids:
                    continue
                # search comment for question
                item['comment'] = get_comment(item['question_id'])
                if item['answer_count'] == 0:
                    posts['questions'].append(item)
                if item['answer_count'] != 0:
                    answers = get_answers(item['question_id'])
                    if answers:
                        posts['questions'].append(item)
            # regulary save scrape results to file
            with open(post_file, "w") as outfile:
                json.dump(posts, outfile)
            # check if there are more search results
            # the api's has_more could return false even there are more results
            # break until 3 more pages no new results
            page += 1
            if res['has_more']:
                has_more = 0
            else:
                has_more += 1
                if has_more > 3:
                    break
        else:
            print(res.json())
            break


if __name__ == "__main__":
    try:
        search_questions(term, page)
    except:
        print("Searching process interupted, saving current files")

    data = pd.DataFrame.from_records(posts['questions'])
    data.to_csv('questions.csv')
    data = pd.DataFrame.from_records(posts['answers'])
    data.to_csv('answers.csv')
