#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
from statsmodels.tsa.api import VAR

"""
"""

lag          = 2
zipcode_list = [
	'30032', '30309', '30308', '30305', '30307', '30306', '30327', 
	'30326', '30303', '30324', '30334', '30336', '30331', '30332', 
	'30354', '30318', '30319', '30316', '30317', '30314', '30315', 
	'30312', '30313', '30310', '30311', '30342', '30344', '30363']
year_list    = ["2011", "2012", "2013", "2014", "2015"]
future_list  = ["2016", "2017", "2018"]
attr_list    = [
	"total population", "number of population age 15-34", "mid-age 35-54", "median age", 
	"number of establishments", "paid employees", "quarter payroll(first quarter)", 
	"annual payroll", "high school graduate percentage", "total household units", 
	"median income(households)", "poverty percentage(all people)"]

Xs = np.zeros((len(attr_list) , len(year_list), len(zipcode_list)))

unknown_dict = {
	"e": (250.0 + 499.0) / 2,
	"j": (5000.0 + 9999.0) / 2,
	"i": (10000.0 + 24999.0) / 2,
	"k": (25000.0 + 49999.0) /2,
	"D": 0.0,
	"null": 0.0
}

start_flag = True
for line in sys.stdin:
	if start_flag:
		start_flag = False
		continue

	data = line.strip("\n").split(",")
	zipcode = data.pop(0)
	year    = data.pop(0)

	formatted_data = map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], data)

	for i in range(len(formatted_data)):
		Xs[i, year_list.index(year), zipcode_list.index(zipcode)] = formatted_data[i]

P = np.zeros((len(attr_list), len(future_list), len(zipcode_list)))
for i in range(len(attr_list)):
	X     = Xs[i]
	noise = np.random.rand(X.shape[0], X.shape[1])
	X     += noise

	model_xi = VAR(X)
	result   = model_xi.fit(lag)
	P[i]     = result.forecast(X, len(future_list))

for i in range(len(zipcode_list)):
	for j in range(len(future_list)):
		output = [zipcode_list[i]] + [future_list[j]] + map(str, P[:, j, i].tolist())
		print ",".join(output)





	


