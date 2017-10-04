#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import numpy as np
from statsmodels.tsa.api import VAR

"""
"""

unknown_dict = {
	"e": (250.0 + 499.0) / 2,
	"j": (5000.0 + 9999.0) / 2,
	"i": (10000.0 + 24999.0) / 2,
	"k": (25000.0 + 49999.0) / 2,
	"D": 0.0,
	"null": 0.0
}

def main():

	# Parse the input parameters
	parser = argparse.ArgumentParser(
	  description="Command-line script for interpolating the missing census data")
	parser.add_argument("-c", "--census", required=True, help="The path of geo data by zipcodes")
	parser.add_argument("-o", "--output", required=True, help="The path of output")
	parser.add_argument("-y", "--years", required=True, help="Years the census data has")
	parser.add_argument("-f", "--future", required=True, help="Future years we wanna estimate")
	parser.add_argument("-l", "--lag", default=1, type=int, required=True, help="Lag of the AR model")
	args = parser.parse_args()

	year_list   = args.years.split(",")
	future_list = args.future.split(",")
	# Validate the input params
	assert os.path.exists(args.census), "census data file %s does not exist" % args.census
	assert len(year_list), "Years list %s is empty" % args.years 
	assert len(future_list), "Future list %s is empty" % args.future 

	# Read data from file
	with open(args.census, "r") as census_h:
		census_data    = [ c.strip("\n").split(",") for c in census_h ]
		feature_fields = census_data[0][2:]
		zip_list       = list(set([ census[0] for census in census_data[1:] ]))

		#
		# Xs = np.zeros((len(feature_fields), len(year_list), len(zip_list)))
		Xs = np.zeros((len(zip_list), len(year_list), len(feature_fields)))
		for census in census_data[1:]:
			zipcode = census.pop(0)
			year    = census.pop(0)
			vals    = map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], census)
			Xs[zip_list.index(zipcode), year_list.index(year)] = vals
			# for val_ind in range(len(feature_fields)):
			# 	Xs[val_ind, year_list.index(year), zip_list.index(zipcode)] = vals[val_ind]

		# 
		# preds = np.zeros((len(feature_fields), len(future_list), len(zip_list)))
		preds = np.zeros((len(zip_list), len(future_list), len(feature_fields)))
		for val_ind in range(len(feature_fields)):
			X     = Xs[:, :, val_ind].transpose()
			noise = np.random.rand(X.shape[0], X.shape[1])
			X     += noise

			model_Xi = VAR(X)
			result   = model_Xi.fit(args.lag)
			preds[:, :, val_ind] = result.forecast(X, len(future_list)).transpose()

		with open(args.output, "w") as output_h:
			for zip_ind in range(len(zip_list)):
				for year_ind in range(len(future_list)):
					output_h.write("%s,%s,%s\n" % ( \
						zip_list[zip_ind], 
						future_list[year_ind], 
						",".join(map(str, preds[zip_ind, year_ind, :].tolist()))))

if __name__ == "__main__":
	main()		

# start_flag = True
# for line in sys.stdin:
# 	if start_flag:
# 		start_flag = False
# 		continue

# 	data = line.strip("\n").split(",")
# 	zipcode = data.pop(0)
# 	year    = data.pop(0)

# 	formatted_data = map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], data)

# 	for i in range(len(formatted_data)):
# 		Xs[i, year_list.index(year), zipcode_list.index(zipcode)] = formatted_data[i]

# P = np.zeros((len(attr_list), len(future_list), len(zipcode_list)))
# for i in range(len(attr_list)):
# 	X     = Xs[i]
# 	noise = np.random.rand(X.shape[0], X.shape[1])
# 	X     += noise

# 	model_xi = VAR(X)
# 	result   = model_xi.fit(lag)
# 	P[i]     = result.forecast(X, len(future_list))

# for i in range(len(zipcode_list)):
# 	for j in range(len(future_list)):
# 		output = [zipcode_list[i]] + [future_list[j]] + map(str, P[:, j, i].tolist())
# 		print ",".join(output)
