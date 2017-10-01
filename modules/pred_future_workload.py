#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import statsmodels.api as sm

attr_list = [
	"total_pop", "pop_15_34", "mid_age_35_54", "median_age", 
	"establishment", "paid_employees", "quarter_payroll", "annual_payroll", 
	"high_school_per", "house_units", "median_income", "poverty_per"]

with open("data/workload_beat_year_data.csv", "r") as f1, \
     open("data/beat_census_data.csv", "r") as f2:

	# Preprocess of beat_year_data
	beat_year_map = np.array([ line.strip("\n").split(",") for line in f1 ])
	y_years = np.delete(beat_year_map[0], 0, axis=0).astype(int).tolist()
	y_beats = np.delete(beat_year_map.transpose()[0], 0, axis=0).astype(int).tolist()
	_       = np.delete(beat_year_map, 0, axis=0)
	y_mat   = np.delete(_, 0, axis=1).astype(int)

	# Preprocess of beat_census_data
	beat_census_data = [ line.strip("\n").split(",") for line in f2 ]
	x_years = map(int, list(set(np.array(beat_census_data).transpose()[1].tolist())))
	x_beats = map(int, list(set(np.array(beat_census_data).transpose()[0].tolist())))
	x_years.sort()
	x_beats.sort()

	x_census_mat = np.zeros((len(x_beats), len(x_years), len(beat_census_data[0])-2))
	for x_census in beat_census_data:
		x_beat   = int(x_census.pop(0))
		x_year   = int(x_census.pop(0))
		x_census = np.array(map(float, x_census))
		x_census_mat[x_beats.index(x_beat), x_years.index(x_year)] = x_census

	# ys and Xs
	ys = []
	Xs = []
	for year in y_years:
		for beat in y_beats:
			if beat in x_beats and year in x_years and year-1 in y_years:
				y = y_mat[y_beats.index(beat), y_years.index(year)].tolist()
				X = x_census_mat[x_beats.index(beat), x_years.index(year)].tolist() +\
					[y_mat[y_beats.index(beat), y_years.index(year-1)], year]
				ys.append(y)
				Xs.append(X)

	Xs = np.array(Xs)
	Xs = sm.add_constant(Xs)
	ys = np.array(ys)

	# Linear regression
	model   = sm.OLS(ys, Xs)
	results = model.fit()
	print results.summary()
