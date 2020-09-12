import tensorflow as tf

look_back = {
    'look_back': 25,
    'look_back_V1':1,

}

hyperParam = {
    'Epoch': 300,
    'Batch_Size':20,

}

optimization = {
    'ADAM': tf.keras.optimizers.Adam,
    'SGD': tf.keras.optimizers.SGD,
}

loss = {
    'BinCrossEntropy': tf.keras.losses.BinaryCrossentropy,
    'MSE': tf.keras.losses.mean_squared_error,
    'MSLE': tf.keras.losses.mean_squared_logarithmic_error,
    'MAPE': tf.keras.losses.mean_absolute_percentage_error,
    'MAE': tf.keras.losses.mean_absolute_error,

}
