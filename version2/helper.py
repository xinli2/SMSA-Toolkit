# -*- coding: utf-8 -*-
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s - %(message)s", level=logging.INFO)
logger = logging


def wait_for(browser: WebDriver, selector: str, seconds: int = 20):
  WebDriverWait(browser, seconds, 0.3).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


def create_browser() -> WebDriver:
  logger.info("motion monitor")
  # get direct return, non-repetitive wait surface access complete
  desired_capabilities = DesiredCapabilities.CHROME
  desired_capabilities["pageLoadStrategy"] = "none"
  # Forbidden pictures sum screenplay
  options = webdriver.ChromeOptions()
  prefs = {
    'profile.default_content_setting_values': {
      'images': 2
    }
  }
  options.add_experimental_option('prefs', prefs)
  # developer model
  options.add_experimental_option('excludeSwitches', ['enable-automation'])
  # Forbidden blink
  options.add_argument("--disable-blink-features=AutomationControlled")
  # Install Chrome display location
  # options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
  options.add_argument('--no-sandbox')  # Solve DevToolsActivePort document missing report
  options.add_argument('window-size=1920x1080')  # Designated monitor division rate
  options.add_argument('--disable-gpu')  # This attribute has been added to the demand bug
  options.add_argument('--hide-scrollbars')  # Operating Articles, for some special pages
  options.add_argument('blink-settings=imagesEnabled=false')  # Unloading image, raising speed
  # options.add_argument('--headless')  # This article does not support visualization under linux.
  # Install chromedriver.exe dynamic location
  browser = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
#   browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#     "source": """
# Object.defineProperty(navigator, 'webdriver', {
# get: () => undefined
# })
# """})
  browser.implicitly_wait(10)
  return browser


def trim_line_break(s: str) -> str:
  if not s:
    return s
  return s.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')


def get_text(node) -> str:
  if not node:
    return None
  if isinstance(node, WebElement):
    s = node.text
  else:
    s = node.get_text()
  return trim_line_break(s.strip())


if __name__ == '__main__':
  logger.info("hello")
  browser = create_browser()
  # browser.get("https://www.neogaf.com/search/3364483/?q=roblox&o=relevance")
  # wait_for(browser, "div.block-container")
  # print(browser.page_source)
  # browser.get("https://www.neogaf.com/threads/roblox-famous-oof-sound-effect-is-now-gone.1639593/")
  # wait_for(browser, "article.message")
  # print(browser.page_source)
  browser.get("https://www.se7ensins.com/search/1655486/?q=roblox&o=relevance")
  browser.close()
