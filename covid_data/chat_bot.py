# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:57:13 2020

@author: sabareesh
"""

from question_classifier import QuestionClassifier 
from question_answer import QuestionAnswer 
from corona_data import CoronaData
import en_core_web_sm
nlp = en_core_web_sm.load()
import datetime 
import pandas as pd

class ChatBot(object):
  def __init__(self, corona_data=None):
    '''
      Parameters
      ----------
      corona_data : class instance
          The object responsible to mine data from github repositories.
          The default is None.
    '''
    self.qc = QuestionClassifier()
    if corona_data == None:
      self.corona_data = CoronaData()
    else: self.corona_data = corona_data 
  
  def reply(self, query:str):
    '''
      Parameters
      ----------
      query : str
          question or query asked.

      Returns
      -------
      answer : str or pd.DataFrame
          returns either one of above based on the query.
    '''
    label = int(self.qc.classify(query))
    if label>0:
      try:
        answer = self.qa.answer_query(query, label)
      except:
        self.qa = QuestionAnswer(self.qc)
        answer = self.qa.answer_query(query, label)
    else:
      country, cases_type, date = self.get_details(query)
      answer = self.corona_data.get_specific_data(country, cases_type, date)
    return answer

  def get_details(self, query:str):
    '''
      Parameters
      ----------
      query : str
          question or query corresponding to label 0.

      Returns
      -------
      country : str
          country name or 'All' in case name is missing.
      cases_type : str
          confirmed or death. We assume confirmed cases if not specified.
      req_date : datetime 
          date. We assume cumulative data in case date is not mentioned.
    '''
    entities = [ent.text for ent in nlp(query).ents]
    if 'DATE' in [ent.label_ for ent in nlp(query).ents]:
      time_entity = [ent.text for ent in nlp(query).ents if ent.label_ in 'DATE'][0] 
      if 'yesterday' in entities:
        req_date = datetime.date.today() - datetime.timedelta(days=1)
      elif 'today' in entities:
        req_date = datetime.date.today()
      else:
        try:
          req_date = pd.to_datetime(time_entity)
        except:
          req_date = pd.to_datetime(time_entity+'2020')
      req_date = req_date.strftime("%Y-%m-%d")
    else: req_date = 'All'

    if 'GPE' in [ent.label_ for ent in nlp(query).ents]:
      country = [ent.text for ent in nlp(query).ents if ent.label_ in 'GPE'][0]
    else: country = 'All'

    if 'death' in query or 'died' in query:
      cases_type = 'deaths'
    else: cases_type = 'confirmed'

    return country, cases_type, req_date
  