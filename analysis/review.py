from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


# Sentiment analysis
def review_analysis(reviews_df):
    # stop_words = set(stopwords.words('portuguese'))
    # tokenizer = RegexpTokenizer(r'\w+')
    # text process
    # 1. drop column with nan
    reviews_df.dropna(subset = ['review_comment_message'],inplace = True ) # Drop comment is NaN

    reviews_df['typed_review_comment_message'] = reviews_df['review_comment_message'].apply(text_preprocessing)
    print(reviews_df.head(5))
    print('-' * 20)
    print(reviews_df.columns)

    common_words_visualisation(reviews_df,'typed_review_comment_message')

    # Extracting features from cleaned reviews
    # Bag of Words


    return reviews_df


def text_preprocessing(data):
    stop_words = set(stopwords.words('portuguese'))
    tokenizer = RegexpTokenizer(r'\w+')
    stemmer = PorterStemmer()

    txt = data.lower()      # Lower the word
    words = tokenizer.tokenize(txt)     # Tokenization
    words = [w for w in words if not w in stop_words]  # remove stop words
    words = [stemmer.stem(i) for i in words]  # stemming the word

    return words

def common_words_visualisation(df,col):
    all_words = ' '.join([str(text) for text in df[col]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f'output/visualisation/reviews/common words.png')

def bag_of_words(df,col):
    review_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='portuguese')
    reviews = review_vectorizer.fit_transform(df[col])
    train_bow = reviews[:31962, :]
    test_bow = reviews[31962:, :]

    # splitting data into training and validation set
    xtrain_bow, xvalid_bow, ytrain, yvalid = train_test_split(train_bow, train['label'], random_state=42, test_size=0.3)

    lreg = LogisticRegression()
    lreg.fit(xtrain_bow, ytrain)  # training the model

    prediction = lreg.predict_proba(xvalid_bow)  # predicting on the validation set
    prediction_int = prediction[:, 1] >= 0.5  # if prediction is greater than or equal to 0.3 than 1 else 0
    prediction_int = prediction_int.astype(np.int)

    f1_score(yvalid, prediction_int)  # calculating f1 score

    test_pred = lreg.predict_proba(test_bow)
    test_pred_int = test_pred[:, 1] >= 0.3
    test_pred_int = test_pred_int.astype(np.int)
    test['label'] = test_pred_int
    submission = test[['id', 'label']]
    submission.to_csv('sub_lreg_bow.csv', index=False)  # writing data to a CSV file

def tf_idf(df,col):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='english')
    # TF-IDF feature matrix
    tfidf = tfidf_vectorizer.fit_transform(df[col])

    train_tfidf = tfidf[:31962, :]
    test_tfidf = tfidf[31962:, :]

    xtrain_tfidf = train_tfidf[ytrain.index]
    xvalid_tfidf = train_tfidf[yvalid.index]

    lreg.fit(xtrain_tfidf, ytrain)

    prediction = lreg.predict_proba(xvalid_tfidf)
    prediction_int = prediction[:, 1] >= 0.3
    prediction_int = prediction_int.astype(np.int)

    f1_score(yvalid, prediction_int)
    return