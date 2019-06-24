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
        traces[off_id].append({"lat": lat, "lng": lng, "call": call_t, "disp": disp_t, "arv": arv_t, "clr": clr_t})

print(len(traces))
off_list  = list(traces.keys())
off_list.sort()
locations = [ [ p["lat"], -1 * p["lng"] ] for p in traces["3761"] ]

import folium
import webbrowser
import numpy as np
import matplotlib.pyplot as plt

geojson_path = '/Users/woodie/Desktop/workspace/Zoning-Analysis/data/apd_beat.geojson'
html_path    = 'trace.html'
center       = [33.796480, -84.394220]

m = folium.Map(location=center, zoom_start=11, zoom_control=True, max_zoom=15, min_zoom=9)
m.choropleth(
    geo_data=open(geojson_path).read(),
    fill_color='YlGn',
    fill_opacity=0.1,
    line_opacity=1.,
    highlight=True
)

for coord in locations:
    folium.CircleMarker(location=coord, color="red", radius=1).add_to(m)
folium.LayerControl().add_to(m)
m.save(html_path)