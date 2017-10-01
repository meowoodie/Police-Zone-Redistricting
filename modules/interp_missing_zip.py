import sys
import json
import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

unknown_dict = {
	"e": (250.0 + 499.0) / 2,
	"j": (5000.0 + 9999.0) / 2,
	"i": (10000.0 + 24999.0) / 2,
	"k": (25000.0 + 49999.0) /2,
	"D": 0.0,
	"null": 0.0
}

# attr_list = [
#      "total population","number of population age 15-34",
#      "mid-age 35-54","median age","number of establishments","paid employees",
#      "quarter payroll(first quarter)","annual payroll","high school graduate percentage",
#      "total household units","median income(households)","poverty percentage(all people)"]

year_list = ["2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]

zip_list  = [
	'30032', '30309', '30308', '30305', '30307', '30306', '30327', 
	'30326', '30303', '30324', '30334', '30336', '30331', '30332', 
	'30354', '30318', '30319', '30316', '30317', '30314', '30315', 
	'30312', '30313', '30310', '30311', '30342', '30344', '30363']
 
with open("data/zip_centers.csv", "r") as f1, \
     open("data/27zip_census_data_with_pred.csv", "r") as f2:

     # Step 1: preprocessing of zip_census_data
     # - Organize zip, year, cencus into a dictionary
     attr_list = list(itertools.islice(f2, 1))[0].strip("\r\n").split(",")[2:] # Attribute list

     _ = [ line.strip("\r\n").split(",") for line in f2 ]
     zip_year_census_mat = np.zeros((len(zip_list), len(year_list), len(attr_list)))

     for items in _ :
     	zip_year_census_mat[zip_list.index(items[0]), year_list.index(items[1])] = np.array(map(
     		lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], 
     		items[2:]))

     # Step 2: preprocessing of zip_centers
     zip_centers_list = [ [ item.strip("\'") for item in line.strip("\r\n").split(",") ] for line in f1 ]
     zip_centers_dict = {}
     for zipcode, lat, lon in zip_centers_list:
     	zip_centers_dict[zipcode] = [float(lat), float(lon)]

     # Step 3: preparation of training data
     # - Data extraction
     train_geo_list = np.array([ zip_centers_dict[zipcode] for zipcode in zip_list ])
     train_x_list   = train_geo_list[:, 0]
     train_y_list   = train_geo_list[:, 1]

     # Step 4: interpolation for each (year, attribute)
     for i in range(len(year_list)):

          interp_mat = np.zeros((len(attr_list), len(zip_centers_dict.keys())))

          for j in range(len(attr_list)):
               train_val_list = zip_year_census_mat[:, i, j]
               # print train_x_list.shape
               # print train_y_list.shape
               # print train_val_list.shape

               interp_func = interpolate.interp2d(train_x_list, train_y_list, train_val_list, kind='linear')

               full_zip_centers = np.array(zip_centers_dict.values())
               full_x_list      = full_zip_centers[:, 0]
               full_y_list      = full_zip_centers[:, 1]
               full_val_list    = interp_func(full_x_list, full_y_list).diagonal()

               interp_mat[j]    = full_val_list
               # print full_x_list
               # print full_y_list

               # fig, ax = plt.subplots(1)
               # cm = plt.cm.get_cmap('RdYlBu')
               # plt.xlim(min(full_x_list), max(full_x_list))
               # plt.ylim(min(full_y_list), max(full_y_list))
               # plt.title("Original data of %s in %s" % (attr_list[j], year_list[i]))
               # plt.grid()
               # sc = plt.scatter(train_x_list, train_y_list, c=train_val_list, vmin=min(full_val_list), vmax=max(full_val_list), s=35, cmap=cm)
               # plt.colorbar(sc)
               # fig.savefig("results/%s_%s_origin.png" % (year_list[i], attr_list[j]))
               # plt.close(fig)    

               # fig, ax = plt.subplots(1)
               # cm = plt.cm.get_cmap('RdYlBu')
               # plt.xlim(min(full_x_list), max(full_x_list))
               # plt.ylim(min(full_y_list), max(full_y_list))
               # plt.title("Interpolated data of %s in %s" % (attr_list[j], year_list[i]))
               # plt.grid()
               # sc = plt.scatter(full_x_list, full_y_list, c=full_val_list, vmin=min(full_val_list), vmax=max(full_val_list), s=35, cmap=cm)
               # plt.colorbar(sc)
               # fig.savefig("results/%s_%s_interp.png" % (year_list[i], attr_list[j]))
               # plt.close(fig)
          zip_attr_mat = interp_mat.transpose().tolist()
          for k in range(len(zip_centers_dict.keys())):
               print "%s,%s,%s" % (
                    zip_centers_dict.keys()[k], 
                    year_list[i], 
                    ",".join(map(
                         lambda x: str(x) if x >= 0.0 else "0.0", zip_attr_mat[k])))


