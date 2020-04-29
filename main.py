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

# Implementing a chatbot to answer FAQ's and retrieve data
chat_bot = covid_data.ChatBot()

question1 = 'How does Covid19 spread?'
chat_bot.reply(question1)
# Answer
# 'through respiratory droplets produced when an infected person coughs or sneezes'

question2 = 'Can Covid19 spread from person to person?'
chat_bot.reply(question2)
# Answer
 # the virus that causes covid - 19 is thought to spread mainly from person to person , \
 # mainly through respiratory droplets produced when an infected person coughs or sneezes.\
 # these droplets can land in the mouths or noses of people who are nearby or possibly be \
 # inhaled into the lungs . spread is more likely when people are in close contact with one\
 # another ( within about 6 feet ) . the number of cases of covid - 19 being reported in \
 # the united states is rising due to increased laboratory testing and reporting across \
 # the country . the growing number of cases in part reflects the rapid spread of covid - 19\
 # as many u . s . states and territories experience community spread . more detailed and \
 # accurate data will allow us to better understand and track the size and scope of the \
 # outbreak and strengthen prevention and response efforts . the virus that causes covid - 19\
 # is spreading from person - to - person
 
question3 = 'Can I donate blood?'
chat_bot.reply(question3)
# Answer
# 'donated blood is a lifesaving , essential part of caring for patients . the need for\
#  donated blood is constant , and blood centers are open and in urgent need of donations.\
#  cdc encourages people who are well to continue to donate blood if they are able , even \
#  if they are practicing social distancing because of covid - 19 . cdc is supporting\
#  blood centers by providing [SEP]'

question4 = 'Should I wear a mask?'
chat_bot.reply(question4)
# Answer
# 'medical masks and n - 95 respirators are reserved for healthcare workers \
# and other first responders'

question7 = 'How many cases got confirmed in US yesterday?'
chat_bot.reply(question7)
# 	Province/State	Country/Region	 Lat	 Long	        Date	confirmed
# 25569	NaN	              US	    37.0902	-95.7129	2020-04-27	22412.0