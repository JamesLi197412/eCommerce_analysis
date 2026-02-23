import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as MSE
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

try:
    import xgboost
    from xgboost import plot_tree
    from xgboost.sklearn import XGBRegressor
except ModuleNotFoundError:
    xgboost = None
    plot_tree = None
    XGBRegressor = None

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

    def data_preprocess(self, encode_features):
        X = self.data[self.features]
        y = self.data[self.target]
        X = pd.get_dummies(X, columns=encode_features)
        return X, y

    def scale_features(self, train_X, test_X, numerical_features):
        # Fit on training data only to avoid leakage.
        scaler = MinMaxScaler()
        train_X = train_X.copy()
        test_X = test_X.copy()
        train_X.loc[:, numerical_features] = scaler.fit_transform(train_X[numerical_features])
        test_X.loc[:, numerical_features] = scaler.transform(test_X[numerical_features])
        return train_X, test_X

    def data_split(self, X, y, portion):
        # self.data.index = self.data.Date
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=portion, random_state=123)
        return train_X, train_y, test_X, test_y

    def model_run(self, encode_features, numerical_features):
        X, y = self.data_preprocess(encode_features)

        if X.empty or len(X) < 10:
            print('Not enough rows to train delivery model; skipping training.')
            return None

        X_train, y_train, X_test, y_test = self.data_split(X, y, 0.3)
        X_train, X_test = self.scale_features(X_train, X_test, numerical_features)

        y_train = np.ravel(y_train)
        y_test = np.ravel(y_test)

        if xgboost is not None:
            best_parameters = self.parameters_tunning(X_train, y_train)
            model = XGBRegressor(
                **best_parameters,
                objective='reg:squarederror',
                random_state=123
            )
        else:
            print('xgboost package is not available; using RandomForestRegressor fallback.')
            model = RandomForestRegressor(
                n_estimators=300,
                random_state=123,
                n_jobs=-1
            )

        model.fit(X_train, y_train)

        # predict the model
        pred = model.predict(X_test)

        # RMSE Computation
        rmse_score = np.sqrt(MSE(y_test, pred))
        print(f'RMSE: {rmse_score:.4f}')

        # save the optimised model
        joblib.dump(model, 'xgb_regression_model.joblib')
        return model

    def visualisation_scatter(self, x_test, y_val, y_pred_xgb):
        plt.scatter(x_test['cities distances'], y_val, color='blue', label='Real', alpha=0.5)
        plt.scatter(x_test['cities distances'], y_pred_xgb, color='red', label='Predict', alpha=0.5)
        plt.title("Real vs Predict")
        plt.legend(loc='best')
        plt.show()

    def parameters_tunning(self, x_train, y_train):
        if XGBRegressor is None:
            return {}

        xgb = XGBRegressor()

        parameters = {'n_jobs': [4],
                      'learning_rate': [0.03, 0.05, 0.07],  # eta
                      'max_depth': [5, 6, 7],
                      'min_child_weight': [2, 4],
                      'subsample': [0.7],
                      'colsample_bytree': [0.7],
                      'n_estimators': [300]}

        xgb_grid = GridSearchCV(xgb,
                                parameters,
                                cv=3,
                                n_jobs=-1,
                                verbose=False)

        xgb_grid.fit(x_train, y_train)

        return xgb_grid.best_params_

    def tree_visualisation(self, num_trees, model):
        if plot_tree is None:
            print('xgboost package is not available; tree visualisation skipped.')
            return
        plot_tree(model, num_trees)
        plt.show()
