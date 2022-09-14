#!/usr/bin/env python
# coding: utf-8

# https://praw.readthedocs.io/en/stable/tutorials/comments.html
# https://praw.readthedocs.io/en/stable/code_overview/other/subredditstream.html#praw.models.reddit.subreddit.SubredditStream.comments
#
# https://github.com/mattpodolak/pmaw#submissions


import os
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import pandas as pd
from pmaw import PushshiftAPI

api = PushshiftAPI()


# Pushshift API documentation: https://github.com/mattpodolak/pmaw


def collect_subreddit(subreddit, outdir):
  # Step 1: collect posts under a subreddit
  begin = int(time.time() - 60 * 60 * 1)
  print(f"Collecting posts on subreddit: {subreddit} ")
  submissions = api.search_submissions(subreddit=subreddit, limit=None)
  sub_df = pd.DataFrame(submissions)
  print(f"Collected {len(sub_df)}'s posts")
  sub_df.to_csv(f'{outdir}/{subreddit}.csv', index=False)

  # Step 2: retrieve comment ids for submissions
  sub_ids = (len(sub_df) and list(sub_df.loc[:, 'id'])) or []
  print(f"Collecting comment ids of {len(sub_ids)}'s post")
  comment_ids = []
  if len(sub_ids) > 0:
    comment_ids = api.search_submission_comment_ids(ids=sub_ids).responses
  comment_ids = list(comment_ids)
  print(f"Total {len(comment_ids)} comment ids found")

  # Step 3 retrieve comments by id
  print("Collecting comments")
  comments_df = pd.DataFrame()
  if len(comment_ids) > 0:
    comments = api.search_comments(ids=comment_ids)
    comments_df = pd.DataFrame(comments)
  print(f"Total {len(comments_df)} comments collected (out of {len(comment_ids)} comment ids)")
  comments_df.to_csv(f'{outdir}/{subreddit}-comments.csv', index=False)


def collect_reddits(outdir: str, subredditfile: str):
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(subredditfile, "r") as f:
    tags = set([s.strip().lower() for s in f.readlines()])
  tags = list(tags)
  print(f"Search {len(tags)}'s tag => {tags}")
  for i in range(len(tags)):
    tag = tags[i].strip()
    print(f"Starting search for tag : {i + 1}/{len(tags)} = {tag}")
    collect_subreddit(tag, outdir)


def main():
  title = "roblox"
  # 近3小时 1661449725
  begin = int(time.time() - 60 * 60 * 1)
  submissions = api.search_submissions(subreddit=title, limit=None, after=begin)
  df = pd.DataFrame(submissions)
  print(df)
  df.to_csv(f"{title}_submissions.csv", index=False)
  submission_ids = list(df.loc[:, 'id'])
  print(f"submission_ids:{len(submission_ids)} => {submission_ids}")
  comment_ids = api.search_submission_comment_ids(submission_ids).responses
  print(f"comment_ids:{len(comment_ids)} => {comment_ids}")
  comments = api.search_comments(ids=comment_ids)
  df = pd.DataFrame(comments)
  print(df)
  df.to_csv(f"{title}_comments.csv", index=False)


if __name__ == '__main__':
  main()
