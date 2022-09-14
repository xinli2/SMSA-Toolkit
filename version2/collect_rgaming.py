# -*- coding: utf-8 -*-
import os
import time
import traceback
from urllib import parse

from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver

from helper import create_browser, logger, wait_for, get_text


class Spider:
  def __init__(self, browser: WebDriver):
    self.browser: WebDriver = browser
    self.soup: BeautifulSoup = None
    self.kw: str = None
    self.posts = []
    self.comments = []

  def yield_comment(self, post: dict):
    nodes = self.soup.select("div.Comment")
    for node in nodes:
      comment = dict()
      comment['post_id'] = post["id"]
      comment['post_url'] = post["url"]
      comment['id'] = node.parent.get("id")
      comment['author'] = get_text(node.select_one("a[data-testid='comment_author_link']"))
      comment['content'] = get_text(node.select_one("div.RichTextJSON-root"))
      comment['created_date'] = get_text(node.select_one("a[data-testid='comment_timestamp']"))
      for div in node.select("div"):
        if div.get("id") and div.get("id").find("vote-arrows") >= 0:
          comment['replies'] = get_text(div)
      yield comment

  def yield_post(self):
    nodes = self.soup.select("div.Post")
    for node in nodes:
      post = dict()
      post["id"] = node.get("id")
      for div in node.select("div"):
        if div.select_one("a[data-click-id='body']"):
          post["url"] = div.select_one("a[data-click-id='body']").get('href')
          post["url"] = parse.urljoin(self.browser.current_url, post["url"])
          post["title"] = get_text(div)
        elif div.select_one("span[data-click-id='timestamp']"):
          post["created_date"] = get_text(div.select_one("span[data-click-id='timestamp']"))
      for span in node.select("div div div span"):
        ss = get_text(span).split(" ")
        if len(ss) >= 2 and ss[1] in ["awards", "upvotes", "comments"]:
          post[ss[1]] = ss[0]
      yield post

  def __get(self, url, wait) -> bool:
    logger.info(f"visit {url}")
    try:
      self.browser.get(url)
      if wait:
        wait()
      self.soup = BeautifulSoup(self.browser.page_source, 'lxml')
      return True
    except:
      logger.error(f"访问 {url} 异常")
      traceback.print_exc()
      return False

  def find_posts(self):
    def parse_and_next():
      prev = len(self.soup.select("div.Post"))
      # 滚动加载
      self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
      time.sleep(10)
      self.soup = BeautifulSoup(self.browser.page_source, 'lxml')
      curr = len(self.soup.select("div.Post"))
      if prev == curr:
        for post in self.yield_post():
          self.append_post(post)
      else:
        parse_and_next()

    url = f"https://www.reddit.com/search/?q={self.kw}"
    if not self.__get(url, lambda: wait_for(self.browser, "#AppRouter-main-content")):
      return
    parse_and_next()

  def find_comments(self, post: dict):
    url = post["url"]
    if not self.__get(url, lambda: wait_for(self.browser, "div.ListingLayout-outerContainer")):
      return
    for comment in self.yield_comment(post):
      self.append_comment(comment)

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
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    import pandas as pd
    df_posts = pd.DataFrame(self.posts)
    df_posts.to_csv(f"{outdir}/{self.kw}.csv", index=False)
    logger.info(f"Save {len(df_posts)}'s posts")
    df_comments = pd.DataFrame(self.comments)
    df_comments.to_csv(f"{outdir}/{self.kw}-comments.csv", index=False)
    logger.info(f"Save {len(df_comments)}'s comments")

  def append_post(self, post):
    self.posts.append(post)

  def append_comment(self, comment):
    self.comments.append(comment)
    if len(self.comments) % 200 == 0:
      spider.save("rgaming_data")


if __name__ == '__main__':
  browser = create_browser()
  spider = Spider(browser)
  try:
    spider.search_by_keyword("roblox")
  except:
    traceback.print_exc()
  finally:
    spider.save("rgaming_data")
    browser.close()
