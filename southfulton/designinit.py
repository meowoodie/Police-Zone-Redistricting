import json
import numpy as np
from shapely import geometry
from sklearn.cluster import KMeans

import branca
import folium
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from collections import defaultdict
from pandas import DataFrame
from matplotlib import animation
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable

def workload_in_polygon(coords, call_table):
    workload = 0
    poly = geometry.Polygon([p for p in coords])
    for call in call_table:
        w   = call[3] + call[4]
        poi = geometry.Point(call[1:3])
        if poi.within(poly):
            workload += w
    return workload

def beat_with_max_workload(grid_table):
    beats_set      = list(set(grid_table[:, 1]))
    beats_set.sort()
    beats_workload = np.array([ 0 for beat in beats_set ])
    for grid in grid_table:
        beat     = grid[1]
        workload = grid[2]
        beats_workload[beats_set.index(beat)] += workload
    beat_ind = beats_workload.argmax()
    return beats_set[beat_ind], beats_set, beats_workload

def split_beat_in_grid_table(beat_id, add_beat_id, grid_table):
    rows   = [ row for row in range(len(grid_table)) if grid_table[row, 1] == beat_id ]
    coords = [ grid[3:5] for grid in grid_table if grid[1] == beat_id ]
    km     = KMeans(
        n_clusters=2, init='random',
        n_init=5, max_iter=100, 
        tol=1e-04, random_state=0)
    beats     = [ beat_id, add_beat_id ]
    assigns   = km.fit_predict(coords)
    new_beats = [ beats[assign] for assign in assigns ]
    # import matplotlib.pyplot as plt
    # colorset  = ["red", "blue"]
    # coords    = np.array(coords)
    # colors    = [ colorset[b] for b in assigns ]
    # plt.scatter(coords[:, 0], coords[:, 1], c=colors)
    # plt.show()
    # change to new beat
    for i in range(len(rows)):
        grid_table[rows[i], 1] = new_beats[i]
    return grid_table

def visualize_grid(grid_table, geo_fname, map_fname, min_val=None, max_val=None):
    # center point
    center = [grid_table[:, 4].mean(), grid_table[:, 3].mean()]
    print(center)

    _, beats_set, beats_workload = beat_with_max_workload(grid_table)

    val_dict = defaultdict(lambda: 0)
    for i in range(len(grid_table)):
        grid_id = int(grid_table[i, 0])
        beat_id = grid_table[i, 1]
        val     = beats_workload[beats_set.index(beat_id)] / 3600
        val_dict[grid_id] = val
    # map initializationc 
    _map       = folium.Map(location=center, zoom_start=11, zoom_control=True, max_zoom=17, min_zoom=8)
    # continuous color map intialization
    if min_val is None and max_val is None:
        min_val = min(beats_workload)/3600
        max_val = max(beats_workload)/3600
    cm         = branca.colormap.linear.YlOrRd_09.scale(min_val, max_val) # colorbar for values
    cm.caption = "workload"
    folium.GeoJson(
        data = open("data/%s.json" % geo_fname).read(),
        style_function = lambda feature: {
            'fillColor':   cm(val_dict[int(feature['id'])]),
            'fillOpacity': .5,
            'weight':      0.2,
            'line_opacity':0.5,
            'highlight':   True,}).add_to(_map)
    _map.add_child(cm)
    # save the map
    _map.save("result/map-%s.html" % map_fname)



if __name__ == "__main__":

    call_fname = "Jan-APR-2019-PD"
    grid_fname = "grids"

    # load call table
    call_table = np.load("data/%s.npy" % call_fname)
    # load grid table
    grid_table = np.load("data/grid-%s.npy" % call_fname)
    # prepare grid table
    # grid_table = []
    # with open("data/%s.json" % grid_fname, "r") as f:
    #     geodata = json.load(f)
    #     for grid in geodata["features"]:
    #         grid_id  = grid["id"]
    #         beat_id  = grid["properties"]["zone"]
    #         coords   = np.array(grid["geometry"]["coordinates"])[0, :4, :]
    #         lats     = coords[:, 0]
    #         lngs     = coords[:, 1]
    #         centroid = [ lats.mean(), lngs.mean() ]
    #         workload = workload_in_polygon(coords, call_table)
    #         grid_table.append([grid_id, beat_id, workload] + centroid)
    #         print(grid_id)
    # np.save("data/grid-%s.npy" % call_fname, np.array(grid_table))

    n_beats = len(set(grid_table[:, 1]))

    for max_n_beats in range(n_beats+1, 20):
        print(max_n_beats)
        # beat id with max 
        added_beat = float(max_n_beats)
        max_workload_beat, beats_set, new_beats_workload = \
            beat_with_max_workload(grid_table)
        print(new_beats_workload)
        print(min(new_beats_workload), max(new_beats_workload))
        print("max beat", max_workload_beat)
        print("added beat", added_beat)
        print(beats_set)

        grid_table = split_beat_in_grid_table(max_workload_beat, added_beat, grid_table)
        visualize_grid(grid_table, grid_fname, map_fname="%s-%d" % (call_fname, max_n_beats))
        np.save("result/grid-%s-nbeat-%d" % (call_fname, max_n_beats), grid_table)




# print(len(geodata))
# print(len(geodata["features"]))
# print(geodata["features"][2])
# print(np.array(grid_table))

