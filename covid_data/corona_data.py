# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 21:18:46 2020

@author: sabareesh
"""

from posixpath import join as urljoin
from datetime import date
from datetime import timedelta 
import pandas as pd
'''
This class collects the Coronavirus time series data from the John Hopkins repository.
It collects time series data from 5 different sources for the Confirmed, Death, and Recovered cases
across the world and USA.
'''
class CoronaData:
    
    def __init__(self, url_root = (
        'https://raw.github.com/'
        'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        'csse_covid_19_time_series/time_series_covid19')):
        self.url_root = urljoin(url_root)
        
        # The last update by default is initialized to yesterday to be able to update the data atleast once.
        self.last_update = date.today() - timedelta(days=1)
        
        # Empty dataframes corresponding to global data and US data
        self.corona_global_dataset = pd.DataFrame()
        self.us_dataset = pd.DataFrame()
        
    def get_data(self, cases_type = 'confirmed', region = 'global'):
        '''
        Args: 
            cases_type can be one of the ['confirmed', 'death', 'recovered'] 
            and region can be one of ['US', 'global']. 
        output:
            a dataframe containing the results of the query.
        '''
        url = self.url_root + '_' + cases_type + '_' + region + '.csv'
        data_df = pd.read_csv(url)
        
        # USA dataset requires additional cleaning which essentially makes 
        # ensures consistency in the columns in global and US queries
        if region == 'US':
            data_df = self._further_clean(data_df)
            
        # flips the dataframe to bring all the dates as rows from columns
        data_df = data_df.melt(id_vars=['Province/State','Country/Region','Lat','Long'])
        
        # proper naming after flipping
        data_df = data_df.rename({'variable':'Date','value': cases_type}, axis='columns')
        
        # changing datatypes as required
        data_df = self._convert_data_type(data_df, column = cases_type)
        return data_df

    def get_global_data(self):
        '''
        Performs three queries and combines the data to get completed global data.
        '''
        cases_types = ['confirmed', 'deaths', 'recovered']
        data_df_list = [self.get_data(cases_type=cases_type) for cases_type in cases_types]
        
        # Combine the three queries to get complete dataset
        self.complete_data = self._combine_data(data_df_list)
        return self.complete_data
    
    def get_US_data(self):
        '''
        Performs two queries and combines the data to get completed US data.
        '''
        cases_types = ['confirmed', 'deaths']
        data_df_list = [self.get_data(cases_type=cases_type, region='US') for cases_type in cases_types]
        
        # Combine the three queries to get complete dataset
        self.complete_data = self._combine_data(data_df_list)
        return self.complete_data
    
    def update_data(self):
        '''
        gets the complete data without writing it into the csv file.
        '''
        self.corona_global_dataset = self.get_global_data()
        self.us_dataset = self.get_US_data()
    
    def update_data_csv(self, force_update = False):
        '''
        reads in the file and updates the file if not up to date.
        Args:
            force_update: If True, updates the file irrespective of the last update.
        '''
        # Checks if there is any existing file and the last updated time
        try: 
            self.corona_dataset = pd.read_csv("corona_combined_dataset.csv")
            self.last_update = self.corona_dataset['Date'].iloc[-1]
        except: pass

        # returns if there is no need to update
        if not force_update and self.last_update == date.today().strftime("%Y-%m-%d"):
            return 
        
        self.update_data()
        self.combine_US_global()
        self.corona_dataset.to_csv("corona_combined_dataset.csv", index=False)
        self.last_update = date.today()
        
    def combine_US_global(self):
        '''
        combines the global and US datasets by removing US country count 
        from global set to avoid repeating twice. 
        '''
        self.us_dataset['recovered'] = 0
        self.corona_dataset = self.corona_global_dataset[self.corona_global_dataset['Country']!='US'].append(self.us_dataset)
        
    def _combine_data(self, data_df_list):
        '''
        Combines the data obtained from two/three queries of 'confiormed', 'deaths' and 'recovered'
        to return the combined dataframe. 
        '''
        combined_df = [data_df.set_index(['Province/State','Country/Region','Lat','Long','Date']) for data_df in data_df_list]
        combined_df = combined_df[0].join(combined_df[1:])
        combined_df=combined_df.reset_index()
        combined_df=combined_df.rename({'Province/State':'State','Country/Region': 'Country'}, axis='columns')
        return combined_df
    
    def _convert_data_type(self, data_df, column):
        '''
        Performs necessary datatype changes.
        '''
        data_df[['Lat', 'Long']] = \
        data_df[['Lat', 'Long']].apply(pd.to_numeric)
        data_df[column] = pd.to_numeric(data_df[column], downcast='integer')
        data_df[['Date']] = data_df[['Date']].apply(pd.to_datetime)
        return data_df
    
    def _further_clean(self, data_df):
        '''
        dropping unnecessary columns from the US dataset.
        '''
        data_df.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region'], axis=1, inplace=True)
        try: data_df.drop(['Population'], axis=1, inplace=True)
        except: pass
        data_df = data_df.rename({'Province_State':'Province/State', 'Long_': 'Long'}, axis='columns')
        data_df = data_df.groupby(['Province/State'])[['Lat', 'Long']].agg('mean')\
                .join(data_df.drop(['Lat', 'Long'], axis=1).groupby(['Province/State']).agg('sum'))
        data_df = data_df.reset_index()
        data_df['Country/Region'] = 'US'
        return data_df
