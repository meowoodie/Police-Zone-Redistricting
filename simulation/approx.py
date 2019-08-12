import numpy as np
import statsmodels.api as sm
from collections import defaultdict
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
print(results.summary())
print(results.mse_total)

# fig, ax = plt.subplots(figsize=(12, 8))
# fig = sm.graphics.plot_fit(results, "x1", ax=ax)
# plt.show()

import branca
import folium
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pandas import DataFrame
from matplotlib import animation
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_vals_on_map(val_vec, name, path):
    # center point
    center = [33.796480, -84.394220]
    # calculate value according to number of points in each beat
    # vals = DataFrame(list(zip(t_beats[:-10], np.zeros(len(t_beats[:-10])))), columns=['beat', 'value'])
    # for beat, v in zip(t_beats[:-10], values):
    #     vals.loc[vals['beat'] == beat, 'value'] = v
    val_dict = defaultdict(lambda: 0)
    for i in range(len(val_vec)):
        val_dict[t_beats[i]] = val_vec[i]
    # map initialization
    _map     = folium.Map(location=center, zoom_start=13, zoom_control=True, max_zoom=17, min_zoom=10)
    # continuous color map intialization
    print(min(val_vec[1:]), max(val_vec[1:]))
    cm       = branca.colormap.linear.YlOrRd_09.scale(min(val_vec[1:]), max(val_vec[1:])) # colorbar for values
    cm.caption = name
    folium.GeoJson(
        data = open("/Users/woodie/Desktop/workspace/Zoning-Analysis/data/geodata/apd_beat.geojson").read(),
        style_function = lambda feature: {
            'fillColor':   cm(val_dict[feature['properties']["BEAT"]]),
            'fillOpacity': .5,
            'weight':      1.,
            'line_opacity':0.2,
            'highlight':   True,}).add_to(_map)
    _map.add_child(cm)
    # save the map
    _map.save(path)

# plot_vals_on_map(results.params, "coef", "params.html")
# plot_vals_on_map(results.tvalues, "t-values", "tvalues.html")
# plot_vals_on_map(results.pvalues, "p-values", "pvalues.html")
# plot_vals_on_map(results.bse, "std error", "stderror.html")