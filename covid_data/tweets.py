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

'''
This class collects the latest tweets relating to coronavirus.
'''
class TwitterTraffic:
    
    def __init__(self, config_file = 'config.cfg'):
        '''
        authentication to login and extract tweets.
        '''
        self.config_file = config_file
        self._get_API()
        try: 
            self.tweets_df = pd.read_csv("tweets.csv")
            self.last_update = self.tweets_df['date'].iloc[-1]
        except: 
            self.last_update = date.today() - timedelta(days=1)
            self.tweets_df = pd.DataFrame()
        
    def get_todays_tweets(self, search_words = ["#coronavirus", "#COVID19"], num=1000):
        '''
        returns todays tweets as a dataframe in raw format.
        Args:
            search_words: search criteria as a list.
            num: number of tweets that need to be extracted (limit of roughly 15000 per 15 minutes)
        '''
        tweets = tw.Cursor(self.api.search,
              q=search_words,
              lang="en",
              since=date.today().strftime("%Y-%m-%d")).items(num)

        # List of lists containing the text and details of the tweet.
        tweets_list = [[tweet.text, tweet.user.screen_name, date.today()] for tweet in tweets]
        uncleaned_tweets_df = pd.DataFrame(data=tweets_list, columns=['text', 'user', 'date'])
        return uncleaned_tweets_df
    
    def update_tweets_data(self):
        '''
        Gets celaned version of todays tweets and append to the existing dataframe.
        '''
        uncleaned_tweets_df = self.get_todays_tweets()
        self.tweets_df = self.tweets_df.append(self._process(uncleaned_tweets_df))
                
    def update_tweets_CSV(self, force_update = False):        
        '''
        Updates the file if not up to date.
        Args:
            force_update: If True, updates the file irrespective of the last update.
        '''
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
            return 
        
        self.update_tweets_data(force_update)
        self.tweets_df.to_csv("tweets.csv", index=False)
        
    def _get_API(self):
        '''
        Authentication to be able to extract tweets.
        '''
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
        '''
        Takes in the uncleaned DataFrame and returns the cleaned DataFrame.
        Returns the necessary subset of the processes DataFrame.
        '''
        cleaned_tweets_df = self._clean(uncleaned_tweets_df)
        processed_tweets_df = self._extract_features(cleaned_tweets_df)
        return processed_tweets_df[['date', 'user', 'text', 'entities', 'sentiment']]
        
    def _clean(self, uncleaned_tweets_df):
        '''
        Performs cleaning of the tweets to perform better sentiment analysis.
        '''
        # Removes any hyperlinks
        uncleaned_tweets_df['text'] = uncleaned_tweets_df['text'].\
                                str.replace('http\S+|www.\S+', '', case=False)
        # Removes usernames, retweets and next line characters from the tweet
        uncleaned_tweets_df['text'] = uncleaned_tweets_df['text'].apply(lambda x:\
                                                                self._clean_tweets(x))
        # Removes any special characters
        uncleaned_tweets_df['cleaned'] = uncleaned_tweets_df['text'].map(lambda x:\
                                                                re.sub(r'\W+', ' ', x))
        # Tokenize the tweet
        uncleaned_tweets_df['cleaned'] = [word_tokenize(i) for i in \
                                          uncleaned_tweets_df['cleaned']]
        stop =stopwords.words('english')
        # Removes stopwords
        uncleaned_tweets_df['cleaned'] = uncleaned_tweets_df['cleaned'].apply(lambda x: \
                                        ' '.join([item for item in x if item not in stop]))
        return uncleaned_tweets_df
    
    def _extract_features(self, cleaned_tweets_df):
        # Extract entities
        cleaned_tweets_df['entities'] = cleaned_tweets_df['cleaned'].apply(lambda x: [(ent.text, ent.label_)\
                                            if (not ent.text.startswith('#')) else "" for ent in nlp(x).ents])
        sid = SentimentIntensityAnalyzer()
        # Estimate the sentiment
        cleaned_tweets_df['sentiment'] = cleaned_tweets_df['cleaned'].apply(lambda x: sid.polarity_scores(x))
        return cleaned_tweets_df
    
    def _clean_tweets(self, text):
        text = re.sub("RT @[\w]*:","",text)
        text = re.sub("@[\w]*","",text)
        text = re.sub("\n","",text)
        return text
