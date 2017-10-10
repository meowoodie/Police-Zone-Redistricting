#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

def plot_beat_heat_map(beat_geo_dict, data_mat, year_list, beat_list, feature_name):
	"""
	"""
	print beat_geo_dict.keys()
	print data_mat.shape
	min_c  = data_mat.min()
	max_c  = data_mat.max()


	for year in year_list:
		fig, ax = plt.subplots(1)
		cm = plt.cm.get_cmap('RdYlBu_r')
		plt.ylim(33.62, 33.90)
		plt.xlim(-84.56, -84.24)
		plt.title("%s in %s" % (feature_name, year))

		for beat in beat_list:
			points = np.array(beat_geo_dict[beat])
			if len(points) <= 0:
				continue
			ys = points[:, 0]
			xs = points[:, 1]
			# c  = (data_mat[beat_list.index(beat), year_list.index(year)] - min_c)/(max_c - min_c)
			c  = data_mat[beat_list.index(beat), year_list.index(year)]
			cs = [ c for i in range(len(xs)) ]
			sc = plt.scatter(xs, ys, c=cs, vmin=min_c, vmax=max_c, s=2, lw=0, cmap=cm)

		plt.colorbar(sc)
		fig.savefig("results/%s_%s.png" % (feature_name, year))
		plt.close(fig)
		# plt.show()

def main_census():
	# Parse the input parameters
	parser = argparse.ArgumentParser(
	  description="Command-line script for interpolating the missing census data")
	parser.add_argument("-g", "--geo", required=True, help="The path of data file that contains geolocation information")
	parser.add_argument("-d", "--data", required=True, help="The path of data file which will be ploted on map")
	args = parser.parse_args()

	assert os.path.exists(args.geo), "geo data file %s does not exist" % args.geo
	assert os.path.exists(args.data), "census data file %s does not exist" % args.data

	with open(args.geo, "r") as geo_h, open(args.data, "r") as data_h:
		# Get Beat-Geolocation dictionary
		beat_geo_dict = defaultdict(list)
		flag = True
		for g in geo_h:
			if flag:
				flag = False
				continue
			items = g.strip("\n").split("\t")
			if items[6].strip() is not "":
				if float(items[3]) < 34.0 and float(items[3]) > 32.0 and \
				   float(items[4]) < -84.0 and float(items[4]) > -85.0:
					# print items[6].strip(), items[3], items[4]
					beat_geo_dict[items[6].strip()].append([float(items[3]), float(items[4])])

		# Extract the fields of years and beats, and the data entries
		census_data    = [ d.strip("\n").split(",") for d in data_h ]
		beat_list      = list(set([ census[0] for census in census_data[1:] ]))
		year_list      = list(set([ census[1] for census in census_data[1:] ]))
		feature_fields = census_data[0][2:]
		census_mat     = np.zeros((len(beat_list), len(year_list), len(feature_fields)))
		for census in census_data[1:]:
			census_mat[beat_list.index(census[0]), year_list.index(census[1])] = \
				np.array(map(lambda x: float(x), census[2:]))

		for feature_name in feature_fields:
			data_mat = np.zeros((len(beat_list), len(year_list)))
			for beat_ind in range(len(beat_list)):
				for year_ind in range(len(year_list)):
					data_mat[beat_ind, year_ind] = census_mat[beat_ind, year_ind, feature_fields.index(feature_name)]
			plot_beat_heat_map(beat_geo_dict, data_mat, year_list, beat_list, feature_name)

def main_workload():

	# Parse the input parameters
	parser = argparse.ArgumentParser(
	  description="Command-line script for interpolating the missing census data")
	parser.add_argument("-g", "--geo", required=True, help="The path of data file that contains geolocation information")
	parser.add_argument("-d", "--data", required=True, help="The path of data file which will be ploted on map")
	args = parser.parse_args()

	assert os.path.exists(args.geo), "geo data file %s does not exist" % args.geo
	assert os.path.exists(args.data), "census data file %s does not exist" % args.data

	with open(args.geo, "r") as geo_h, open(args.data, "r") as data_h:
		# Get Beat-Geolocation dictionary
		beat_geo_dict = defaultdict(list)
		flag = True
		for g in geo_h:
			if flag:
				flag = False
				continue
			items = g.strip("\n").split("\t")
			if items[6].strip() is not "":
				if float(items[3]) < 34.0 and float(items[3]) > 32.0 and \
				   float(items[4]) < -84.0 and float(items[4]) > -85.0:
					# print items[6].strip(), items[3], items[4]
					beat_geo_dict[items[6].strip()].append([float(items[3]), float(items[4])])

		# Extract the fields of years and beats, and the data entries
		rawdata   = [ d.strip("\r\n").split(",") for d in data_h ]
		year_list = rawdata.pop(0)[1:]
		print len(year_list), year_list
		beat_list = [ item.pop(0) for item in rawdata ]
		print len(beat_list), beat_list
		data_mat  = np.array(rawdata).astype(float)

		plot_beat_heat_map(beat_geo_dict, data_mat, year_list, beat_list, "workload")




if __name__ == "__main__":
	main_workload()
	# main_census()