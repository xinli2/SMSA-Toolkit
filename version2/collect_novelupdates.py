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
    nodes = self.soup.select("li.message")
    for node in nodes:
      comment = dict()
      comment['post_id'] = post["id"]
      comment['post_url'] = post["url"]
      comment['id'] = node.get("id").split("-")[-1]
      comment['author'] = get_text(node.select_one("a.username"))
      comment['jobTitle'] = get_text(node.select_one("em.userTitle"))
      comment['content'] = get_text(node.select_one("div.messageContent"))
      comment['created_date'] = node.select_one("div.messageMeta span.DateTime").get("title")
      for pair in node.select("dl.pairsJustified"):
        k = get_text(pair.select_one("dt")).strip(":")
        v = get_text(pair.select_one("dd"))
        comment[k] = v
      yield comment

  def yield_post(self):
    nodes = self.soup.select("li.searchResult")
    for node in nodes:
      post = dict()
      post["url"] = node.select_one("div.titleText h3.title a").get('href')
      post["url"] = parse.urljoin(self.browser.current_url, post["url"])
      # https://forum.novelupdates.com/threads/what-would-you-do-during-purge-night.151802/#post-7047440
      # https://forum.novelupdates.com/search/124299699/posts/7047849/
      post["id"] = node.get("id")
      post["title"] = get_text(node.select_one("div.titleText h3.title a"))
      post["snippet"] = get_text(node.select_one("blockquote.snippet"))
      tmp = node.select_one("div.meta span.DateTime")
      if tmp:
        post['created_date'] = tmp.get("title")
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
    def parse_and_next(url: str):
      if not self.__get(url, lambda: wait_for(self.browser, "div.searchResults", 120)):
        return
      posts = []
      for post in self.yield_post():
        self.posts.append(post)
        posts.append(post)
      for post in posts:
        tmp = self.browser.find_elements_by_css_selector("#" + post["id"] + " h3.title a")
        if tmp and len(tmp) > 0:
          tmp[0].click()
          time.sleep(3)
          self.find_comments(post)
          self.browser.back()

      nexts = self.browser.find_elements_by_css_selector("div.PageNav nav a")
      if nexts and len(nexts) > 0:
        next = nexts[-1]
        if next and get_text(next).find("Next") >= 0:
          time.sleep(3)
          next_url = parse.urljoin(self.browser.current_url, next.get_attribute('href'))
          parse_and_next(next_url)

    url = f"https://forum.novelupdates.com/search/124299699/?q={self.kw}&o=date"
    parse_and_next(url)

  def find_comments(self, post: dict):
    try:
      wait_for(self.browser, "#messageList")
      self.soup = BeautifulSoup(self.browser.page_source, 'lxml')
      post['url'] = self.browser.current_url
      for comment in self.yield_comment(post):
        self.comments.append(comment)
    except:
      print(self.browser.current_url + " 访问异常")

  def clear(self):
    self.posts.clear()
    self.comments.clear()

  def search_by_keyword(self, kw: str):
    self.kw = kw
    self.clear()
    self.find_posts()

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
    spider.save("novelupdates_data")
    browser.close()
