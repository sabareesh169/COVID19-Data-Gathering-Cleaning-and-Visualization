# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 20:55:06 2020

@author: sabareesh
"""

from datetime import date, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import requests
import en_core_web_sm
nlp = en_core_web_sm.load()

class News:
    
    d = date.today().strftime("%m-%d-%y")
    cnn_url="https://www.cnn.com/world/live-news/coronavirus-pandemic-{}/index.html".format(d)
    nbc_url='https://www.nbcnews.com/health/coronavirus'
    cnbc_rss_url='https://www.cnbc.com/id/10000108/device/rss/rss.html'
    urls=[cnn_url, nbc_url,cnbc_rss_url]

    def __init__(self, urls= urls, formats=['html.parser','html.parser','xml'],\
                tags=['h2','h2','description'], websites=['CNN', 'NBC','CNBC']):
        self.formats = formats
        self.tags = tags
        self.websites = websites
        self.last_update = date.today() - timedelta(days=1)
        self.news_dict = []
        self.news_df = pd.DataFrame()
    
    def today_news_dict(self):

        news_dict = []
        crawl_len=0
        for url in self.urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, self.formats[crawl_len])

            for link in soup.find_all(self.tags[crawl_len]):
                if(len(link.text.split(" ")) > 4):
                    entities=[]
                    entities=[(ent.text, ent.label_) for ent in nlp(link.text).ents]
                    news_dict.append({'website':self.websites[crawl_len],'url': url,\
                                      'headline':link.text, 'entities':entities, 'date': date.today()})

            crawl_len=crawl_len+1
        return news_dict
    
    def update_news_data(self, force_update = False):
        
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
                return self.news_dict
        
        self.news_df = self.news_df.append(pd.DataFrame(self.today_news_dict()))
        self.news_df.drop_duplicates(['headline'], keep='last', inplace=True)
        self.last_update = date.today()
        
        return self.news_df
    
    def add_URL(self, url, format_, tag, website):
        self.urls.append(url)
        self.formats.append(format_)
        self.tags.append(tag)
        self.websites.append(website)
        
    def update_news_CSV(self, force_update = False):
        
        try: 
            self.news_df = pd.read_csv("web_scraping.csv")
            self.last_update = self.news_df['date'].iloc[-1]
        except: pass
        
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
            return 
        
        self.update_news_data(force_update)
        self.news_df.to_csv("web_scraping.csv", index=False)