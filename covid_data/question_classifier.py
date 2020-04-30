# -*- coding: utf-8 -*-
"""
@author: sabareesh
"""


from bs4 import BeautifulSoup
import requests
from transformers import BertTokenizer
import unicodedata
import torch
import numpy as np
from transformers import BertForSequenceClassification, AdamW
from torch.utils.data import TensorDataset, DataLoader, RandomSampler

import os
import pandas as pd

'''
This class scraps Frequently asked questinos from the CDC website. It also scraps 
information about the virus and tries to answer questions based on the information
available. To make this task easier, I divided the questions into 15 major classes.
Each class corresponds to one topic with 1 question corresponding to the statistics
of the confirmed cases and deaths. This I retrieve from the dataset I gathered. 
'''

class QuestionClassifier(object):
  def __init__(self):
    '''
      Load a pretrained tokenizer from Bert.
      All the faqs are scraped from the cdc website.
      Returns
      -------
      None.

    '''
    self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    self.url = 'https://www.cdc.gov/coronavirus/2019-ncov/faq.html'
    self.format = 'html.parser'
    self.make_data()

  def attach_additional_questions(self, questions_list:list):
    '''

      Parameters
      ----------
      questions_list : list
          List of possible questions(training data for retrieving 
          data from table.
      Returns
      -------
      questions_list : list
          list of questions with a label attached to them (0 in this case).

    '''
    fabricated_questions = ['what are the number of cases in US yesterday?', \
                            'How many confirmed cases were recorded over the entire world yesterday?',\
                            'What are the number of deaths in China on 24th January?',\
                            'How many died on 30th March in Italy?', \
                            "What's the number of confirmed corona cases in India on 4th April?",\
                            "How many people were affected by COVID19 in Mexico on 15th April?"\
                            "What's the total cases in United States on 25th Feb?", \
                            "What is the total number of cases in United States?",\
                            "What's the net increase in confirmed cases worlwide yesterday?", \
                            "How many people died on 12th April in Australia?"]
    
    for question in fabricated_questions:
      questions_list.append([question, 0])
    
    return questions_list

  def extract_questions(self):
    '''
      Data mining questions from the CDC website. And label them accordingly.
      Returns
      -------
      questions_list : list

    '''
    response = requests.get(self.url)
    soup = BeautifulSoup(response.content, self.format)
    label = 0
    questions_list = []
    # Extract questions from the website
    # Go through all the tags, if you find the 'h3' tag, then a new set of 
    # questoins have started, so start a new label.
    for tag in soup.find_all():
      if tag.name=='h3':
        label+=1
    
      # If the tag is span and text xontains '?', then add the text as question.
      if tag.name=='span' and '?' in tag.text:
        questions_list.append([tag.text, label]) 
        
    # Augment the data with the training set for stats query questions
    questions_list = self.attach_additional_questions(questions_list)
    return questions_list

  def extract_answers(self):
    '''
      Data mining information from the CDC website. And label them accordingly.

      Returns
      -------
      answers_list : list
    '''
    response = requests.get(self.url)
    soup = BeautifulSoup(response.content, self.format)
    answer_text = ' '
    label = 0
    answers_list = []
    next_answer = False
    # Extract questions from the website
    for tag in soup.find_all():
    
      # Everytime you encounter new category, join the answer text and label
      if tag.name=='h3':
        answers_list.append([answer_text, label])
        answer_text = ''
        label+=1
        
      # Collect only 1 paragraph answer to keep the answer tkens to less than 512
      if tag.name=='span' and '?' in tag.text:
        next_answer = True
      if tag.name=='p' and len(tag.text.split(" ")) > 4 and next_answer==True:
        answer_text+=' '+str(unicodedata.normalize('NFKD',tag.text))
        next_answer = False
        
      # tag 'h4' correponds to footnotes
      if tag.name=='h4':
        break
    answers_list.append([answer_text, label])

    return answers_list

  def make_data(self):
    '''
      Calls the required functions to gather data.
      Performs shuffling as well.
    '''
    self.questions_df = pd.DataFrame.from_records(self.extract_questions(), \
                                                  columns=['query', 'label']).sample(frac=1)
    self.answers_df = pd.DataFrame.from_records(self.extract_answers(), columns=['answer_text', 'label'])
    self.answers_df = self.answers_df.set_index('label')

  def tokenize_data(self, x : str, y=None, max_length=None):
    '''

      Parameters
      ----------
      x : string
          question or the first sentence.
      y : string, optional
          answer or the second sentence. The default is None.
      max_length : int, optional
          default value is the maximum length encountered. The default is None.

      Returns
      -------
      input_ids : list
          padded list of tokens.
      tokens : list
          words converted to tokens.

    '''
    input_ids = self.tokenizer.encode(x, y, max_length=max_length, pad_to_max_length=True)
    tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
    return input_ids, tokens
    
  def fit(self):
    '''
      Finetunes the model parameters for the training set.
      Returns
      -------
      None.

    '''
    train_labels = torch.tensor(self.questions_df['label'])
    input_ids = self.questions_df['query'].apply(lambda x: \
                                    self.tokenizer.encode(x, max_length = 20, pad_to_max_length=True))

    train_masks = torch.tensor([[int(token_id > 0) for token_id in input_id] for input_id in \
                   input_ids])
    train_inputs = torch.tensor(input_ids)

    batch_size = 32

    # Create the DataLoader for our training set.
    train_data = TensorDataset(train_inputs, train_masks, train_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

    self.model = BertForSequenceClassification.from_pretrained(
    'bert-large-uncased-whole-word-masking-finetuned-squad', 
    num_labels = 16, 
    output_attentions = False, output_hidden_states = False)
    self.perform_training(train_dataloader)

  def perform_training(self, train_dataloader:iter):
    '''
      Parameters
      ----------
      train_dataloader : iter
          A pytorch iterable to loop over the training set and masks.

      Optimizes the model parameters

    '''
    epochs = 12
    optimizer = AdamW(self.model.parameters(), lr = 3e-5)

    for epoch_i in range(0, epochs):

      print('Training Epoch {:} / {:}'.format(epoch_i + 1, epochs))
      self.model.train()

      # Reset the total loss for this epoch.
      total_loss = 0

      # For each batch of training data...
      for step, batch in enumerate(train_dataloader):

        self.model.zero_grad()        
        outputs = self.model(batch[0], 
                    token_type_ids=None, 
                    attention_mask=batch[1], 
                    labels=batch[2])
        
        loss = outputs[0]
        total_loss += loss.item()

        # Perform a backward pass to calculate the gradients.
        loss.backward()

        #Clipping gradients to 1.0 to avoid explosion of gradients
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

        # Update parameters 
        optimizer.step()
      print("Average training loss: {0:.2f}".format(total_loss / len(train_dataloader)))
    
    # Save the model to a directory
    output_dir = './model/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    self.model.save_pretrained('./model/')
    self.tokenizer.save_pretrained('./model/')

  def classify(self, query:str):
    '''
      Parameters
      ----------
      query : str
          Query or question to be classified.

      Returns
      -------
      Predicted class label.
    '''
    # Check if the model exists already, if not try to load or train
    try:
      self.model
    except:
      # Try to load the model
      try:
        self.model = BertForSequenceClassification.from_pretrained('./model/')
        self.tokenizer = BertTokenizer.from_pretrained('./model/')
      # or load and train the model
      except:
        self.fit()

    # forward pass only
    self.model.eval()

    inputs = self.tokenizer.encode(query, max_length=20, pad_to_max_length=True)
    # specify the padding if any
    masks = [int(token_id > 0) for token_id in inputs]

    with torch.no_grad():        
        outputs = self.model(torch.tensor([inputs]), 
                        token_type_ids=None, 
                        attention_mask=torch.tensor([masks]))
        
    logits = outputs[0]
    
    # Reurn the most probable class
    return np.argmax(logits.numpy(), axis=1).flatten()
