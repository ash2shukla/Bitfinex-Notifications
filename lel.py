import numpy as np
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import BayesianRidge
from matplotlib import pyplot as plt
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler

def forecast_feature(data,col='x1'):
	history = [x for x in data[col].values]
	forecasted = []
	for i in range(len(test_X)):
		model = ARIMA(history,order=(5,1,0))
		model_fit = model.fit(disp=0)
		output = model_fit.forecast()[0]
		history.append(output)
		forecasted.append(output[0])
		#print("forecasted = %f , exact = %f"%(output,test_X[col][933+i]))
	return forecasted
'''
def predictRNN(X_train,Y_train,X_test):
	X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
	Y_train = np.reshape(Y_train)
	regressor = Sequential()
	regressor.add(LSTM(units = 4, activation = 'sigmoid', input_shape = (1, 10)))
	regressor.add(Dense(units = 1))
	regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
	regressor.fit(X_train, Y_train, batch_size = 32, epochs = 200)

	inputs = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))
	forecast = regressor.predict(inputs)
	return forecast
'''	
if __name__ == "__main__":
	#data = pd.read_csv('bch81.csv')
	data = pd.read_json('https://pythonpolo.firebaseio.com/BCHdata/1.json').transpose()
	data = data.drop(['BCHHighestBid','BCHbaseVol','BCHlowestAsk','BCHquoteVol','timestamp'],axis=1)
	data=data.dropna(axis=0)
	length = data.shape[0]-1
	
	data_X = data.filter(['BCHhigh', 'BCHlow', 'BCHpercent', 'BTChigh', 'BTClast','BTClow', 'bchtradebuyprice', 'bchtradesellprice','btctradebuyprice','btctradesellprice', 'timestamp'])
	data_Y = data['BCHlast']
	
	# Y is one ahead
	
	train_X = data_X[:length]
	test_X = data_X[length:]

	train_Y = data_Y[:length]
	test_Y = data_Y[length:]
	#print(train_X.shape,test_X.shape,train_Y.shape,test_Y.shape)
	model = BayesianRidge(alpha_2=0.01,fit_intercept=False)
	model.fit(train_X,train_Y)
	forecasted = []
	for i in ['BCHhigh','BCHlow', 'BCHpercent', 'BTChigh', 'BTClast','BTClow', 'bchtradebuyprice', 'bchtradesellprice','btctradebuyprice','btctradesellprice']:
		feature_name= i
		out = forecast_feature(train_X,col=feature_name)
		forecasted.append(out[0])
	forecasted = np.array(forecasted).reshape(1,-1)
	print('Forecast by Bayesian with ARIMA ',model.predict(forecasted))
	
	print('Prediction by Bayesian with actual values ',model.predict(test_X.ix[0].reshape(1,-1)))
	print('Actual Value ',test_Y.ix[0])

	#sc = MinMaxScaler()
	#print('Forecast by RNN ',predictRNN(sc.fit_transform(train_X),sc.fit_transform(train_Y),sc.fit_transform(forecasted)))
	
	
	
	
	
	
	
	
