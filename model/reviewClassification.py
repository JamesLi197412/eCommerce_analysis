import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import train_test_split


class reviewClassification:
    def __init__(self, df, reviews, mark):
        self.data = df
        self.X = df[reviews]
        self.y = df[mark]

    def data_split(self, portion):
        train_X, test_X, train_y, test_y = train_test_split(self.X, self.y, test_size=portion, random_state=123)
        return train_X, train_y, test_X, test_y

    def transformation(self, X_train):
        vect = CountVectorizer(ngram_range=(1, 2)).fit(X_train)
        X_train_vectorized = vect.transform(X_train)
        return vect, X_train_vectorized

    def classification_run(self, portion):
        X_train, train_y, test_X, test_y = self.data_split(portion)
        vect, X_train_vectorized = self.transformation(X_train)

        model = LogisticRegression(solver='lbfgs', max_iter=1000)
        model.fit(X_train_vectorized, train_y)

        predictions = model.predict(vect.transform(test_X))

        print('AUC: {}'.format(roc_auc_score(test_y, predictions)))  # multi_class = 'ovr'

        # self.confusion_matrix_plot(test_y, predictions)
        self.roc_curve(test_y, predictions)

        return model

    def confusion_matrix_plot(self, y_test, y_pred_grid):
        cm = confusion_matrix(y_test, y_pred_grid)
        ConfusionMatrixDisplay(confusion_matrix=cm).plot()
        plt.savefig(f'output/model_evaluation/review matrix.png')

    def roc_curve(self, y_test, y_pred_grid):
        ns_probs = [0 for _ in range(len(y_test))]

        fpr, tpr, thresh1 = roc_curve(y_test, y_pred_grid)
        ns_fpr, ns_tpr, thresh2 = roc_curve(y_test, ns_probs)

        # auc scores
        auc_score = roc_auc_score(y_test, y_pred_grid)
        ns_auc = roc_auc_score(y_test, ns_probs)

        # Plot the ROC curve
        plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % auc_score)

        # roc curve for tpr = fpr
        plt.plot(ns_fpr, ns_tpr, linestyle='--', label='50%')
        plt.plot(fpr, tpr, marker='.', label='Logistic')

        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        # plt.show()
        plt.savefig(f'output/model_evaluation/ROC curve.png')
