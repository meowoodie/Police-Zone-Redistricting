import geopandas as gpd
import numpy as np
import json
from shapely import geometry
from sklearn.cluster import KMeans
import math

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
from designinit import beat_with_max_workload

# merge grids in the same beat to get zone boundary
def get_beat_bound(geo_fname,fname):
    grid_table = np.load("result/grid-%s.npy" % fname)
    grid_gpd = gpd.read_file("data/%s.json" % geo_fname)
    grid_gpd["zone"] = grid_table[:,1]
    beat_boundary_gpd = grid_gpd[['zone','geometry']]
    beat_regions = beat_boundary_gpd.dissolve(by='zone')
    
    beat_regions.to_file("result/boundary-%s.json" % fname, driver="GeoJSON")
    boundary_geo_fname = "result/boundary-%s.json" % fname
    with open("result/boundary-%s.json" % fname,'r', encoding='utf-8-sig') as f:
        beat_regions_json = json.load(f)
        
    return beat_regions_json

def visualize_grid(geo_boundary, grid_table, geo_fname, map_fname, min_val=None, max_val=None):
    # center point
    center = [grid_table[:, 4].mean(), grid_table[:, 3].mean()]

    _, beats_set, beats_workload = beat_with_max_workload(grid_table)

    val_dict = defaultdict(lambda: 0)
    for i in range(len(grid_table)):
        grid_id = int(grid_table[i, 0])
        beat_id = grid_table[i, 1]
        val     = beats_workload[beats_set.index(beat_id)] / 3600
#        val_dict[grid_id] = val
        val_dict[grid_id] = math.log(val)
        
    # map initialization
    _map       = folium.Map(location=center, zoom_start=11, zoom_control=True, max_zoom=17, min_zoom=8)
    # continuous color map intialization
    if min_val is None and max_val is None:
        min_val = min(beats_workload)/3600
        max_val = max(beats_workload)/3600
    cm         = branca.colormap.linear.YlOrRd_09.scale(min_val, max_val) # colorbar for values
    cm.caption = "workload (log)"
    folium.GeoJson(
        data = open("data/%s.json" % geo_fname).read(),
        style_function = lambda feature: {
            'fillColor':   cm(val_dict[int(feature['id'])]),
            'fillOpacity': .5,
            'weight':      0.2,
            'line_opacity':0.5,
            'highlight':   True,}).add_to(_map)
    
    folium.GeoJson(geo_boundary, name='beat boundary',style_function=lambda feature: {
        'color': 'grey',
        'fillOpacity': 0,
        'weight': 1.7
        }).add_to(_map)
    
    _map.add_child(cm)
    # save the map
    _map.save("result/map-%s.html" % map_fname)
    
if __name__ == "__main__":
    # load data
#    greedy_fname = "regression-workload-2020-nbeat-15"
#    redesign_fname   = "redesign-regression-workload-2020-nbeat-15"
    
    greedy_fname   = "regression-workload-2021-nbeat-15"
    redesign_fname = "redesign-regression-workload-2021-nbeat-15"
    
    greedy_design  = np.load("result/grid-%s.npy" % greedy_fname)
    redesign  = np.load("result/grid-%s.npy" % redesign_fname)

    grid_fname = "grids"
    
    greedy_geo = get_beat_bound(grid_fname,greedy_fname)
    redesign_geo = get_beat_bound(grid_fname,redesign_fname)
    
    _, _, init_beats_workload  = beat_with_max_workload(greedy_design)
    _, _, final_beats_workload  = beat_with_max_workload(redesign)
    
    ex_fname = "Jan-APR-2019-PD"
    ex_design = np.load("data/grid-%s.npy" % ex_fname)
    # ex_geo = get_beat_bound(grid_fname,ex_fname)
    _, _, ex_beats_workload  = beat_with_max_workload(ex_design)
    
#    cm_min_val = min([min(init_beats_workload)/3600, min(final_beats_workload)/3600])
#    cm_max_val = max([max(init_beats_workload)/3600, max(final_beats_workload)/3600])
    
    cm_min_val = math.log(min([min(init_beats_workload)/3600, min(final_beats_workload)/3600, min(ex_beats_workload)/3600]))
    cm_max_val = math.log(max([max(init_beats_workload)/3600, max(final_beats_workload)/3600, max(ex_beats_workload)/3600]))
    print(cm_min_val,cm_max_val)
    
    visualize_grid(greedy_geo, greedy_design, grid_fname, map_fname=greedy_fname,min_val=cm_min_val,max_val=cm_max_val)
    visualize_grid(redesign_geo, redesign, grid_fname, map_fname=redesign_fname,min_val=cm_min_val,max_val=cm_max_val)
    
    # visualize_grid(ex_geo, ex_design, grid_fname, map_fname=ex_fname,min_val=cm_min_val,max_val=cm_max_val)
#    visualize_grid(ex_geo, ex_design, grid_fname, map_fname=ex_fname)