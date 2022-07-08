# -*- coding: utf-8 -*-
"""
web-scraper designed for pulling comments, 
news, and articles on selected keywords
"""
## required dependencies
import pandas as pd
import numpy as np
import os 
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread
import threading
import praw
import twint
import nest_asyncio
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
nest_asyncio.apply()
from GoogleNews import GoogleNews


def reddit_scalp(keyword):
    ## scraper on reddit website
    ## api key is required to gain access
    reddit = praw.Reddit(client_id='UdQPf6yOva9GE94mQ9e4RA', 
                         client_secret='2etLPIoO8lOIbAGvj8aFQaZKcvyOXQ', 
                         user_agent='pachong',
                         check_for_async=False)
    
    reddit_all = reddit.subreddit("all").search(str(keyword),limit=1000)
    result=[]
    for i in reddit_all:
        ## scraping all posts and comments that appear in the search results
        post=i.selftext
        temp=i.comments
        temp.replace_more(limit=None)
        comments=[c.body for c in temp]
        comments.insert(0,post)
        result.append(comments)
    ## text results are stored in csv format in the same directory
    pd.DataFrame(result).rename(columns={0:'title'}).to_csv(os.getcwd()+'/'+str(keyword)+' reddit.csv',index=False,encoding='utf-8')
    print(str(keyword)+' search completed')

def twitter_scalp(keyword):
    ## twitter scraper using the pypi twint package
    t = twint.Config()
    t.Search = str(keyword)
    t.Store_csv= True
    t.Limit = 10000
    t.Hide_output = True
    t.Output=os.getcwd()+'/emocloud'+'/'+str(keyword)+' twitter.csv'
    twint.run.Search(t)
    print(str(keyword)+' search completed')

def wta(driver,xpath,waittime=5):
    ## selenium-driven explicit wait method 
    try: 
        element=WebDriverWait(driver,waittime).until(
            EC.visibility_of_element_located((By.XPATH,xpath)))
        return True
    except:
        return False

def wtd(driver,xpath,waittime=10):
    ## selenium-driven explicit wait method 
    try: 
        element=WebDriverWait(driver,waittime).until(
            EC.invisibility_of_element_located()((By.XPATH,xpath)))
        return True
    except:
        return False

def facebook_scalp(kw_g,kw_a):
    ## facebook post scraper using selenium chromedriver
    driver=webdriver.Chrome(os.getcwd()+'/emocloud/chromedriver')
    options=webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver.get('https://m.facebook.com')
    
    ## login step
    xpath_login='//*[@class="_7nyk _7nyj"]'
    if wta(driver,xpath_login):
        driver.find_element_by_xpath(xpath_login).click()
        
    xpath_username='//*[@placeholder="Mobile number or email"]'
    xpath_pwd='//*[@placeholder="Password"]'
    if wta(driver,xpath_username):
        username='1412470309@qq.com'
        password='290541'
        driver.find_element_by_xpath(xpath_username).send_keys(username)
        driver.find_element_by_xpath(xpath_pwd).send_keys(password)
        driver.find_element_by_xpath('//*[@name="login"]').click()
    
    if wta(driver,'//*[@class="_54k8 _56bs _26vk _56b_ _56bw _56bt"]'):
        driver.find_element_by_xpath('//*[@class="_54k8 _56bs _26vk _56b_ _56bw _56bt"]').click()
    
    ## using facebook embedded search box
    driver.get('https://m.facebook.com/search/posts/?q='+kw_g+'%20'+kw_a)
    xpath_circle='//*[@id="see_more_pager"]'
    xpath_posthrefs='//*[@class="_5msj _26yo"]'
    if wta(driver,xpath_posthrefs):
        ## continous scrolling til the end 
        while wta(driver,xpath_circle,waittime=5):
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        
        temp=driver.find_elements_by_xpath(xpath_posthrefs)
        hrefs=[h.get_attribute('href') for h in temp]  
    
    else:
        print('no post for'+kw_g+' '+kw_a)
        return False
    
    ## and check related posts using URLs and scrape texts
    result=[]
    for h in hrefs:
        driver.get(h)
        xpath_p='//*[@class="_5rgt _5nk5"]/div//p'
        if wta(driver,xpath_p):
            ps=driver.find_elements_by_xpath(xpath_p)
            msg=''.join([p.text for p in ps])
            result.append(msg)
    
    ## all texts are stored in csv format
    pd.DataFrame(result).to_csv(os.getcwd()+'/'+kw_g+' '+kw_a+' facebook.csv',
                                encoding='utf-8',index=False)
    print(kw_g+' '+kw_a+' complete')
    return True

