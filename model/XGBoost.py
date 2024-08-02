import numpy as np
import pandas as pd

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error as MSE
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

import xgboost
import xgboost as xgb
from xgboost import plot_importance


class XGBoostDelivery:
    def __init__(self, df, features, target_col):
        self.data = df
        self.features = features
        self.target = target_col
        self.model = None

    def data_preprocess(self, encode_features, numerical_features):
        X = self.data[self.features]
        y = self.data[self.target]
        X = pd.get_dummies(X, columns=encode_features)

        # numerical_features
        scaler = MinMaxScaler()
        X.loc[:, numerical_features] = scaler.fit_transform(X[numerical_features])
        return X, y

    def data_split(self, X, y, portion):
        # self.data.index = self.data.Date
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=portion, random_state=123)
        return train_X, train_y, test_X, test_y

    def model_run(self, encode_features, numerical_features):
        X, y = self.data_preprocess(encode_features, numerical_features)
        X_train, y_train, X_test, y_test = self.data_split(X,y,0.3)
        xgb_r = xgboost.XGBRFRegressor(objective='reg:linear', n_estimators=10, seed=123)
        xgb_r.fit(X_train, y_train)

        # predict the model
        pred = xgb_r.predict(X_test)

        # RMSE Computation
        rmse = np.sqrt(MSE(y_test, pred))
        print("RMSE : % f" % (rmse))

        return pred


    def modelfit(self, alg, dtrain, predictors, target,useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
        if useTrainCV:
            xgb_param = alg.get_xgb_params()
            xgtrain = xgb.DMatrix(dtrain[predictors].values, label=dtrain[target].values)
            cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
                              metrics='auc', early_stopping_rounds=early_stopping_rounds, show_progress=False)
            alg.set_params(n_estimators=cvresult.shape[0])

        # Fit the algorithm on the data
        alg.fit(dtrain[predictors], dtrain['Disbursed'], eval_metric='auc')

        """
        # Predict training set:
        dtrain_predictions = alg.predict(dtrain[predictors])
        dtrain_predprob = alg.predict_proba(dtrain[predictors])[:, 1]

        # Print model report:
        print("\nModel Report")
        print("Accuracy : %.4g" % metrics.accuracy_score(dtrain['Disbursed'].values, dtrain_predictions)
        print("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain['Disbursed'], dtrain_predprob))

        feat_imp = pd.Series(alg.booster().get_fscore()).sort_values(ascending=False)
        feat_imp.plot(kind='bar', title='Feature Importances')
        plt.ylabel('Feature Importance Score')
        """
