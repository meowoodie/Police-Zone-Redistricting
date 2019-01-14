#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time distribution study:
1. Histogram t1 and t2 of domestic violence over each zones
2. Histogram of t1 over each zone
3. Histogram of t2 over each zone
"""

import json
import arrow
from shapely.geometry import Polygon, Point, shape

class T(object):
    """
	T is an simple class for preprocessing raw '911callsforservice' and yielding well-prepared records in a memory-friendly way. 
	"""
    def __init__(self, fhandler, geojson=None):
        self.fhandler = fhandler
        self.polygons = self.geojson2polygons(geojson) if geojson else None

    def __iter__(self):
        """
        yield well-prepared record iteratively for each calling.
        """
        for line in self.fhandler:
            # split data string and get each field
            try:
                _id, crimecode, crimedesc, \
                date, startt, endt, \
                e911t, rect, dispt, enrt, arvt, trant, bookt, clrt, \
                lat, lng, text = line.strip().split("\t")
            except Exception as e:
                print(e)
                continue
            # preprocess into proper data format
            e911t, rect, dispt, enrt, arvt, trant, bookt, clrt = [ 
                self.tstr2arrow(startt, tstr) if tstr.strip() is not "" else None
                for tstr in [e911t, rect, dispt, enrt, arvt, trant, bookt, clrt] ]
            lat, lng = [ float(lat[:3] + "." + lat[3:]), -1 * float(lng[:3] + "." + lng[3:]) ] \
                if lat.strip() is not "" and lng.strip() is not "" else [ None, None ]
            zone  = self.zone4point((lng, lat), self.polygons) if self.polygons and lat and lng else None
            # calculate t1, t2, t3
            t1 = (dispt - e911t).seconds if dispt and e911t else None
            t2 = (arvt - dispt).seconds if arvt and dispt else None
            t3 = (clrt - arvt).seconds if clrt and arvt else None
            yield t1, t2, t3, lat, lng, zone

    @staticmethod
    def tstr2arrow(date, tstr):
        """convert time string in the format of 'hhmmss' into arrow object where 'hh' is hour, 'mm' is minutes, 'ss' is seconds."""
        date = date[:10].strip()
        tstr = tstr.strip()
        try:
            t = arrow.get(date + " " + tstr, 'YYYY-MM-DD HHmmss')
        except Exception as e:
            print(e)
            t = None
        return t
    
    @staticmethod
    def geojson2polygons(geojson):
        """parse geojson file, extract polygons and indexed by their ID."""
        polygons = {}
        with open(geojson, "r") as f:
            geo_obj = json.load(f)
            for feature in geo_obj["features"]:
                name    = feature["properties"]["ID"]
                polygon = shape(feature["geometry"])
                polygons[name] = polygon
            return polygons

    @staticmethod
    def zone4point(point, polygons):
        """get zone ID of the point."""
        for name in polygons:
            if polygons[name].contains(Point(point)):
                return name
        return None

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import gamma, kstest
from collections import defaultdict
from matplotlib.backends.backend_pdf import PdfPages

def plot_t_distribution(tuples, savepath, t_lim, t_annotation="t1"):
    tdist = defaultdict(lambda: [])
    for t, zone in tuples:
        tdist[zone].append(t)
    
    cm = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    with PdfPages(savepath) as pdf:
        fig, ax = plt.subplots(figsize=(8, 6))
        zones   = list(tdist.keys())
        zones.sort()
        for zone in zones:
            print(zone)
            print(len(tdist[zone]))
            print(max(tdist[zone]))
            # fitting
            shape, loc, scale = gamma.fit(tdist[zone], floc=0)
            mu = shape * scale
            # check goodness of the fit
            ks, _ = kstest(tdist[zone], gamma(shape, scale=scale).cdf)
            # plotting
            x = np.linspace(0, t_lim, 1000)
            y = gamma.pdf(x, shape, 0, scale)
            ax.plot(x, y, label=r'zone %s ($n=%d$, $k=%.2f$, $\theta=%.2f$, $\mu=%.2f$, $p=%.3f$)' % (zone, len(tdist[zone]), shape, scale, mu, ks), c=cm[zone-1])
            # plt.axvline(x=mu, linestyle='-.', c=cm[zone-1], linewidth=1)
        ax.set(xlabel=t_annotation, ylabel="frequency")
        ax.set_title("Distribution of all categories over zones", fontweight="bold")
        ax.legend(frameon=False)
        pdf.savefig(fig)
        plt.clf()

if __name__ == "__main__":
    domvio_911calls  = "/Users/woodie/Desktop/workspace/Zoning-Analysis/data/casestudy/domvio.rawdata.txt"
    all_911calls     = "/Users/woodie/Desktop/workspace/Crime-Pattern-Detection-for-APD/data/records_380k/raw_data.txt"
    apd_zone_geojson = "/Users/woodie/Desktop/workspace/Zoning-Analysis/data/apd_zone.geojson"
    with open(all_911calls, "r", encoding="utf8", errors='ignore') as f:
        tuples = [ [ t1, t2, t3, zone ] 
                   for t1, t2, t3, lat, lng, zone in T(f, geojson=apd_zone_geojson) 
                   if zone and zone != 50 ]

        t1_tuples = [ [ t1, zone ] for t1, t2, t3, zone in tuples if zone and t1 and t1 > 0 and t1 < 4000]
        t2_tuples = [ [ t2, zone ] for t1, t2, t3, zone in tuples if zone and t2 and t2 > 0 and t2 < 4000]
        t3_tuples = [ [ t3, zone ] for t1, t2, t3, zone in tuples if zone and t3 and t3 > 0 and t3 < 50000]

        savepath = "/Users/woodie/Desktop/workspace/Zoning-Analysis/data/casestudy/all-t1.pdf"
        plot_t_distribution(t1_tuples, savepath, 4000, t_annotation=r'$t_1$')
        savepath = "/Users/woodie/Desktop/workspace/Zoning-Analysis/data/casestudy/all-t2.pdf"
        plot_t_distribution(t2_tuples, savepath, 4000, t_annotation=r'$t_2$')
        savepath = "/Users/woodie/Desktop/workspace/Zoning-Analysis/data/casestudy/all-t3.pdf"
        plot_t_distribution(t3_tuples, savepath, 50000, t_annotation=r'$t_3$')

