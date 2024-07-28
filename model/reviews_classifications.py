from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split


def bag_of_words(df, stop_words, col='tidy_review_comment_message'):
    sizes = int(round(df.shape[0]) * 0.8)
    train = df.iloc[:sizes, :]
    test = df.iloc[sizes:, :]

    review_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words=stop_words)
    # bag-of-words feature matrix
    reviews_train = review_vectorizer.fit_transform(train[col])
    reviews_test = review_vectorizer.fit_transform(test[col])

    # splitting src into training and validation set
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
    # submission.to_csv('output/review_bag_of_word.csv', index=False)  # writing src to a CSV file
    return submission


def tf_idf(df, stop_words, col='tidy_review_comment_message'):
    sizes = int(round(df.shape[0]) * 0.8)
    train = df.iloc[:sizes, :]
    test = df.iloc[sizes:, :]

    tfidf_vectorizer = TfidfVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words=stop_words)
    # TF-IDF feature matrix
    train_tfidf = tfidf_vectorizer.fit_transform(train[col])
    test_tfidf = tfidf_vectorizer.fit_transform(test[col])

    return train_tfidf, test_tfidf
