"""
Created on Sun Apr  5 21:31:31 2020

@author: sabareesh
"""

# covid_data contains the modules to gather and clean corona virus data, news and tweets related to corona virus
import covid_data

news = covid_data.News()
# If there is no existing file, gets the news from today from 3 different websites and
# writes to a new file created. 
# If there is an existing file, checks whether todays news has been gathered.
# If already gathered, then no action is performed (essentially allows only scraping once per day unless 'force_update' is set to True)
news.update_news_CSV()

# Returns a dictionary of headlines on todays website irrespective of whether the news is scraped already or not. 
print(news.today_news_dict())

tweets = covid_data.TwitterTraffic()
# If there is no existing file, a new file is created with tweets from today,
# containing the terms '#COVID19' or '#coronavirus'
# If there is an existing file, it first checks the day of the last update time and 
# updates only if todays tweets has not been collected yet.
# (allows only collecting once per day unless 'force_update' is set to True)
tweets.update_tweets_CSV()

# Returns a dataframe of todays tweets irrespective of whether the tweets have been collected or not. 
print(tweets.get_todays_tweets())

corona_data = covid_data.CoronaData()
# If there is no existing file, a new file is created with data until today,
# If there is an existing file, it first checks the day of the last update time and 
# updates only if latest records has not been collected yet.
# (allows only updating once per day unless 'force_update' is set to True)
corona_data.update_data_csv()

# prints out the data according to the query.
print(corona_data.get_data(region='US', cases_type= 'deaths'))
