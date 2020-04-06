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
'''
This class collects the news headlines from three different websites.
Daily update helps to infer the day of the headline without extracting explicitly.
'''
class News:
    
    # defining the default urls and their details.
    d = date.today().strftime("%m-%d-%y")
    cnn_url="https://www.cnn.com/world/live-news/coronavirus-pandemic-{}/index.html".format(d)
    nbc_url='https://www.nbcnews.com/health/coronavirus'
    cnbc_rss_url='https://www.cnbc.com/id/10000108/device/rss/rss.html'
    urls=[cnn_url, nbc_url, cnbc_rss_url]
    formats=['html.parser','html.parser','xml']
    tags=['h2','h2','description']
    websites=['CNN', 'NBC','CNBC']
    
    def __init__(self):
        
        # Empty dataframe and dictionary to store news
        self.news_dict = []
        try: 
            self.news_df = pd.read_csv("web_scraping.csv")
            self.last_update = self.news_df['date'].iloc[-1]
        except: 
            self.news_df = pd.DataFrame()
            # The last update by default is initialized to yesterday to be able to update the data atleast once.
            self.last_update = date.today() - timedelta(days=1)
    
    def today_news_dict(self):
        '''
        collects headlines and extracts entities from the headlines and 
        returns the dictionary.
        '''
        news_dict = []
        scrap_len=0
        
        # Loop through the urls
        for url in self.urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, self.formats[scrap_len])

            # Extract headlines from the website
            for link in soup.find_all(self.tags[scrap_len]):
                
                # Less than 4 words might not mean a very useful headline
                if(len(link.text.split(" ")) > 4):
                    entities=[]
                    
                    # Extract the entities from the headline and store them
                    entities=[(ent.text, ent.label_) for ent in nlp(link.text).ents]
                    news_dict.append({'website':self.websites[scrap_len],'url': url,\
                                      'headline':link.text, 'entities':entities, 'date': date.today()})

            scrap_len=scrap_len+1
        return news_dict
    
    def update_news_data(self):
        '''
        Gets todays news dataframe and append to the existing dataframe.
        Dropping duplicates since to get only the latest news.
        '''
        self.news_df = self.news_df.append(pd.DataFrame(self.today_news_dict()))
        self.news_df.drop_duplicates(['headline'], keep='last', inplace=True)
            
    def add_URL(self, url, format_, tag, website):
        '''
        add additional urls and details if needed
        '''
        self.urls.append(url)
        self.formats.append(format_)
        self.tags.append(tag)
        self.websites.append(website)
        
    def update_news_CSV(self, force_update = False):
        '''
        Reads in the file and updates the file if not up to date.
        Args:
            force_update: If True, updates the file irrespective of the last update.
        '''

        # returns if there is no need to update
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
            return 
        
        self.update_news_data(force_update)
        self.news_df.to_csv("web_scraping.csv", index=False)
        self.last_update = date.today()
