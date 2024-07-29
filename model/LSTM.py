import math

import matplotlib.pyplot as plt
import numpy as np
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler


# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, LSTM

class LSTM_Model:
    def __init__(self, data):
        self.data = data
        self.train = None

    def split_data(self, ratio, df):
        train_size = int(len(df) * ratio)
        train, test = df[0:train_size, :], df[train_size:len(df), :]
        return train, test, train_size

    def data_process(self):
        scaler = MinMaxScaler(feature_range=(0, 1))
        self.scaler = scaler
        df = scaler.fit_transform(np.array(self.data).reshape(-1, 1))

        return df

    def create_dataset(self, time_step=1):
        dataX, dataY = [], []
        for i in range(len(self.data) - time_step - 1):
            a = self.data[i:(i + time_step), 0]
            dataX.append(a)
            dataY.append(self.data[i + time_step, 0])
        return np.array(dataX), np.array(dataY)

    def build_model(self, trainX, trainY, time_step):
        regressor = Sequential()
        # First LSTM layer with Dropout regularisation
        regressor.add(LSTM(units=4, return_sequences=True, input_shape=(1, time_step)))
        regressor.add(Dense(1))

        regressor.compile(optimizer='adam', loss='mean_squared_error')
        regressor.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)
        print(regressor.summary())
        return regressor

    def rmse_evaulation(train, predict):
        return (math.sqrt(mean_squared_error(train, predict)))

    def run(self, time_step=100):
        df = self.data_process()
        train, test, train_size = self.split_data(0.8, df)
        X_train, Y_train = self.create_dataset(train, time_step)
        X_test, Y_test = self.create_dataset(test, time_step)
        model = self.build_model(X_train, Y_train, time_step)

        train_predict = model.predict(X_train)
        test_predict = model.predict(X_test)

        # invert predictions
        train_predict = self.scaler.inverse_transform(train_predict)
        Y_train = self.scaler.inverse_transform([Y_train])
        test_predict = self.scaler.inverse_transform(test_predict)
        Y_test = self.scaler.inverse_transform([Y_test])

        # calculate root mean squared error
        trainScore = np.sqrt(mean_squared_error(Y_train[0], train_predict[:, 0]))
        print('Train Score: %.2f RMSE' % (trainScore))
        testScore = np.sqrt(mean_squared_error(Y_test[0], test_predict[:, 0]))
        print('Test Score: %.2f RMSE' % (testScore))

        self.visulations(time_step, train_predict, test_predict)

        return train_predict, test_predict

    def visulations(self, time_step, train_predict, test_predict):
        trainPlot = np.empty_like(self.data)
        trainPlot[:, :] = np.nan
        trainPlot[time_step: len(train_predict) + time_step, :] = train_predict

        testPlot = np.empty_like(self.data)
        testPlot[:, :] = np.nan
        testPlot[len(train_predict) + (time_step) * 2 + 1:len(self.data) - 1, :] = test_predict

        plt.plot(self.scaler.inverse_transform(self.data))
        plt.plot(trainPlot)
        plt.plot(testPlot)
        plt.show()
