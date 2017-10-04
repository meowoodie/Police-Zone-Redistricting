#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import numpy as np

"""
"""

unknown_dict = {
	"e": (250.0 + 499.0) / 2,
	"j": (5000.0 + 9999.0) / 2,
	"i": (10000.0 + 24999.0) / 2,
	"k": (25000.0 + 49999.0) /2,
	"D": 0.0,
	"null": 0.0
}

def main():
	# Parse the input parameters
	parser = argparse.ArgumentParser(
	  description="Command-line script for interpolating the missing census data")
	parser.add_argument("-b", "--beat", required=True, help="The path of the table associates zipcodes and beats")
	parser.add_argument("-c", "--census", required=True, help="The path of census data by zipcodes")
	parser.add_argument("-o", "--output", required=True, help="The path of output")
	parser.add_argument("-y", "--years", required=True, help="Years the census data has")

	args = parser.parse_args()

	year_list = args.years.split(",")
	# Validate the input params
	assert os.path.exists(args.beat), "beat data file %s does not exist" % args.geo
	assert os.path.exists(args.census), "census data file %s does not exist" % args.census
	assert len(year_list), "years list %s is empty" % args.years 

	with open(args.beat, "r") as beat_h, open(args.census, "r") as census_h:
		# 
		beats_data = [ b.strip("\n").split(",") for b in beat_h ]
		beat_list  = beats_data.pop(0)[1:]
		b_zip_list = [ beat.pop(0) for beat in beats_data ]
		beat_zip_table = np.array([ map(float, beat) for beat in beats_data ])

		#
		census_data    = [ c.strip("\n").split(",") for c in census_h ]
		feature_fields = census_data[0][2:]
		c_zip_list     = list(set([ census[0] for census in census_data[1:] ]))
		census_mat     = np.zeros((len(c_zip_list), len(year_list), len(feature_fields)))

		for census in census_data[1:]:
			zipcode = census.pop(0)
			year    = census.pop(0)
			vals    = map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], census)
			census_mat[c_zip_list.index(zipcode), year_list.index(year)] = vals

		#
		beat_mat = np.zeros((len(beat_list), len(year_list), len(feature_fields)))
		for beatcode in beat_list:
			sum_count = beat_zip_table[:, beat_list.index(beatcode)].sum()
			weights   = [ count/sum_count for count in beat_zip_table[:, beat_list.index(beatcode)] ]
				
			reordered_census = np.zeros((len(b_zip_list), len(year_list), len(feature_fields)))
			for zipcode in b_zip_list:
				reordered_census[b_zip_list.index(zipcode)] = \
					census_mat[c_zip_list.index(zipcode)] * weights[b_zip_list.index(zipcode)]

			beat_mat[beat_list.index(beatcode)] = reordered_census.sum(axis=0)

		with open(args.output, "w") as output_h:
			for beatcode in beat_list:
				for year in year_list:
					line = ",".join(map(str, beat_mat[
						beat_list.index(beatcode), 
						year_list.index(year)].tolist()))
					output_h.write("%s,%s,%s\n" % (beatcode, year, line))

				# reordered_census *= weights


if __name__ == "__main__":
	main()

