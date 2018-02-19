import json
import pprint
import nltk
import math
import string
import re

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

tokenizer = RegexpTokenizer(r'\w+')
p_stemmer = PorterStemmer()
postive = []
posText = ""
negative = []
negText = ""
en_stop = get_stop_words('en')

with open('./dataset/review.json', 'r') as f:
    for i, line in enumerate(f.readlines()):
        line_json = json.loads(line)
        posText += line_json['text'].lower()
        
        
        #sentence = TextBlob(line_json['text'].lower())
        #tokens = [word for word, tag in sentence.tags if "NN" in tag or "JJ" in tag]
        #final_tokens = [t for t in tokens if len(t) > 1 and not t in en_stop]
        #final_tokens = [p_stemmer.stem(t) for t in stopped_tokens]
        #print(final_tokens)
        star = int(line_json['stars'])
        #print(i+1)
        if star >=4:
            posText += line_json['text'].lower().replace("\n","")
            #postive.append(final_tokens)
        else:
            negText += line_json['text'].lower().replace("\n","")
            #negative.append(final_tokens)
        if i == 100:
            break

posRake = Rake()
negRake = Rake()

posRake.extract_keywords_from_text(posText)
print(posRake.get_ranked_phrases())
negRake.extract_keywords_from_text(negText)
print(negRake.get_ranked_phrases())



"""
NUM_TOPIC = 3

print("building postive model")
#postive
dictionary_pos = corpora.Dictionary(postive)
corpus_pos = [dictionary_pos.doc2bow(text) for text in postive]
postive_model = models.ldamulticore.LdaMulticore(corpus_pos, num_topics=NUM_TOPIC, id2word = dictionary_pos, passes=20, workers=3)
pprint.pprint(postive_model.print_topics(num_topics=NUM_TOPIC, num_words=15))
postive_model.save("LDA_Postive_100000")

print("building negative model")
#postive
dictionary_neg = corpora.Dictionary(negative)
corpus_neg = [dictionary_neg.doc2bow(text) for text in negative]
negative_model = models.ldamulticore.LdaMulticore(corpus_neg, num_topics=NUM_TOPIC, id2word = dictionary_neg, passes=20, workers=3)
pprint.pprint(negative_model.print_topics(num_topics=NUM_TOPIC, num_words=15))
postive_model.save("LDA_Negative_100000")
"""
