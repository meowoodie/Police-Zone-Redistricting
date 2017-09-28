import sys
import numpy as np
from statsmodels.tsa.api import VAR


lag    = 2

zipcode_list = [
	"30314", "30305", "30318", "30306", "30363", "30317", 
	"30307", "30308", "30303", "30309", "30324", "30334", 
	"30313", "30332", "30312", "30326", "30327"]
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
	"D": 0.0,
	"null": 0.0
}

ind = 0
for line in sys.stdin:
	if ind == 0:
		ind += 1
		continue
	data = line.strip("\n").split(",")
	zipcode = data.pop(0)
	year    = data.pop(0)

	formatted_data = map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], data)

	for i in range(len(formatted_data)):
		Xs[i, year_list.index(year), zipcode_list.index(zipcode)] = formatted_data[i]

P = np.zeros((len(attr_list), len(future_list), len(zipcode_list)))
for i in range(len(attr_list)):
	X = Xs[i]
	# zeros_cols_inds = X.any(axis=0).tolist().index(False) 
	# X = np.delete(X, zeros_cols_inds, axis=1)
	noise = np.random.rand(X.shape[0], X.shape[1])
	X = noise + X

	model_xi = VAR(X)
	result   = model_xi.fit(lag)
	pred     = result.forecast(X, len(future_list))
	
	P[i] = pred

# P = P.reshape(len(zipcode_list), len(future_list), len(attr_list))

for i in range(len(zipcode_list)):
	for j in range(len(future_list)):
		output = [zipcode_list[i]] + [future_list[j]] + map(str, P[:, j, i].tolist())
		print ",".join(output)





	



