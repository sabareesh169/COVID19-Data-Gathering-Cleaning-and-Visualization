# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:40:52 2020

@author: sabareesh
"""

from transformers import BertTokenizer
import torch
from transformers import BertForQuestionAnswering

'''
This classes attempts to answer the question from the corresponding information as
well as query from the coronavirus dataset in case the label is 0.
'''

class QuestionAnswer(object):
  def __init__(self, question_classifier:object):
    '''
      Parameters
      ----------
      question_classifier : Class instance
          required to know the informatino corresponding to the label.
      
      Downloads the pretrained BERT model and encoder.
    '''
    self.model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    self.answers_df = question_classifier.answers_df
    self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

  def tokenize(self, query:str, label:int):
    '''
      Parameters
      ----------
      query : str
          question to be tokenized and masks.
      label : int
          predicted class of the question.

      Returns
      -------
      input_ids : list
          tokens of questions and corresponding information.
      segment_ids : TYPE
          masks corresponding to the tokens.
    '''
    input_ids = self.tokenizer.encode(query, self.answers_df.answer_text.loc[label], max_length=512, pad_to_max_length=True)
    self.tokens = self.tokenizer.convert_ids_to_tokens(input_ids)

    # Search the input_ids for the first instance of the `[SEP]` token.
    sep_index = input_ids.index(self.tokenizer.sep_token_id)

    # The number of segment A tokens includes the [SEP] token istelf.
    num_seg_a = sep_index + 1

    # The remainder are segment B.
    num_seg_b = len(input_ids) - num_seg_a

    # Construct the list of 0s and 1s.
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    return input_ids, segment_ids

  def answer_query(self, query:str, label:int):
    '''
      Parameters
      ----------
      query : str
          question to be tokenized and masks.
      label : int
          predicted class of the question.

      Returns
      -------
      answer : str 
          Required/predicted answer to the question.

      '''
    input_ids, segment_ids = self.tokenize(query, label)
    start_scores, end_scores = self.model(torch.tensor([input_ids]), # The tokens representing our input text.
                                  token_type_ids=torch.tensor([segment_ids]))
    start_token = torch.argmax(start_scores)
    end_token = torch.argmax(end_scores)
    answer = self.get_answer(start_token, end_token)
    return answer

  def get_answer(self, start_token:int, end_token:int):
    '''
      Parameters
      ----------
      start_token : int
          most probable start word of the answer.
      end_token : int
          most probable end word of the answer.

      Returns
      -------
      answer : str
          Performs any cleaning necessary and returns the string.
      '''
    # Start with the first token.
    answer = self.tokens[start_token]

    # Select the remaining answer tokens and join them with whitespace.
    for i in range(start_token + 1, end_token + 1):
        
        # If it's a subword token, then recombine it with the previous token.
        if self.tokens[i][0:2] == '##':
            answer += self.tokens[i][2:]
        
        # Otherwise, add a space then the token.
        else:
            answer += ' ' + self.tokens[i]
    return answer