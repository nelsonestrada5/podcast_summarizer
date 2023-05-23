# extractive_scoring.py

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def get_sentences(text):
    return sent_tokenize(text)

def position_score(i, sentences_len):
    normalized_position = i / sentences_len
    if normalized_position <= 0.1:
        return 0.85
    elif normalized_position > 0.1 and normalized_position <= 0.2:
        return 0.8
    elif normalized_position > 0.2 and normalized_position <= 0.3:
        return 0.7
    elif normalized_position > 0.3 and normalized_position <= 0.4:
        return 0.6
    else:
        return 0.5

def remove_stop_words(words):
    stop_words = set(stopwords.words('english'))
    return [word for word in words if word not in stop_words]

def relevance_score(sentence, query):
    vectorizer = CountVectorizer().fit_transform([sentence, query])
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    return csim[0,1]

def get_sentence_score(i, sentence, sentences_len, query):
    words = word_tokenize(sentence)
    non_stop_words = remove_stop_words(words)

    position_weight = 0.4
    non_stop_word_density_weight = 0.3
    relevance_weight = 0.3

    position_s = position_score(i, sentences_len)
    non_stop_word_density_s = len(non_stop_words) / len(words)
    relevance_s = relevance_score(sentence, query)

    score = position_weight * position_s + non_stop_word_density_weight * non_stop_word_density_s + relevance_weight * relevance_s
    return score
