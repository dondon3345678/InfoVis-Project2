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
from rake_nltk import Rake

en_stop = get_stop_words('en')

class Category:
    def __init__(self, name):
        self.name = name
        self.ids = set() 
        self.numberOfReviews = 0
        self.starDistribution = [0,0,0,0,0,0]
        self.pos_tokens = []
        self.neg_tokens = []
        self.pos_text = ' '
        self.neg_text = ' '
    def add_review(self, reviewText, star):
        preprocess_text = reviewText.lower().replace("\n", "")
        self.starDistribution[star] += 1
        if star >= 4:
            self.pos_text += preprocess_text
        else:
            self.neg_text += preprocess_text
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
            pprint.pprint(ldamodel.print_topics(num_topics=num_topic, num_words=10))
            print("Negative LDA")
            dictionary = corpora.Dictionary(self.neg_tokens)
            corpus = [dictionary.doc2bow(text) for text in self.neg_tokens]
            ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num_topic, id2word = dictionary, passes=20)
            pprint.pprint(ldamodel.print_topics(num_topics=num_topic, num_words=10))
    def build_rake(self):
        if len(self.pos_text) == 0 or len(self.neg_text) == 0:
            pass
        else:
            posRake = Rake()
            negRake = Rake()
            numOfPhrase = 10
            posRake.extract_keywords_from_text(self.pos_text)
            print(posRake.get_ranked_phrases()[:numOfPhrase])
            negRake.extract_keywords_from_text(self.neg_text)
            print(negRake.get_ranked_phrases()[:numOfPhrase])


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
count = 0
for k, v in category_set.iteritems():
    if sum(v.starDistribution) >= 100:
        count += 1
        print(k)
        print("Star Distribution")
        print(v.starDistribution)
        #v.build_lda(2)
        v.build_rake()

print("Count = %d" % (count))
# Writing to database
with open('category_set_rake.pk', 'wb') as handle:
    pickle.dump(category_set, handle, protocol=pickle.HIGHEST_PROTOCOL)
