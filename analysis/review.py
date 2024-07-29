import jieba
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud

from model.LDA import *


# Sentiment analysis
def review_analysis(reviews_df):
    # 1. drop column with nan
    reviews_df.dropna(subset=['review_comment_message'], inplace=True)  # Drop comment is NaN

    reviews_df, reviews_df_without_stopwords = data_preprocess(reviews_df, 'review_comment_message')
    reviews_df['tidy_review_comment_message'] = reviews_df['review_comment_message'].apply(text_preprocessing)
    reviews_df['label'] = np.where(reviews_df['review_score'] >= 3, 1, 0)
    reviews_df.to_csv('reviews.csv')
    # Produce common words
    # common_words_visualisation(reviews_df, 'tidy_review_comment_message')

    # Work on Classification and top modelling

    # Topic modelling -- LDA method
    lda_model, corpus = LDA(reviews_df_without_stopwords, num_topics=20)

    topic_sents_keywords = format_topics_sentences(lda_model, corpus, reviews_df)
    topic_sents_keywords.to_csv('test_topic.csv')
    return reviews_df



def data_preprocess(df, col):
    portuguese_stopwords = nltk.corpus.stopwords.words('portuguese')
    lemma = WordNetLemmatizer()

    length = df.shape[0]
    data_without_stopwords = []

    # Loop through each review
    for i in range(0, length):
        reviews = df.iloc[i][col]  # extract reviews
        doc = jieba.lcut(reviews.strip())  # Split the Chinese words

        doc = [lemma.lemmatize(word) for word in doc if not word in set(portuguese_stopwords)]

        # remove special characterists
        special_symbols = ['，', '！', '。', '？', 'h', '+', ' ', '、', '?', '…', '：', ')', '⊙', 'o', '⊙', '(',
                           '!', ':', '', '...', "'"]
        doc = [value for value in doc if not value in set(special_symbols)]

        data_without_stopwords.append(doc)

    df['cleaned_reviews'] = data_without_stopwords

    return df, data_without_stopwords


def text_preprocessing(data):
    stop_words = set(stopwords.words('portuguese'))
    tokenizer = RegexpTokenizer(r'\w+')
    stemmer = PorterStemmer()

    txt = data.lower()  # Lower the word
    words = tokenizer.tokenize(txt)  # Tokenization
    words = [w for w in words if not w in stop_words]  # remove stop words
    words = [stemmer.stem(i) for i in words]  # stemming the word
    words = ','.join([text for text in words])

    return words

def common_words_visualisation(df,col):
    all_words = ' '.join([str(text) for text in df[col]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f'output/visualisations/reviews/common words.png')

