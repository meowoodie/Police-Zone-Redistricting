import arrow
from collections import defaultdict

# with open("/Users/woodie/Desktop/APD_Data/other/911calls.txt", "r", encoding='utf-8', errors='ignore') as f:
#     for line in f.readlines():
#         try:
#             data     = line.strip().split("\t")
#             date     = data[2].strip()
#             call_t   = data[55].strip()
#             lat, lng = data[8].strip(), data[9].strip()
#             disp_t, arv_t, clr_t = data[40].strip(), data[42].strip(), data[45].strip()
#             off_id   = data[50].strip()
#             if off_id != "" and call_t != "" and lat != "" and lng != "" and disp_t != "" and arv_t != "" and clr_t != "":
#                 date   = arrow.get(date[:-4], 'YYYY-MM-DD HH:mm:ss').timestamp
#                 call_t = arrow.get(call_t[:-4], 'YYYY-MM-DD HH:mm:ss').timestamp
#                 lat    = float(lat) / (10 ** (len(lat) - 3))
#                 lng    = float(lng) / (10 ** (len(lng) - 3))
#                 disp_t = date + float(disp_t[:2]) * 3600 + float(disp_t[2:4]) * 60 + float(disp_t[4:])
#                 arv_t  = date + float(arv_t[:2]) * 3600 + float(arv_t[2:4]) * 60 + float(arv_t[4:])
#                 clr_t  = date + float(clr_t[:2]) * 3600 + float(clr_t[2:4]) * 60 + float(clr_t[4:])
#                 if arv_t - disp_t >= 0 and clr_t - arv_t >= 0:
#                     print("\t".join([ str(d) for d in (off_id, lat, lng, call_t, disp_t, arv_t, clr_t) ]))
#         except Exception as e:
#             pass

traces = defaultdict(list)
with open("patrol.trace.txt", "r") as f:
    for line in f.readlines():
        data   = line.strip().split("\t")
        off_id = data[0]
        lat, lng, call_t, disp_t, arv_t, clr_t = [ float(d) for d in data[1:] ]
        # print(off_id, lat, lng, call_t, disp_t, arv_t, clr_t)
        traces[off_id].append({
            "lat": lat, "lng": lng, 
            "call": call_t, "disp": disp_t, "arv": arv_t, "clr": clr_t,
            "dt": arv_t - disp_t})

print(len(traces))
off_list  = list(traces.keys())
off_list.sort()

# PLOTTING TRAJECTORIES ON THE MAP
import branca
import folium
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
# configuration
geojson_path = '/Users/woodie/Desktop/workspace/Zoning-Analysis/data/apd_beat.geojson'
trace        = traces["3761"]
center       = [33.796480, -84.394220]
# data preparation
times     = np.array([ p["call"] for p in trace ]) # len: N
travel_t  = np.array([ p["dt"] for p in trace ])   # N
locations = np.array([ [ p["lat"], -1 * p["lng"] ] for p in trace ]) # N
t_order   = np.argsort(times)
travel_t  = travel_t[t_order]                      # N
locations = locations[t_order]                     # N
# calculate distances and speeds
distances = np.array([ # len: N-1
    abs(locations[i][0] - locations[i-1][0]) + \
    abs(locations[i][1] - locations[i-1][1]) 
    for i in range(1, len(locations)) ])       
speeds    = np.array([ # N-1
    distances[i] / travel_t[i+1] if travel_t[i+1] != 0 else -1 
    for i in range(0, len(travel_t) - 1)])     
idx       = np.array([ # N-1
    i for i in range(0, len(distances))                 
    if travel_t[i+1] < 3600 and travel_t[i+1] > 0 ]) # remove zero travel time

# print(min(np.exp(speeds[idx])), max(np.exp(speeds[idx])))
print(min(travel_t[idx+1]), max(travel_t[idx+1]))

# map initialization
html_path = 'trace.html'
cm        = branca.colormap.linear.YlOrRd_09.scale(min(travel_t[idx+1]), max(travel_t[idx+1]))
m         = folium.Map(
    location=center, zoom_start=11, zoom_control=True, max_zoom=20, min_zoom=9)
m.choropleth(
    geo_data=open(geojson_path).read(),
    fill_color='YlGn',
    fill_opacity=0.1,
    line_opacity=1.,
    highlight=True)
# plot dots and lines
for i in idx:
    folium.CircleMarker(
        location=locations[i+1], color="red", radius=.1).add_to(m)
    folium.PolyLine(
        [locations[i+1], locations[i]], weight=2., color=cm(travel_t[i+1]), opacity=.8).add_to(m)
folium.LayerControl().add_to(m)
m.save(html_path)

