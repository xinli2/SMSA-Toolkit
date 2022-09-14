# -*- coding: utf-8 -*-
import os
import traceback
from urllib import parse

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver

from helper import create_browser, logger, get_text, wait_for


class Spider:
  def __init__(self, browser: WebDriver):
    self.browser: WebDriver = browser
    self.soup: BeautifulSoup = None
    self.posts = []
    self.comments = []
    self.kw: str = None

  def yield_comment(self, post: dict):
    nodes = self.soup.select("article.message--post")
    for node in nodes:
      comment = dict()
      comment['post_id'] = post["id"]
      comment['post_url'] = post["url"]
      comment['author'] = node.get("data-author")
      comment['id'] = node.get("data-content").split("-")[-1]
      comment['joined_date'] = node.select_one("div.message-userStats time.u-dt").get("datetime")
      comment['created_date'] = node.select_one("div.message-attribution-main time.u-dt").get("datetime")
      comment['content'] = node.select_one("div.message-content div.bbWrapper").get_text().strip()
      yield comment

  def yield_post(self):
    nodes = self.soup.select("li.block-row")
    for node in nodes:
      post = dict()
      post["title"] = get_text(node.select_one(".contentRow-title"))
      post["url"] = node.select_one(".contentRow-title a").get('href')
      post["url"] = parse.urljoin(self.browser.current_url, post["url"])
      post["id"] = post["url"].split("-")[-1]
      post["subtitle"] = get_text(node.select_one(".contentRow-subtitle"))
      post["snippet"] = get_text(node.select_one(".contentRow-snippet"))
      post["replies"] = node.select_one("i.message-icon[title='Replies']").next_sibling.strip()
      post["views"] = node.select_one("i.eye-icon[title='Views']").next_sibling.strip()
      post["username"] = node.select_one("time.u-dt").get("datetime")
      yield post

  def __get(self, url: str, wait) -> bool:
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

    def parse_and_next(url):
      if not self.__get(url, lambda: wait_for(self.browser, "div.block-outer")):
        return
      for post in self.yield_post():
        self.posts.append(post)
      next = self.browser.find_elements_by_css_selector("a.pageNav-jump--next")
      if next and len(next) > 0:
        next_url = parse.urljoin(self.browser.current_url, next[0].get_attribute('href'))
        parse_and_next(next_url)

    url = f"https://www.robloxforum.com/search/480/?q={self.kw}&o=relevance"
    parse_and_next(url)

  def find_comments(self, post: dict):
    if not self.__get(post["url"], lambda: wait_for(self.browser, "div.p-body-pageContent")):
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
    spider.save("robloxforum_data")
    browser.close()
