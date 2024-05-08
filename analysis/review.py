from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer

from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Sentiment analysis
def review_analysis(reviews_df):
    stop_words = set(stopwords.words('portuguese'))
    # tokenizer = RegexpTokenizer(r'\w+')
    # text process
    # 1. drop column with nan
    reviews_df.dropna(subset = ['review_comment_message'],inplace = True ) # Drop comment is NaN

    reviews_df['tidy_review_comment_message'] = reviews_df['review_comment_message'].apply(text_preprocessing)
    reviews_df['label'] = np.where(reviews_df['review_score'] >=3 , 1, 0)

    # common_words_visualisation(reviews_df,'typed_review_comment_message')
    # Classification
    # Bag of Words + Logistic Regression
    #test_df = bag_of_words(reviews_df,stop_words) # generate the prediction
    #test_df.columns = ['review_id','prediction_label']
    # print(test_df.columns)
    # merge test_df with original review_df
    #test_df = test_df.merge(reviews_df, on = 'review_id', how = 'inner')
    #print(test_df.head(5))
    #print(test_df.columns)

    # TF-IDF + Logistic Regression
    # tf_idf(reviews_df,stop_words)

    # Topic modelling
    topic_modelling()

    return reviews_df


def text_preprocessing(data):
    stop_words = set(stopwords.words('portuguese'))
    tokenizer = RegexpTokenizer(r'\w+')
    stemmer = PorterStemmer()

    txt = data.lower()      # Lower the word
    words = tokenizer.tokenize(txt)     # Tokenization
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
    plt.savefig(f'output/visualisation/reviews/common words.png')

def bag_of_words(df, stop_words,col = 'tidy_review_comment_message'):
    sizes = int(round(df.shape[0]) * 0.8)
    train = df.iloc[:sizes,:]
    test = df.iloc[sizes:,:]

    review_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words=stop_words)
    # bag-of-words feature matrix
    reviews_train = review_vectorizer.fit_transform(train[col])
    reviews_test = review_vectorizer.fit_transform(test[col])

    # splitting data into training and validation set
    xtrain, xvalid, ytrain, yvalid = train_test_split(reviews_train, train['label'], random_state=42, test_size=0.3)

    lreg = LogisticRegression()
    lreg.fit(xtrain, ytrain)  # training the model

    prediction = lreg.predict_proba(xvalid)  # predicting on the validation set
    prediction_int = prediction[:, 1] >= 0.5  # if prediction is greater than or equal to 0.3 than 1 else 0
    prediction_int = prediction_int.astype(int)

    f1_score(yvalid, prediction_int)  # calculating f1 score

    test_pred = lreg.predict_proba(reviews_test)
    test_pred_int = test_pred[:, 1] >= 0.3
    test_pred_int = test_pred_int.astype(int)
    test.loc[:, 'label'] = test_pred_int
    submission = test[['review_id', 'label']]
    # submission.to_csv('output/review_bag_of_word.csv', index=False)  # writing data to a CSV file
    return submission

def tf_idf(df,stop_words, col = 'tidy_review_comment_message'):
    sizes = int(round(df.shape[0]) * 0.8)
    train = df.iloc[:sizes,:]
    test = df.iloc[sizes:,:]

    tfidf_vectorizer = TfidfVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words=stop_words)
    # TF-IDF feature matrix
    train_tfidf = tfidf_vectorizer.fit_transform(train[col])
    test_tfidf = tfidf_vectorizer.fit_transform(test[col])


    return train_tfidf,test_tfidf

def topic_modelling():
    # Sample documents
    documents = ["I like to eat bananas",
                 "I prefer apples over bananas",
                 "Bananas are delicious",
                 "I like to eat apples",
                 "I like to eat oranges"]

    # Tokenize the documents
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = set(stopwords.words('english'))
    tokenized_docs = [word_tokenize(doc.lower()) for doc in documents]
    tokenized_docs = [[word for word in doc if word not in stop_words and word.isalnum()] for doc in tokenized_docs]

    # Create a dictionary and a corpus
    dictionary = corpora.Dictionary(tokenized_docs)
    corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]

    # Build the LDA model
    lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=2, passes=10)

    # Print the topics
    topics = lda_model.print_topics(num_topics=2, num_words=3)
    for topic in topics:
        print(topic)

    # Compute Coherence score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=tokenized_docs, dictionary=dictionary, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    print('Coherence Score: ', coherence_lda)