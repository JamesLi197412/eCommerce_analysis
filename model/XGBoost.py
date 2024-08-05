import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost
from sklearn.metrics import mean_squared_error as MSE
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from xgboost import plot_tree
from xgboost.sklearn import XGBRegressor
import joblib

"""
    This module is a XGBoost Linear Regression class. It is used for predicting 
    Delivery time.
"""
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
        X_train, y_train, X_test, y_test = self.data_split(X, y, 0.3)

        best_parameters = self.parameters_tunning(X_train, y_train)

        xgb_r = xgboost.XGBRFRegressor(colsample_bytree = best_parameters['colsample_bytree'],
                                       learning_rate = best_parameters['learning_rate'],
                                       max_depth = best_parameters['max_depth'],
                                       min_child_weight = best_parameters['min_child_weight'],
                                       n_estimators = best_parameters['n_estimators'],
                                       nthread = best_parameters['nthread'],
                                       subsample = best_parameters['subsample'],
                                       objective='reg:linear'
                                       )
        xgb_r.fit(X_train, y_train)

        # predict the model
        pred = xgb_r.predict(X_test)

        # RMSE Computation
        rmse_score = np.sqrt(MSE(y_test, pred))
        print("RMSE : % f" % (rmse_score))

        # save the optimised model
        joblib.dump(xgb_r, 'xgb_regression_model.joblib')


        return xgb_r



    def visualisation_scatter(self,x_test, y_val, y_pred_xgb):
        plt.scatter(x_test['cities distances'], y_val, color='blue', label='Real', alpha=0.5)
        plt.scatter(x_test['cities distances'], y_pred_xgb, color='red', label='Predict', alpha=0.5)
        plt.title("Real vs Predict")
        plt.legend(loc='best')
        plt.show()


    def parameters_tunning(self, x_train, y_train):
        xgb = XGBRegressor()

        parameters = {'nthread': [4],  # when use hyperthread, xgboost may become slower
                      'objective': ['reg:linear'],
                      'learning_rate': [.03, 0.05, .07],  # so called `eta` value
                      'max_depth': [5, 6, 7],
                      'min_child_weight': [4],
                      'subsample': [0.7],
                      'colsample_bytree': [0.7],
                      'n_estimators': [500]}

        xgb_grid = GridSearchCV(xgb,
                                parameters,
                                cv=2,
                                n_jobs=5,
                                verbose=True)

        xgb_grid.fit(x_train, y_train)

        return xgb_grid.best_params_

    def tree_visualisation(self, num_trees, model):
        plot_tree(model, num_trees)
        plt.show()
