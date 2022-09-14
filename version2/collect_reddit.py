{'url': 'https://api.pushshift.io/reddit/submission/search', 'params': {'subreddit': 'roblox', 'limit': None, 'size': 100, 'sort': 'desc', 'metadata': 'true', 'before': 1662389851, 'after': 1659236251}}


# -*- coding: utf-8 -*-
import os
import time
import traceback

from pmaw import PushshiftAPI

from helper import logger


class Spider:
  def __init__(self):
    self.posts = []
    self.comments = []
    self.kw: str = None
    self.api = PushshiftAPI()

  def find_posts(self):
    interval = 60 * 60 * 1
    before = int(time.time())
    after = before - interval
    submissions = self.api.search_submissions(subreddit=self.kw, before=before, after=after)
    while len(submissions) > 0:
      for post in submissions:
        self.append_post(post)
      before = after
      after = after - interval
      submissions = self.api.search_submissions(subreddit=self.kw, before=before, after=after)

  def find_comments(self, post: dict):
    submission_ids = [post['id'] for post in self.posts]
    index = 0

    def find(begin, end):
      ids = submission_ids[begin:end]
      comment_ids = self.api.search_submission_comment_ids(ids).responses
      comments = self.search_comments(ids=comment_ids)
      for comment in comments:
        self.append_comment(comment)

    while index < len(submission_ids):
      next_index = min(index + 10, len(submission_ids))
      find(index, next_index)
      index = next_index

  def clear(self):
    self.posts.clear()
    self.comments.clear()

  def search_by_keyword(self, kw: str):
    self.kw = kw
    self.clear()
    self.find_posts()
    for post in self.posts:
      self.find_comments(post)

  def save(self, outdir: str):
    import pandas as pd
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    df_posts = pd.DataFrame(self.posts)
    df_posts.to_csv(f"{outdir}/{self.kw}.csv", index=False)
    logger.info(f"Save {len(df_posts)}'s posts")
    df_comments = pd.DataFrame(self.comments)
    df_comments.to_csv(f"{outdir}/{self.kw}-comments.csv", index=False)
    logger.info(f"Save {len(df_comments)}'s comments")

  def append_post(self, post):
    self.posts.append(post)
    if len(self.posts) % 100 == 0:
      self.save("0_reddit")

  def append_comment(self, comment):
    self.comments.append(comment)
    if len(self.comments) % 100 == 0:
      self.save("0_reddit")


if __name__ == '__main__':
  spider = Spider()
  try:
    spider.search_by_keyword("roblox")
  except:
    traceback.print_exc()
  finally:
    spider.save("reddit_data")
