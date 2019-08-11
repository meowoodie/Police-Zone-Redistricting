import numpy as np
import statsmodels.api as sm
from validation import data_preparation

# load random generated decision and corresponding simulation output
with open("data/sim-output.txt", "r") as f:
    ds = []
    ws = []
    for line in f:
        d, w        = line.strip("\n").split("\t")
        year, beats = d.split(",")[0], d.split(",")[1:]
        ds.append([year, beats])
        ws.append(float(w))

# load data
beat_info, mu, t_beats, Tau, d_beats, Dist, _ = data_preparation()

X = []
Y = []
for n in range(len(ds)):
    # load decision into a vector
    year, beats = ds[n][0], ds[n][1]
    # load workload
    w           = sum([ beat_info[beat][year]["count"] for beat in beats ]) * mu
    # construct Y
    y           = ws[n] - w
    # construct X
    x           = [ 0 for i in range(len(t_beats) - 10) ] # remove last 10 beats (zone 7)
    for beat in beats:
        x[t_beats.index(beat)] = beat_info[beat][year]["count"] * Tau[t_beats.index(beat),:].sum()

    X.append(x)
    Y.append(y)

# linear regression model
X       = np.array(X)
X       = (X - X.min()) / (X.max() - X.min())
Y       = np.array(Y)
Y       = (Y - Y.min()) / (Y.max() - Y.min())

X       = sm.add_constant(X)
model   = sm.OLS(Y,X)
results = model.fit()
print(results.params)
print(results.summary())    




