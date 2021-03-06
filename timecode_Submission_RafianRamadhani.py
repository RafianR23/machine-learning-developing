# -*- coding: utf-8 -*-
"""TimeCode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oer3EK5ovV60IX9ucF0v6Cc42bONKDUN

## Koneksi Dataset dengan Google Drive
"""

from google.colab import drive
drive.mount('/content/gdrive')

"""## Import Library"""

import seaborn as sns
import matplotlib.pyplot as plt # plotting
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# To Use Algorithm
from keras.layers import Dense, LSTM
import tensorflow as tf

"""## Memasukan Dataset"""

df=pd.read_csv('/content/gdrive/My Drive/Startup/DicodingMLPemula/Time_Series/openweatherdata-denpasar-1990-2020.csv')
#df_test=pd.read_csv('/content/gdrive/My Drive/Sanbercode/Week4/Project/test.csv')
#df_test=pd.read_csv('/content/gdrive/My Drive/Sanbercode/Week4/Project/test.csv')
#df_test=pd.read_csv('/content/gdrive/My Drive/Sanbercode/Week4/Project/test.csv')

"""## Memanggil 10 ribu data terakhir"""

df.tail(10000)

"""## Mengklasifikasikan Cuaca"""

print(df['weather_main'].value_counts())
plt.figure(1, figsize=(8, 6))
sns.countplot(y='weather_main', data=df)
plt.show()

"""## Mengecek Missing Value Pada Data dan memilah Data yang akan digunakan
dan melakukan Drop Kolom dengan missing value besar
"""

df.isnull().sum()

df.drop(columns=['sea_level', 'grnd_level', 'rain_1h', 'rain_3h','rain_6h',
                 'snow_today','rain_today','rain_12h','rain_24h',
                 'snow_1h','snow_3h','snow_6h','snow_12h','snow_24h'],
                 inplace=True, axis=1)

df.isnull().sum()

df.drop(columns=['lat', 'lon', 'timezone',],
                 inplace=True, axis=1)

df.drop(columns=['dt','weather_icon'],
                 inplace=True, axis=1)

df

df.drop(columns=['city_name'],
                 inplace=True, axis=1)

"""## Membagi data yang akan dijadikan latih dan validasi sebesar 80:20"""

df_latih = df[254923:262923] #Mengambil data latih 8 Ribu
df_validasi = df[262924:264925] #Mengambil data validasi 2 Ribu

"""## Membuat Grafik Waktu dan Temperatur"""

dates_latih = df_latih['dt_iso']
temp_train  = df_latih['temp'].values

dates_valid = df_validasi['dt_iso'].values
temp_valid = df_validasi['temp'].values

 
plt.figure(figsize=(15,5))
plt.plot(dates_latih, temp_train)
plt.title('Temperature average',
          fontsize=20);
plt.plot(dates_valid, temp_valid)
plt.title('Temperature average',
          fontsize=20);

train_temp=temp_train.reshape(-1, 1)
valid_temp=temp_valid.reshape(-1, 1)

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
temp_train_new=scaler.fit_transform(train_temp)
temp_valid_new=scaler.fit_transform(valid_temp)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    #series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

"""## Membuat Arsitektur Tensorflow LSTM """

test_set = windowed_dataset(temp_train_new, window_size=60, batch_size=32, shuffle_buffer=1000)
train_set = windowed_dataset(temp_valid_new, window_size=60, batch_size=32, shuffle_buffer=1000)
model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(128, dropout=0.1, recurrent_dropout=0.1, return_sequences=True),
  tf.keras.layers.LSTM(128, dropout=0.1, recurrent_dropout=0.1, return_sequences=True),
  tf.keras.layers.LSTM(64, dropout=0.1, recurrent_dropout=0.1),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

optimizer = tf.keras.optimizers.Adam()
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                              patience=5, min_lr=0.0001)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

"""## Training Data"""

history = model.fit(train_set,epochs=10 , callbacks=[reduce_lr], validation_data=(test_set))

"""## Plot loss dan akurasi pada saat training dan validation"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('Loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc = 'upper left')
plt.show()

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Val MAE Model')
plt.ylabel('MAE')
plt.xlabel('epoch')
plt.legend(['mae', 'val_mae'], loc = 'upper left')
plt.show()

