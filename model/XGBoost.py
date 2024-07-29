import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from xgboost import plot_importance


class StockForecaster:
    def __init__(self, df, features, target_col, parms, drop_cols):
        self.data = df
        self.features = features
        self.target = target_col
        self.parms = parms
        self.model = None
        self.drop_cols = drop_cols

    def data_split(self, test_size, valid_size):
        self.data = self.data.fillna(0)
        self.data.index = self.data.Date

        test_split_idx = int(self.data.shape[0] * (1 - test_size))
        valid_split_idx = int(self.data.shape[0] * (1 - (valid_size + test_size)))

        train_df = self.data.iloc[:valid_split_idx].copy()
        valid_df = self.data.iloc[valid_split_idx + 1:test_split_idx].copy()
        test_df = self.data.iloc[test_split_idx + 1:].copy()

        train_df = train_df.drop(self.drop_cols, 1)
        test_df = test_df.drop(self.drop_cols, 1)
        valid_df = valid_df.drop(self.drop_cols, 1)

        y_train = train_df[self.target].copy()
        X_train = train_df.drop([self.target], 1)

        y_valid = valid_df[self.target].copy()
        X_valid = valid_df.drop([self.target], 1)

        y_test = test_df[self.target].copy()
        X_test = test_df.drop([self.target], 1)
        self.test_split_idx = test_split_idx
        return X_train, y_train, X_test, y_test, X_valid, y_valid

    def fine_tune(self, X_train, y_train, X_valid, y_valid, X_test, y_test):
        eval_set = [(X_train, y_train), (X_valid, y_valid)]
        model = xgb.XGBRegressor(eval_set=eval_set, objective='reg:squarederror', verbose=False)
        clf = GridSearchCV(model, self.parms)
        clf.fit(X_train, y_train)
        print(f"Best params:{clf.best_params_}")
        print(f"Best Validation Score = {clf.best_score_}")

        model = xgb.XGBRegressor(**clf.best_params_, objective='reg:squarederror')
        model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

        plot_importance(model)

        y_pred = model.predict(X_test)
        print(f'y_true = {np.array(y_test)[:5]}')
        print(f'y_pred = {y_pred[:5]}')

        print(f'mean_squared_error = {mean_squared_error(y_test, y_pred)}')

        predicted_prices = self.data.loc[self.test_split_idx + 1:].copy()
        predicted_prices[self.target] = y_pred
        return predicted_prices

    def model_run(self):
        X_train, y_train, X_test, y_test, X_valid, y_valid = self.data_split(0.15, 0.15)
        prediction = self.fine_tune(X_train, y_train, X_valid, y_valid, X_test, y_test)
        return prediction

    def create_lagged_dataset(self, n_past=1):
        """
        Creates a dataset for XGBoost with lagged features.

        Args:
            n_past (int, optional): The number of past periods to use as features. Defaults to 1.

        Returns:
            pandas.DataFrame: The dataset with lagged features and target.
        """

        lagged_df = self.data.copy()
        for i in range(1, n_past + 1):
            lagged_df[f"lag_{i}"] = lagged_df.shift(i)[self.target.name]
        lagged_df.dropna(inplace=True)

        X = lagged_df.drop(self.target.name, axis=1)
        y = lagged_df[self.target.name]

        return X, y
