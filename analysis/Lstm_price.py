import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from analysis import HouseAnalysis as kl
import tensorflowjs as tfjs
import argparse
import warnings

from hyParameter.hyPerParameter import hyperParam,loss, look_back, optimization

warnings.filterwarnings("ignore")

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=True, help="path to csv data file")
ap.add_argument("-hp", "--h5path", required=True, help="path where keras model is to be saved")
ap.add_argument("-tfp", "--tfjspath", required=True,help="path where tfjs layer is to be saved")
args = vars(ap.parse_args())


def M1Data(data):
    data_ = data
    # Method One
    trainx = data_.mean(axis=1)
    trainx = np.reshape(trainx.values, (len(trainx), 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_x = scaler.fit_transform(trainx)

    # The Focus Should be Sales price focus is on Sale Price
    trainy = np.reshape(data['SalePrice'].values, (len(trainx), 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_y = scaler.fit_transform(trainy)

    return data_x, data_y


# following function outputs X training as mean of all features column wise and train Y is sale price only.
# following function can be used to train LSTM model


# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back = 1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)


# following split train test function can be used when you use create_dataset_new function
def train_test_split(data_x, data_y, percent=0.67):
    train_size = int(len(data_x) * percent)
    # test_size = len(data_x) - train_size
    tran_x, tst_x = data_x[0:train_size, :], data_x[train_size:len(data_x), :]
    print(len(tran_x), len(tst_x))

    tran_y, tst_y = data_y[0:train_size, :], data_y[train_size:len(data_y), :]
    print(len(tran_y), len(tst_y))

    return tran_x, tran_y, tst_x, tst_y


def lstmArchitect(node, error, optimizer):
    model = tf.keras.models.Sequential(
        tf.keras.layers.LSTM(node,input_shape=(1, look_back['look_back']), return_sequences=True),
        tf.keras.layers.LSTM(node),
        tf.keras.layers.Dense(1))
    model.compile(loss=error, optimizer=optimizer)
    return model


def trainLSTMModel(trainX, trainY, epoch, batch_size, verbose):
    lstm = lstmArchitect(288, loss.get('MSE'), optimization.get('ADAM'))
    lstm.fit(trainX, trainY, batch_size=batch_size, epochs=epoch, verbose=verbose)
    print('summary:\n',)
    print(lstm.summary())
    return lstm


def runModel(data, h5_path, tfjs_path):
    # use saleprice only for both x and y features ###METHOD 2
    data_ = data
    # As our focus is on Sale Price
    trainy = np.reshape(data_['SalePrice'].values, (len(data_), 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_y = scaler.fit_transform(trainy)
    # split data
    train_size = int(len(data_y) * 0.67)
    train, test = data_y[0:train_size, :], data_y[train_size:len(data_y), :]
    print(len(train), len(test))

    #
    #Preprocess the Data for the LSTM Model

    look_back = 25
    trainX, trainY = create_dataset(train, look_back=look_back)
    testX, testY = create_dataset(test, look_back=look_back)

    # reshape input to be [samples, time steps, features]
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    trained_model = trainLSTMModel(trainX, trainY, hyperParam.get('Epoch'), hyperParam.get('Batch_Size'), 2)

    # save model to h5py to make restAPI
    trained_model.save(h5_path)  # path where to store h5 model

    # convert model to tfjs layer format
    tfjs_target_dir = tfjs_path
    tfjs.converters.save_keras_model(trained_model, tfjs_target_dir)  # path where to store tfjs format

    # prediction
    trainPredict = trained_model.predict(trainX)
    testPredict = trained_model.predict(testX)
    # inverse tranformation for coreect prediction
    trainPredict = scaler.inverse_transform(trainPredict)
    trainY = scaler.inverse_transform([trainY])
    testPredict = scaler.inverse_transform(testPredict)
    testY = scaler.inverse_transform([testY])

    trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
    print('Train Score: %.2f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
    print('Test Score: %.2f RMSE' % (testScore))

    # shift train predictions for plotting
    trainPredictPlot = np.empty_like(data_y)
    trainPredictPlot[:, :] = np.nan
    trainPredictPlot[look_back:len(trainPredict) + look_back, :] = trainPredict

    # shift test predictions for plotting
    testPredictPlot = np.empty_like(data_y)
    testPredictPlot[:, :] = np.nan
    testPredictPlot[len(trainPredict) + (look_back * 2) + 1:len(data_y) - 1, :] = testPredict

    # plot training actual and predicted part
    plt.plot(data['SalePrice'], label='Actual')
    plt.plot(pd.DataFrame(trainPredictPlot, columns=["close"], index=data.index).close, label='Training')
    plt.plot(pd.DataFrame(testPredictPlot, columns=["close"], index=data.index).close, label='Testing')
    plt.legend(loc='best')
    plt.show()


if __name__ == '__main__':
    # load preprocessed data
    data = kl.final_data(args["path"])

    runModel(data, args["h5path"], args["tfjspath"])
