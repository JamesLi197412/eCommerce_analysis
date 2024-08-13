import jieba
import matplotlib
import numpy as np

matplotlib.use('TkAgg')

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud

from model.LDA import *
from model.reviewClassification import *


# Sentiment analysis
def review_analysis(reviews_df):
    # 1. drop column with nan
    reviews_df.dropna(subset=['review_comment_message'], inplace=True)  # Drop comment is NaN

    reviews_df, reviews_df_without_stopwords = data_preprocess(reviews_df, 'review_comment_message')
    reviews_df['tidy_review_comment_message'] = reviews_df['review_comment_message'].apply(text_preprocessing)
    reviews_df['review_label'] = np.where(reviews_df['review_score'] >= 3, 1, 0)

    # Produce common words
    # common_words_visualisation(reviews_df, 'tidy_review_comment_message')

    # Work on Classification and top modelling
    # To make life easier, review_label: positive is 1 and negative is 0.
    reviews_subs = reviews_df[['tidy_review_comment_message', 'review_label']].copy(deep=True).dropna()
    review_classification = reviewClassification(df = reviews_subs, reviews = 'tidy_review_comment_message', mark = 'review_label')
    review_classification.classification_run(0.3)

    # Topic modelling -- LDA method
    topic_sents_keywords = topic_modeling(reviews_df_without_stopwords, reviews_df)
    return reviews_df,topic_sents_keywords


def topic_modeling(tokens, df):
    coherences = []
    for k in range(5, 25, 5):
        print('Current number of topics: ' + str(k))
        _, _, _, coherence_score = LDA(tokens, num_topics=k)
        coherences.append((k, coherence_score))

    # coherence_plot(coherences)

    lda_model, corpus, dictionary, _ = LDA(tokens, num_topics=10)
    # Visualize the topics
    topic_visualisation(lda_model, corpus, dictionary)

    topic_data = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, mds='pcoa')

    all_topics = {}
    num_terms = 10  # Adjust number of words to represent each topic
    lambd = 0.6  # Adjust this accordingly based on tuning above
    for i in range(1, 24):  # Adjust this to reflect number of topics chosen for final LDA model
        topic = topic_data.topic_info[topic_data.topic_info.Category == 'Topic' + str(i)].copy()
        topic['relevance'] = topic['loglift'] * (1 - lambd) + topic['logprob'] * lambd
        all_topics['Topic ' + str(i)] = topic.sort_values(by='relevance', ascending=False).Term[:num_terms].values

    topics_df = pd.DataFrame(all_topics).T
    topics_df.to_csv('topics_keyword.csv')

    topic_sents_keywords = format_topics_sentences(lda_model, corpus, df)

    return topic_sents_keywords


def coherence_plot(coherences):
    x_val = [x[0] for x in coherences]
    y_val = [x[1] for x in coherences]

    plt.plot(x_val, y_val)
    plt.scatter(x_val, y_val)
    plt.title('Number of Topics vs. Coherence')
    plt.xlabel('Number of Topics')
    plt.ylabel('Coherence')
    plt.xticks(x_val)
    # plt.show()
    plt.savefig(f'output/model_evaluation/coherence score by topics.png')


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


def common_words_visualisation(df, col):
    all_words = ' '.join([str(text) for text in df[col]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f'output/visualisations/reviews/common words.png')
