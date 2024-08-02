import math

import matplotlib.pyplot as plt
import numpy as np
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split



# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, LSTM

class LSTM_Model:
    def __init__(self, data):
        self.data = data
        self.train = None

    def data_split(self, X, y, portion):
        # self.data.index = self.data.Date
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=portion, random_state=123)
        return train_X, train_y, test_X, test_y

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
        train_X, train_y, test_X, test_y = self.data_split(0.8, df)
        model = self.build_model(train_X,train_y, time_step)

        train_predict = model.predict(train_X)
        test_predict = model.predict(test_X)

        # invert predictions
        train_predict = self.scaler.inverse_transform(train_predict)
        Y_train = self.scaler.inverse_transform([train_y])
        test_predict = self.scaler.inverse_transform(test_predict)
        Y_test = self.scaler.inverse_transform([test_y])

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
