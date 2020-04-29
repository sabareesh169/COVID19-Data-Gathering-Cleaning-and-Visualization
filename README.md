# COVID19-Data-Gathering-Cleaning-and-Visualization

https://public.tableau.com/profile/sabareesh.mamidipaka#!/vizhome/COVIDdashboard_15860596712740/Dashboard1?publish=yes

The objective of the program is to get latest information regarding the coronavirus including the data, news and tweets by running the command once. I also created a chatbot to answer questions about Coronavirus and perform queries from text.

![image](https://user-images.githubusercontent.com/25951391/80550709-cbb46e80-8975-11ea-8192-1838f58bbbed.png)
![image](https://user-images.githubusercontent.com/25951391/80550770-00282a80-8976-11ea-9c6b-463e2b941786.png)
![image](https://user-images.githubusercontent.com/25951391/80550649-99a30c80-8975-11ea-8fb2-f5dc0ac9da37.png)

The 'corona_data.py' contains the CoronaData class which takes data from the Johns Hopkins(https://github.com/CSSEGISandData/COVID-19) data repository. The file takesin data from 5 different files containing the data in the form of train series. This combined data is cleaned and aggregated. Depending on the queries, you can get cases for death, recovered and confirmed either over US or over the entire world. We can also get the details for a select country on a select day for a specific case type.

The 'news.py' file contains the News class which scrapes headlines from three sprecific websites. We can also add additional websites using the 'add_URL' method. By adding all the headlines and filtering out repeated data, we get the time of the postings as well. There are mwthods to get todays news, or the entire news or just update the file. The file also contains the list of entities extrated from each headline in case we like to talk about the specific topic the headlines are about.

The 'tweets.py' file contains the TwitterTraffic class which collects todays tweets on the coronavirus topic. Additional cleaning,  sentiment analysis and extraction of entities from tweets was performed.

All this data gathered and scraped was used to make the following dashboard:
https://public.tableau.com/profile/sabareesh.mamidipaka#!/vizhome/COVIDdashboard_15860596712740/Dashboard1?publish=yes