def youtube_scalp(kw_g,kw_a):
    ## youtube comment scalper
    kw_g='Minecraft';kw_a='Safe'
    options=webdriver.ChromeOptions()
    #options.add_argument('headless')
    options.add_argument("window-size=400,400")
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver=webdriver.Chrome(os.getcwd()+'/emocloud/chromedriver',options=options)
    driver.get('https://www.youtube.com/results?search_query='+kw_g+'+'+kw_a)
    
    xpath_non='//*[@class="promo-title style-scope ytd-background-promo-renderer"]'
    if wta(driver,xpath_non,waittime=3):
        print('no result')
        return False
    
    ## continuing loading videos
    xpath_pm='//*[@id="message"]'
    count=1
    while ''.join([i.text for i in driver.find_elements_by_xpath(xpath_pm)])!='No more results':
        driver.execute_script("window.scrollTo(0,arguments[0])",count*10000)
        count+=1
    
    ## scrape related titles and comments
    xpath_href='//*[@id="video-title"]'
    temp=driver.find_elements_by_xpath(xpath_href)
    hrefs=[h.get_attribute('href') for h in temp]
    time.sleep(3)
    
    result=[]
    for h in hrefs:
        if not isinstance(h,str):
            pass
        driver.get(h)
        msg=''
        xpath_title='//*[@class="title style-scope ytd-video-primary-info-renderer"]'
        xpath_info='//*[@class="content style-scope ytd-video-secondary-info-renderer"]'
        if wta(driver,xpath_info,waittime=3):
            msg+=driver.find_element_by_xpath(xpath_title).text
        if wta(driver,xpath_info,):
            msg+=driver.find_element_by_xpath(xpath_info).text
        result.append(msg)
    
    print(kw_g+' '+kw_a+' complete')
    pd.DataFrame(result).to_csv(os.getcwd()+'/'+kw_g+' '+kw_a+' youtube.csv',
                                encoding='utf-8',index=False)
    return True

def gnews(keyword):
    ## google news scraper
    lst=[]
    ## find all articles with keyword param in 5 years
    googlenews = GoogleNews(lang='en', period='5y')    
    googlenews.search(keyword)
    result=googlenews.result()
    googlenews.clear()
    for r in result:
        s=r['title']+r['desc']
        lst.append(s)
    pd.DataFrame(lst).to_csv(os.getcwd()+'/'+keyword+' gnews.csv',
                                 encoding='utf-8',index=False)   
    
    print(keyword+' complete')

## games and adjectives supplied in advance
kw_game=['Minecraft','Cubic Castles','Minetest','KoGaMa','Fortnite','8BitMMO','Growtopia']
kw_adj=['Safe','Security','Script','Model','Data stores','Plugin']

for g in kw_game:
    for a in kw_adj:
        ## using threading method to make scraping more efficient
        t1=Thread(target=reddit_scalp,args=[g+' '+a]);t1.start()
        t2=Thread(target=twitter_scalp,args=[g+' '+a]);t2.start()
        facebook_scalp(g,a)
        youtube_scalp(g,a)
        t5=Thread(target=gnews,args=[g+' '+a]);t5.start()



