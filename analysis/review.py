import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud

from model.LDA import LDA, format_topics_sentences, topic_visualisation
from model.reviewClassification import reviewClassification

try:
    import nltk
except ModuleNotFoundError:
    nltk = None


FALLBACK_PORTUGUESE_STOPWORDS = {
    'a', 'as', 'o', 'os', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
    'e', 'ou', 'mas', 'com', 'sem', 'para', 'por', 'que', 'se', 'ao', 'aos', 'à', 'às', 'como', 'mais',
    'menos', 'muito', 'muita', 'muitos', 'muitas', 'já', 'não', 'sim', 'foi', 'são', 'ser', 'ter', 'eu',
    'ele', 'ela', 'eles', 'elas', 'me', 'te', 'lhe', 'nós', 'vocês', 'isso', 'isto', 'aquele', 'aquela'
}


# Sentiment analysis
def review_analysis(reviews_df):
    # Drop empty reviews and keep original dataframe unchanged.
    reviews_df = reviews_df.dropna(subset=['review_comment_message']).copy(deep=True)

    if reviews_df.empty:
        print('No non-null review comments found; skipping review analysis.')
        return reviews_df, pd.DataFrame()

    reviews_df, reviews_df_without_stopwords = data_preprocess(reviews_df, 'review_comment_message')
    reviews_df['tidy_review_comment_message'] = reviews_df['review_comment_message'].apply(text_preprocessing)
    reviews_df['review_label'] = np.where(reviews_df['review_score'] >= 3, 1, 0)

    # Produce common words
    # common_words_visualisation(reviews_df, 'tidy_review_comment_message')

    # Work on Classification and top modelling
    # To make life easier, review_label: positive is 1 and negative is 0.
    reviews_subs = reviews_df[['tidy_review_comment_message', 'review_label']].copy(deep=True).dropna()
    review_classification = reviewClassification(
        df=reviews_subs,
        reviews='tidy_review_comment_message',
        mark='review_label'
    )
    review_classification.classification_run(0.3)

    # Topic modelling -- LDA method
    topic_sents_keywords = topic_modeling(reviews_df_without_stopwords, reviews_df)
    return reviews_df, topic_sents_keywords


def topic_modeling(tokens, df):
    if len(tokens) < 10:
        print('Insufficient tokenized reviews for topic modeling; skipping LDA.')
        return pd.DataFrame()

    coherences = []
    topic_candidates = [k for k in range(5, 25, 5) if k < len(tokens)]
    if not topic_candidates:
        topic_candidates = [2]

    for k in topic_candidates:
        print('Current number of topics: ' + str(k))
        _, _, _, coherence_score = LDA(tokens, num_topics=k)
        coherences.append((k, coherence_score))

    # coherence_plot(coherences)
    best_topic_size = max(coherences, key=lambda item: item[1])[0]
    lda_model, corpus, dictionary, _ = LDA(tokens, num_topics=best_topic_size)
    # Visualize the topics
    topic_visualisation(lda_model, corpus, dictionary)

    all_topics = {}
    num_terms = 10  # Adjust number of words to represent each topic
    for i in range(best_topic_size):
        topic_terms = [word for word, _ in lda_model.show_topic(i, topn=num_terms)]
        all_topics[f'Topic {i + 1}'] = topic_terms

    topics_df = pd.DataFrame(all_topics).T
    topics_df.to_csv('output/model_evaluation/topics_keyword.csv')

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
    portuguese_stopwords = get_portuguese_stopwords()

    length = df.shape[0]
    data_without_stopwords = []

    # Loop through each review
    for i in range(0, length):
        reviews = df.iloc[i][col]  # extract reviews
        doc = tokenize_portuguese(reviews)

        doc = [word for word in doc if word not in portuguese_stopwords]

        # remove very short tokens and numerics
        doc = [value for value in doc if len(value) > 1 and not value.isnumeric()]

        data_without_stopwords.append(doc)

    df['cleaned_reviews'] = data_without_stopwords

    return df, data_without_stopwords


def text_preprocessing(data):
    stop_words = get_portuguese_stopwords()
    words = tokenize_portuguese(data)
    words = [word for word in words if word not in stop_words and len(word) > 1]
    return ' '.join(words)


def tokenize_portuguese(text):
    if not isinstance(text, str):
        text = str(text)
    return re.findall(r"[a-zA-ZÀ-ÿ']+", text.lower())


def get_portuguese_stopwords():
    if nltk is None:
        return FALLBACK_PORTUGUESE_STOPWORDS

    try:
        return set(nltk.corpus.stopwords.words('portuguese'))
    except LookupError:
        return FALLBACK_PORTUGUESE_STOPWORDS


def common_words_visualisation(df, col):
    all_words = ' '.join([str(text) for text in df[col]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f'output/visualisations/reviews/common words.png')
