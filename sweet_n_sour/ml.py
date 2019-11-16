import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# pull in sentiment and stock performance data
sentiment = pd.read_csv('')

# reshape data
X = sentiment."".values.reshape(-1, 1)
y = sentiment."".values.reshape(-1, 1)

# plot data (optional at this step)
plt.scatter(X, y)

# create the model and fit the model to the data
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X, y)
# LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

y = m(model.coef_) + model.intercept_ # y=mx+b

# transform min and max values
x_min = np.array([[X.min()]])
x_max = np.array([[X.max()]])

# calculate the y_min and y_max
y_min = model.predict(x_min)
y_max = model.predict(x_max)

# plot data with fit line
plt.scatter(X, y, c='blue')
plt.plot([x_min[0], x_max[0]], [y_min[0], y_max[0]], c='red')

# predict a value and score it 
from sklearn.metrics import mean_squared_error, r2_score

predicted = model.predict(X)
mse = mean_squared_error(y, predicted)
r2 = r2_score(y, predicted)

# overall score
model.score(X, y)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# train the model using the training data
model.fit(X_train, y_train)


# Neural Networks with Keras
# setting seed value to ensure results are reproduced
from numpy.random import seed
seed(42)
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dense

training_data_path = os.path.join('sentimentsamp.csv')
alltrainingdata_df = pd.read_csv(training_data_path, delimiter="|", skiprows=1, header=None)

X_train_df = alltrainingdata_df['sentencescore']
y_train_df = alltrainingdata_df['sentiment']
y_training_data = os.path.join('sentimentsamp')
# shape data
X_train = X_train_df.values
y_train = to_categorical
# scale train data
from sklearn.preprocessing import StandardScaler
X_scaler = StandardScaler().fit('x sentiment samples')
X_train_scaled = X_scaler.transform('x sentiment samples')
# scale test data
X_test_scaled = X_scaler.transform('x test data')
# one-hot encode the labels
from tensorflow.keras.utils import to_categorical
y_train_categorical = to_categorical('y sentiment samples')
y_test_categorical = to_categorical('y test data')
