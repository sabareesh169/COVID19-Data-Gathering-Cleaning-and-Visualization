# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 21:02:25 2020

@author: sabareesh
"""

import configparser
import tweepy as tw
from tweepy import OAuthHandler
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from datetime import date
from datetime import timedelta 
import pandas as pd

import en_core_web_sm
nlp = en_core_web_sm.load()

class TwitterTraffic:
    
    def __init__(self, config_file = 'config.cfg'):
        self.config_file = config_file
        self._get_API()
        self.last_update = date.today() - timedelta(days=1)
        self.tweets_df = pd.DataFrame()
        
    def get_todays_tweets(self, search_words = ["#coronavirus", "#COVID19"], num=1000):
        tweets = tw.Cursor(self.api.search,
              q=search_words,
              lang="en",
              since=date.today().strftime("%Y-%m-%d")).items(num)

        tweets_list = [[tweet.text, tweet.user.screen_name, date.today()] for tweet in tweets]
        uncleaned_tweets_df = pd.DataFrame(data=tweets_list, columns=['text', 'user', 'date'])
        return uncleaned_tweets_df
    
    def update_tweets_data(self, force_update = False):
        
        if not force_update and self.last_update == date.today():
            return self.tweets_df
        
        uncleaned_tweets_df = self.get_todays_tweets()
        self.tweets_df = self.tweets_df.append(self._process(uncleaned_tweets_df))
        self.last_update = date.today()
                
    def update_tweets_CSV(self, force_update = False):
        try: 
            self.tweets_df = pd.read_csv("tweets.csv")
            self.last_update = self.tweets_df['date'].iloc[-1]
        except: pass
        
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
            return 
        
        self.update_tweets_data(force_update)
        self.tweets_df.to_csv("tweets.csv", index=False)
        
    def _get_API(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)

        accesstoken=config.get('twitter', 'access_token')
        accesstokensecret=config.get('twitter', 'access_token_secret')
        apikey=config.get('twitter', 'consumer_key')
        apisecretkey=config.get('twitter', 'consumer_secret')

        auth = tw.OAuthHandler(apikey, apisecretkey)
        auth.set_access_token(accesstoken, accesstokensecret)
        self.api = tw.API(auth, wait_on_rate_limit=True)
        
    def _process(self, uncleaned_tweets_df):
        cleaned_tweets_df = self._clean(uncleaned_tweets_df)
        processed_tweets_df = self._extract_features(cleaned_tweets_df)
        return processed_tweets_df[['date', 'user', 'text', 'entities', 'sentiment']]
        
    def _clean(self, uncleaned_tweets_df):
        uncleaned_tweets_df['text'] = uncleaned_tweets_df['text'].\
                                str.replace('http\S+|www.\S+', '', case=False)
        uncleaned_tweets_df['text'] = uncleaned_tweets_df['text'].apply(lambda x:\
                                                                self._clean_tweets(x))
        uncleaned_tweets_df['cleaned'] = uncleaned_tweets_df['text'].map(lambda x:\
                                                                re.sub(r'\W+', ' ', x))
        uncleaned_tweets_df['cleaned'] = [word_tokenize(i) for i in \
                                          uncleaned_tweets_df['cleaned']]
        stop =stopwords.words('english')
        uncleaned_tweets_df['cleaned'] = uncleaned_tweets_df['cleaned'].apply(lambda x: \
                                        ' '.join([item for item in x if item not in stop]))
        return uncleaned_tweets_df
    
    def _extract_features(self, cleaned_tweets_df):
        cleaned_tweets_df['entities'] = cleaned_tweets_df['cleaned'].apply(lambda x: [(ent.text, ent.label_)\
                                            if (not ent.text.startswith('#')) else "" for ent in nlp(x).ents])
        sid = SentimentIntensityAnalyzer()
        cleaned_tweets_df['sentiment'] = cleaned_tweets_df['cleaned'].apply(lambda x: sid.polarity_scores(x))
        return cleaned_tweets_df
    
    def _clean_tweets(self, text):
        text = re.sub("RT @[\w]*:","",text)
        text = re.sub("@[\w]*","",text)
        text = re.sub("\n","",text)
        return text