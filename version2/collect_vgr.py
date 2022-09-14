# -*- coding: utf-8 -*-
import os
import time
import traceback
from urllib import parse

import pandas as pd
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
    nodes = self.soup.select("article.cPost")
    for node in nodes:
      comment = dict()
      comment['post_id'] = post["id"]
      comment['post_url'] = post["url"]
      comment['id'] = node.get("id").split("_")[-1]
      comment['author'] = get_text(node.select_one("div.cAuthorPane_author a"))
      comment['content'] = get_text(node.select_one("div.cPost_contentWrap"))
      comment['created_date'] = node.select_one("div.ipsComment_meta a.ipsType_blendLinks time").get("datetime")
      tmp = node.select_one("ul.cAuthorPane_stats a.ipsType_blendLinks")
      if tmp and tmp.get("_title"):
        comment['comments'] = tmp.get("_title").strip().split(" ")[0]
      yield comment
    next = self.browser.find_elements_by_css_selector("li.ipsPagination_next a")
    if next and len(next) > 0 and next[0].is_displayed():
      url = parse.urljoin(self.browser.current_url, next[0].get_attribute("href"))
      if not self.__get(url, lambda: wait_for(self.browser, "#elPostFeed")):
        return
      for comment in self.yield_comment(post):
        yield comment

  def yield_post(self):
    nodes = self.soup.select("li.ipsStreamItem")
    for node in nodes:
      post = dict()
      post["url"] = node.select_one("span.ipsContained a").get('href')
      post["url"] = parse.urljoin(self.browser.current_url, post["url"])
      # https://www.vgr.com/forum/topic/14430-do-you-play-old-video-games/page/5/#comments
      post["id"] = post["url"].split("topic/")[-1].split("-")[0]
      post["title"] = get_text(node.select_one("span.ipsContained a"))
      post["snippet"] = get_text(node.select_one("div.ipsStreamItem_snippet"))
      post['created_date'] = node.select_one("ul.ipsStreamItem_meta time").get("datetime")
      post["replies"] = get_text(node.select("ul.ipsStreamItem_meta a.ipsType_blendLinks")[-1]).split(" ")[0]
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
      logger.error(f"visit {url} unusual")
      traceback.print_exc()
      return False

  def find_posts(self):
    def parse_and_next(url: str):
      if not self.__get(url, lambda: wait_for(self.browser, "#elSearch_main")):
        return
      for post in self.yield_post():
        self.posts.append(post)
      next = self.browser.find_elements_by_css_selector("li.ipsPagination_next a")
      if next and len(next) > 0 and next[0].is_displayed():
        time.sleep(3)
        next_url = parse.urljoin(self.browser.current_url, next[0].get_attribute('href'))
        parse_and_next(next_url)

    url = f"https://www.vgr.com/forum/search/?q={self.kw}&quick=1"
    parse_and_next(url)

  def find_comments(self, post: dict):
    url = post["url"]
    if not self.__get(url, lambda: wait_for(self.browser, "#elPostFeed")):
      return
    for comment in self.yield_comment(post):
      self.comments.append(comment)

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
    df_posts = pd.DataFrame(self.posts)
    df_posts.to_csv(f"{outdir}/{self.kw}.csv", index=False)
    logger.info(f"Save {len(df_posts)}'s posts")
    df_comments = pd.DataFrame(self.comments)
    df_comments.to_csv(f"{outdir}/{self.kw}-comments.csv", index=False)
    logger.info(f"Save {len(df_comments)}'s comments")


if __name__ == '__main__':
  browser = create_browser()
  spider = Spider(browser)
  try:
    spider.search_by_keyword("roblox")
  except:
    traceback.print_exc()
  finally:
    spider.save("vgr_data")
    browser.close()
