#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import os
import argparse
import numpy as np
import statsmodels.api as sm

def main():

	# Parse the input parameters
	parser = argparse.ArgumentParser(
	  description="Command-line script for interpolating the missing census data")
	parser.add_argument("-w", "--workload", required=True, help="The path of geo data by zipcodes")
	parser.add_argument("-c", "--census", required=True, help="The path of output")
	parser.add_argument("-o", "--output", required=True, help="The path of output")
	parser.add_argument("-f", "--future", required=True, help="Future years we wanna estimate")
	args = parser.parse_args()

	predict_years = map(int, args.future.split(","))
	# Validate the input params
	assert os.path.exists(args.census), "census data file %s does not exist" % args.census
	assert os.path.exists(args.workload), "workload data file %s does not exist" % args.workload
	assert len(predict_years), "Future list %s is empty" % args.future

	with open(args.workload, "r") as workload_h, open(args.census, "r") as census_h:

		# Preprocess of beat_year_data
		beat_year_map = np.array([ w.strip("\n").split(",") for w in workload_h ])
		y_years = np.delete(beat_year_map[0], 0, axis=0).astype(int).tolist()
		y_beats = np.delete(beat_year_map.transpose()[0], 0, axis=0).astype(int).tolist()
		_       = np.delete(beat_year_map, 0, axis=0)
		y_mat   = np.delete(_, 0, axis=1).astype(int)

		print len(y_beats), y_beats
		print len(y_years), y_years
		print y_mat.shape

		# Preprocess of beat_census_data
		beat_census_data = [ c.strip("\n").split(",") for c in census_h ]
		x_years = map(int, list(set(np.array(beat_census_data).transpose()[1].tolist())))
		x_beats = map(int, list(set(np.array(beat_census_data).transpose()[0].tolist())))

		print len(x_beats), x_beats
		print len(x_years), x_years

		x_census_mat = np.zeros((len(x_beats), len(x_years), len(beat_census_data[0])-2))
		for x_census in beat_census_data:
			x_beat   = int(x_census.pop(0))
			x_year   = int(x_census.pop(0))
			x_census = np.array(map(float, x_census))
			x_census_mat[x_beats.index(x_beat), x_years.index(x_year)] = x_census

		print x_census_mat.shape

		# ys and Xs
		ys = []
		Xs = []
		for year in y_years:
			for beat in y_beats:
				if beat in x_beats and year in x_years and year-1 in y_years:
					y = y_mat[y_beats.index(beat), y_years.index(year)].tolist()
					X = x_census_mat[x_beats.index(beat), x_years.index(year)].tolist() + \
						[y_mat[y_beats.index(beat), y_years.index(year-1)], year]
					ys.append(y)
					Xs.append(X)

		Xs = np.array(Xs)
		ys = np.array(ys)

		# Linear regression
		model   = sm.OLS(ys, Xs)
		# results = model.fit()
		results = model.fit_regularized(L1_wt=1)
		
		pred_ys = []
		last_y  = []
		for year in predict_years:
			_Xs    = []
			for beat in y_beats:
				if predict_years.index(year) == 0:
					_X = x_census_mat[x_beats.index(beat), x_years.index(year)].tolist() + \
						[y_mat[y_beats.index(beat), y_years.index(year-1)], year]
				else:
					_X = x_census_mat[x_beats.index(beat), x_years.index(year)].tolist() + \
						[last_y[y_beats.index(beat)], year]
				_Xs.append(_X)
			pred_y = results.predict(_Xs)
			last_y = pred_y
			pred_ys.append(pred_y)

		pred_ys = np.array(pred_ys).transpose().tolist()

		with open(args.output, "w") as output_h:
			output_h.write("%s,%s\n" % ("beat", ",".join(map(str, predict_years))))
			for beat in y_beats:
				output_h.write("%s,%s\n" % (beat, ",".join(map(str, pred_ys[y_beats.index(beat)]))))

if __name__ == "__main__":
	main()

