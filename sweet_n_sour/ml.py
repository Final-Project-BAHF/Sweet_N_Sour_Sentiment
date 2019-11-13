import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# pull in sentiment and stock performance data
sentiment = pd.read_csv('')

# reshape data
X = sentiment."".values.reshape(-1, 1)
y = sentiment."".values.reshape(-1, 1)

# plot data
plt.scatter(X, y)

# create the model and fit the model to the data
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X, y)
# LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

