
# coding: utf-8

# In[130]:

import sys
import re
import os
import nltk
from nltk.corpus import stopwords, words
from nltk.corpus import wordnet as wn

import pandas as pd
import numpy as np

import matplotlib
#matplotlib.style.use('ggplot')

import matplotlib.pyplot as plt
#get_ipython().magic(u'matplotlib inline')


# In[2]:

# Create sentiment dictionary from AFINN-111 list (free online)
sentiment_dict = {}
for line in open('AFINN/AFINN-111.txt'):
    word, score = line.split('\t')
    sentiment_dict[word] = int(score)


# In[73]:

dates = ['01-15', '02-06', '03-15', '12-15']


# ### Initialize file list and dictionaries

# In[7]:

files = ['transcript01-15.txt', 'transcript02-06.txt', 'transcript03-15.txt', 'transcript12-15.txt']
statements = {}
transcripts = ['transcripts/' + f for f in files]
names = {}


# In[8]:

moderators = {'02-06':['MUIR'], '01-15':['CAVUTO', 'BARTIROMO'], '12-15':['BLITZER'], '03-15':['TAPPER']}


# Names are extracted using regex.
# 
# Transcript speaker format is assumed to be
# > SPEAKER: statement

# In[9]:

name = re.compile(r'([A-Z]+)\:')


# In[10]:

for t in transcripts:
    with open(t, 'r') as fh:
        for n in re.findall(name, fh.read()):
            if n not in names.keys():
                names[n] = {}


# ### Parse transcripts
# 
# Statements are stored in a list of tuples containing the statement number and statement string.
# 
# They are then split and stored by speaker and file names in the same format.

# In[11]:

debate_pos = {}
j = 0
for t in files:
    t_name = t[-9:-4]
    statements[t_name] = []
    with open('transcripts/' + t, 'r') as fh:
        or_names = '|'.join(names.keys())
        pattern = re.compile(r"({0})(.+\n)|(\n)(.+)(\n)".format(or_names))

        for statement in re.findall(pattern, fh.read()):
            statements[t_name].append((j,''.join([s for s in statement if s not in ['', '\n', '(APPLAUSE)']])))
            j+=1
        debate_pos[t_name] = j


# In[80]:

current_speaker = ''
for key in dates:
    for n in names.keys():
        names[n][key] = []
    for state in statements[key]:
        if len(state[1]) < 1:
            continue
        statement = state[1]
        if statement.split(':')[0] in names.keys():
            current_speaker = statement.split(':')[0]
            names[current_speaker][key].append((state[0],statement.split(':')[1]))
        elif current_speaker in names.keys():
            names[current_speaker][key].append((state[0],statement))


# ### Statement parsing
# 
# Create a statement dictionary containing the speaker names.
# The speaker names hold a second set of dictionaries with a 2D list of statements and the words in those statements.
# 
# All words are lowercase, and stopwords are ignored.

# In[233]:

statement_dict = {}
for n in names.keys():
    statement_dict[n] = {}
    for t in files:
        t_name = t[-9:-4]
        statement_dict[n][t_name] = []
        for line in names[n][t_name]:
            st = re.sub(r'(\xe2\x80\x99)',r"'",line[1].lower().strip('\n'))
            #st = line[1].lower().strip('\n').decode('utf-8')

            if st != '' and len(st) > 0:
                statement_dict[n][t_name].append((line[0],st))
        if len(statement_dict[n][t_name]) == 0:
            del statement_dict[n][t_name]


# ### Get sentiment scores
# 
# Sentiment is scored from AFINN-111.
# They are formated in lists of length 2 (`[pos, neg]`)

# ## Create data frame with statement
# ### Columns:
# - Statement_Num: Position number of statement in transcripts
# - Statement: Statement string
# - Word_Count: Number of words in statement
# - Setiment: Sentiment score calculated above
#  * Sentiment is scored from AFINN-111.
#  * They are formated in lists of length 2 (`[pos, neg]`)
# - Sentence_Count: Number of sentences in statement
# - Question (obtained from add_questions function): Most recent question asked by a moderator
#  * Format: 
#   > [Statement Number] [Moderator] [Question]

# In[241]:

def get_speaker_df(speaker, date_list=dates):
    statement_list = []
    for d in date_list:
        statement_list += [s for s in statement_dict[speaker][d]]
    scores = {}
    scores[speaker] = []
    sentence_count = []
    word_count = []
    t_scores = []
    df = pd.DataFrame()
    
    df['Statement_Num'] = [s[0] for s in statement_list]
    df['Statement'] = [s[1].decode('utf-8') for s in statement_list]

    for statement in df['Statement'].values:
        sentences = nltk.tokenize.sent_tokenize(statement)
        sentence_count.append(len(sentences))
        wc = 0
        s_scores = []
        for sentence in sentences:
            words = nltk.tokenize.word_tokenize(sentence) 
            pos,neg=0,0
            for word in words:
                score = sentiment_dict.get(word,0)
                if score > 0:
                    pos += score
                if score < 0:
                    neg += score
            s_scores.append([pos,neg])
            wc += len(words)
        word_count.append(wc)
        t_scores.append(sum(sum(s) for s in s_scores))
    
    df['Word_count'] = word_count
    df['Sentiment'] = t_scores
    df['Sentence_Count'] = sentence_count
    
    return df


# In[237]:

def add_questions(df):
    question_list = []
    for d in dates:
        for mod in moderators[d]:
            question_list += [(n, mod, s.decode('utf-8')) for n,s in statement_dict[mod][d]]
    questions = []
    for value in df['Statement_Num']:
        for q in range(len(question_list)):
            if question_list[q][0] < value and question_list[q+1][0] > value:
                questions.append(str(question_list[q][0]) + ' ' +question_list[q][1] +' '+ question_list[q][2])
                break
                
    df['Question'] = questions


# In[242]:

trump = get_speaker_df('TRUMP')#.sort('Statement_Num')
add_questions(trump)


# In[239]:

print trump.head()


# ## To do:
# 
# 1. Use NLTK to contextualize statements.
#  * Find key words and topics
# 2. Use scikit-learn to analyze speaker attitudes towards key words and topics

# In[ ]:
