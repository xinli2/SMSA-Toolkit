·Use cases:

·Sensing Analysis:Conduct software and give social media sensing analysis for software security concern results.
·Enhancing the framework: Enhance SMSASSC toolkit through the incorporation of additionally scripts from third-party sources.


·Proposed Framework:

·There are two code sections. The name scraper.py is the crawler code, and the sentiment_analysis is the sentiment analysis code. The crawler chooses a variety of crawler
tools, including selenium, requests, regex, newspaper, and various APIs. The crawler uses multi-threaded crawling.

·Sentiment analysis consists of three parts: data preprocessing, word frequency analysis displayed in a pie chart, word cloud, and a classifier based on the Decision 
Tree-VAUDER- Machine Learning Model. The main packages used are Pandas, Matplotlib, Nltk, Wordcloud, and Numpy.

·The data produced by the crawler program includes the review title articles crawled from 6 data sources according to the selected keyword combination. The data sources 
are Youtube, Facebook, Twitter, Google News, RSS feeds, and Reddit.

·The data produced by the sentiment analysis program is summarized by the software, each software has a word cloud, a pie chart, the total sentiment analysis index of 
game reviews, and the top ten reviews by score (.csv).
