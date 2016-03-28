from nltk.corpus import stopwords #stop word list
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.ensemble import RandomForestClassifier
from scipy.sparse import coo_matrix
from sklearn import tree
from sklearn.svm import SVC
import numpy as np

'''
takes in a string and returns a list of meaningful words
'''
def clean_text(text):
    stops = set(stopwords.words("english")) #stopwords list
    #convert emojis to placeholders
    emoji = {':)': 'smileyface', ':(': 'sadface', ':-)': 'smileyface', ':-(': 'sadface', '#': 'hashtag'}
    letters_only = re.sub("[^a-zA-z]", " ", text)
    lower_case = letters_only.lower()
    split = lower_case.split() #gives list of words lower case

    with_emojis = []
    for word in split:
        if word in emoji:
            with_emojis.append(emoji[word])
        else:
            with_emojis.append(word)

    #find meaningful words
    meaningful_words = [w for w in with_emojis if not w in stops]
    final_string = " ".join(meaningful_words)

    return final_string

'''
takes in the bag of words and runs NMF for the number of topics specified, also for the number of top words
'''
def nmf(bag_of_words, vocab, topics, top_words):
    dtm = bag_of_words.toarray()

    from sklearn import decomposition
    num_topics = topics
    num_top_words = top_words
    clf = decomposition.NMF(n_components=num_topics, random_state=1)

    doctopic = clf.fit_transform(dtm)

    #print words associated with topics
    topic_words = []

    for topic in clf.components_:
        word_idx = np.argsort(topic)[::-1][0:num_top_words]
        topic_words.append([vocab[i] for i in word_idx])

    #make visualization easier
    #doctopic = doctopic/np.sum(doctopic, axis = 1, keepdims=True)
    #print "doctopic matrix"
    #print doctopic[0:5]


    print "show top 15 words"
    for t in range(len(topic_words)):
        print ("topic {}: {}".format(t, ' '.join(topic_words[t][:15])))

    return doctopic
