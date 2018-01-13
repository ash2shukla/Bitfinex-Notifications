from pandas import read_json
from numpy import concatenate as concat
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

sc = MinMaxScaler()

data = read_json('https://pythonpolo.firebaseio.com/BCHdata/2.json').transpose()
data = data.drop(['timestamp'],axis =1)
shifted_data = data['BCHlast'].shift(-1)
shifted_data = shifted_data.rename('Y')

#partially fit the data
sc.partial_fit(data)
data = sc.transform(data)

train_X,train_Y = data[:-1],shifted_data.values.reshape(-1,1)[:-1]
test_X = data[-1]

train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((1,1,test_X.shape[0]))

# design network
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
model.fit(train_X, train_Y, epochs=500, batch_size=72, verbose=2, shuffle=False)

yhat = model.predict(test_X)
print(yhat)
