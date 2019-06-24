#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A set of helper functions for preprocessing or visualization.
'''

import json
import arrow
import folium
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial
from pandas import DataFrame
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

BEATS_SET = [
    '050', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110',
    '111', '112', '113', '114', '201', '202', '203', '204', '205', '206', '207',
    '208', '209', '210', '211', '212', '213', '301', '302', '303', '304', '305',
    '306', '307', '308', '309', '310', '311', '312', '313', '401', '402', '403',
    '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414',
    '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511',
    '512', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610',
    '611', '612']

def plot_intensities4beats(
        locations=None, 
        geojson_path='/Users/woodie/Desktop/workspace/Zoning-Analysis/data/apd_beat.geojson',
        html_path='intensity_map.html',
        center=[33.796480, -84.394220]):
    '''plot background rate intensities over a map.'''
    # color map for points
    # color_map = ['red', 'blue', 'black', 'purple', 'orange', 'brown', 'grey']
    # label_set = ['burglary', 'pedrobbery', 'DIJAWAN_ADAMS', 'JAYDARIOUS_MORRISON', 'JULIAN_TUCKER', 'THADDEUS_TODD']
    # calculate intensity according to number of points in each beat
    intensities = DataFrame(list(zip(BEATS_SET, np.zeros(len(BEATS_SET)))), columns=['BEAT', 'intensity'])
    # for beat, mu in zip(beats_set, Mu):
    #     intensities.loc[intensities['BEAT'] == beat, 'intensity'] = 0.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(intensities)
    map = folium.Map(location=center, zoom_start=13, zoom_control=True, max_zoom=17, min_zoom=10)
    map.choropleth(
        geo_data=open(geojson_path).read(),
        data=intensities,
        columns=['BEAT', 'intensity'],
        key_on='feature.properties.BEAT',
        fill_color='BuPu', # 'YlGn',
        fill_opacity=0.1,
        line_opacity=1.,
        highlight=True,
        legend_name='Intensity'
    )
    for coord in locations:
        # color = color_map[label_set.index(label)] if label in label_set else color_map[-1]
        folium.CircleMarker(location=coord, color="red", radius=1).add_to(map)

    map.save(html_path)

if __name__ == '__main__':
    data = np.load('../../Spatio-Temporal-Point-Process-Simulator/data/apd.robbery.perweek.npy')
    data = np.concatenate(data, axis=0)
    pois = data[:, 1:]
    print(pois[:5,:])
    print(pois.shape)

    plot_intensities4beats(pois)


