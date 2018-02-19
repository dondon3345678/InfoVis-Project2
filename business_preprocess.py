import json
import pprint
import nltk
import math
import string
import re
import pickle
import os
import sys

from rake_nltk import Rake
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob
from stop_words import get_stop_words
from gensim import corpora, models

en_stop = get_stop_words('en')

class Category:
    def __init__(self, name):
        self.name = name
        self.ids = set() 
        self.numberOfReviews = 0
        self.starDistribution = [0,0,0,0,0,0]
        self.pos_tokens = []
        self.posLDA = None
        self.neg_tokens = []
        self.negLDA = None
    def add_review(self, reviewText, star):
        preprocess_text = reviewText.lower().replace("\n", "")
        self.starDistribution[star] += 1
        paragraph = TextBlob(preprocess_text)
        tokens = [word for word, tag in paragraph.tags if "NN" in tag or "JJ" in tag]
        final_tokens = [t for t in tokens if len(t) > 1 and not t in en_stop]
        if star >= 4:
            self.pos_tokens.append(final_tokens)
        else:
            self.neg_tokens.append(final_tokens)
    def add_bussinessID(self, bussinessID):
        ids.add(businessID)
    def build_lda(self, num_topic):
        if len(self.pos_tokens) == 0 or len(self.neg_tokens) == 0:
            pass
        else:
            print("Postive LDA")
            dictionary = corpora.Dictionary(self.pos_tokens)
            corpus = [dictionary.doc2bow(text) for text in self.pos_tokens]
            ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num_topic, id2word = dictionary, passes=20)
            self.posLDA = ldamodel.show_topics(num_topics=num_topic, num_words=10, formatted=False) 
            pprint.pprint(self.posLDA)
            print("Negative LDA")
            dictionary = corpora.Dictionary(self.neg_tokens)
            corpus = [dictionary.doc2bow(text) for text in self.neg_tokens]
            ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num_topic, id2word = dictionary, passes=20)
            self.negLDA = ldamodel.show_topics(num_topics=num_topic, num_words=10, formatted=False)
            pprint.pprint(self.negLDA)

category_dict = {}
category_set = {}
if os.path.isfile("./category_dict.pk") and os.path.isfile("./category_set.pk"):
    with open('./category_dict.pk', 'rb') as handle:
        category_dict = pickle.load(handle)
    with open('./category_set.pk', 'rb') as handle:
        category_set = pickle.load(handle)
else:
    with open('./dataset/business.json', 'r') as f:
        for line in f.readlines():
            line_json = json.loads(line)
            categories = line_json['categories']
            business_id = line_json['business_id']
            if business_id not in category_dict:
                category_dict[business_id] = [c for c in categories]
            for c in category_dict[business_id]:
                if c not in category_set:
                    category_set[c] = Category(c) 
    with open('category_dict.pk', 'wb') as handle:
        pickle.dump(category_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('category_set.pk', 'wb') as handle:
        pickle.dump(category_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("%d categories processed" % (len(category_set)))

LIMIT = 100000

with open('./dataset/review.json', 'r') as f:
    for i, line in enumerate(f.readlines()):
        line_json = json.loads(line)
        b_id = line_json['business_id']
        #tokens = tokenizer.tokenize(line_json['text'].lower())
        #stopped_tokens = [t for t in tokens if not t in en_stop]
        #final_tokens = [t for t in stopped_tokens if len(t) > 1]
        star = int(line_json['stars'])
        sys.stdout.write("\rLine %d" % (i+1))
        sys.stdout.flush()
        if i == LIMIT:
            break
        for c in category_dict[b_id]:
            category_set[c].add_review(line_json['text'], star)
            category_set[c].numberOfReviews += 1

category_count = [(v.name, v.numberOfReviews) for k, v in category_set.iteritems()]
category_count = sorted(category_count, key=lambda x: x[1], reverse=True)

data = []

cnt = 0
for x in category_count:
    temp_dict = {}
    c = category_set[x[0]]
    if len(c.pos_tokens) == 0 or len(c.neg_tokens) == 0:
        continue
    cnt +=1
    if cnt > 20:
        break
    print("Category Name:")
    print(c.name)
    print("Star Distribution")
    print(c.starDistribution)
    temp_dict['star'] = c.starDistribution
    c.build_lda(2)
    temp_dict['reviews'] = c.numberOfReviews
    temp_dict['postive'] =  dict([(i[0], int(100000*i[1])) for i in c.posLDA[0][1]])
    temp_dict['negative'] = dict([(i[0], int(100000*i[1])) for i in c.negLDA[0][1]])
    temp_dict['name'] = c.name
    data.append(temp_dict)

print("Writing to data.json")
with open('data.json', 'w') as f:
    json.dump(data, f)




# Writing to database
with open('category_set_complete.pk', 'wb') as handle:
    pickle.dump(category_set, handle, protocol=pickle.HIGHEST_PROTOCOL)
