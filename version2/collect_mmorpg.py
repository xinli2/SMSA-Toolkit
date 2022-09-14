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

  def yield_post(self):
    nodes = self.soup.select("div.gsc-webResult")
    for node in nodes:
      post = dict()
      post["url"] = node.select_one("div.gs-title a.gs-title").get('href')
      post["url"] = parse.urljoin(self.browser.current_url, post["url"])
      post["title"] = get_text(node.select_one("div.gs-title a.gs-title"))
      post["snippet"] = get_text(node.select_one("div.gsc-table-result"))
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

  def fill_post(self, post: dict):
    pass

  def find_posts(self):
    url = f"https://www.mmorpg.com/search?q={self.kw}"
    if not self.__get(url, lambda: wait_for(self.browser, "div.gsc-results")):
      return

    def parse_and_next():
      for post in self.yield_post():
        self.posts.append(post)
      next = self.browser.find_elements_by_xpath("//div[contains(@class,'gsc-cursor-current-page')]/following-sibling")
      if next and len(next) > 0:
        logger.info("下一页")
        next[0].click()
        time.sleep(3)

    parse_and_next()

  def clear(self):
    self.posts.clear()

  def search_by_keyword(self, kw: str):
    self.kw = kw
    self.clear()
    self.find_posts()
    for post in self.posts:
      self.fill_post(post)

  def save(self, outdir: str):
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    df_posts = pd.DataFrame(self.posts)
    df_posts.to_csv(f"{outdir}/{self.kw}.csv", index=False)
    logger.info(f"Save {len(df_posts)}'s posts")


if __name__ == '__main__':
  browser = create_browser()
  spider = Spider(browser)
  try:
    spider.search_by_keyword("roblox")
  except:
    traceback.print_exc()
  finally:
    spider.save("mmorpg_data")
    browser.close()
