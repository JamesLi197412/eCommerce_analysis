import matplotlib.pyplot as plt
import numpy as np
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
        train_X, test_X, train_y, test_y = train_test_split(
            self.X,
            self.y,
            test_size=portion,
            random_state=123,
            stratify=self.y
        )
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

        X_test_vectorized = vect.transform(test_X)
        pred_probs = model.predict_proba(X_test_vectorized)[:, 1]
        predictions = (pred_probs >= 0.5).astype(int)

        try:
            auc_score = roc_auc_score(test_y, pred_probs)
            print(f'AUC: {auc_score:.4f}')
        except ValueError as error:
            print(f'AUC is not available for this split: {error}')

        self.confusion_matrix_plot(test_y, predictions)
        self.roc_curve(test_y, pred_probs)

        return model

    def confusion_matrix_plot(self, y_test, y_pred_grid):
        cm = confusion_matrix(y_test, y_pred_grid)
        ConfusionMatrixDisplay(confusion_matrix=cm).plot()
        plt.savefig(f'output/model_evaluation/review matrix.png')

    def roc_curve(self, y_test, y_pred_probs):
        ns_probs = np.zeros(len(y_test))
        fpr, tpr, _ = roc_curve(y_test, y_pred_probs)
        ns_fpr, ns_tpr, _ = roc_curve(y_test, ns_probs)
        auc_score = roc_auc_score(y_test, y_pred_probs)

        # Plot the ROC curve
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % auc_score)
        plt.plot(ns_fpr, ns_tpr, linestyle='--', label='50%')

        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.savefig(f'output/model_evaluation/ROC curve.png')
