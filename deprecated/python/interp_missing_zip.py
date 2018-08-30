#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interpolate Missing census Data in terms of Zipcodes

Params:
1. --geo (-g): The path of geo data by zipcodes. 
     Data fields: [zipcode] [latitude] [longitude]
2. --census (-c): The path of census data by zipcodes 
     Data fields (declaration at the first row): [zipcode] [year] [feature_1] ... [feature_N]
"""

import os
import argparse
import numpy as np

unknown_dict = {
     "e": (250.0 + 499.0) / 2,
     "j": (5000.0 + 9999.0) / 2,
     "i": (10000.0 + 24999.0) / 2,
     "k": (25000.0 + 49999.0) /2,
     "D": 0.0,
     "null": 0.0
}

def weighted_vector(weights, mat):
     """
     Weighted Vector

     Calculated weighted vector by weighting each row of the mat and summing them up to one vector.
     The weights vector is supposed to add up to 1, and the len of the weights is also supposed to be 
     identical with the number of the rows of the mat.
     """

     # Make a copy of the mat to avoid changing the original matrix
     copy_mat     = mat.copy()
     copy_weights = weights.copy() 
     # TODO: improve the weigths vector by using a better formula instead of exponential function
     # Weight a exponential values on the original weights vector to make the larger value plays
     # higher percentage of weight
     exp_vals     = np.exp(range(len(copy_weights)))
     sorted_ind   = np.argsort(copy_weights)
     for i in range(len(sorted_ind)):
          copy_weights[sorted_ind[i]] *= exp_vals[i]
     # Normalize the weights
     copy_weights = [ w/sum(copy_weights) for w in copy_weights ]
     # Sum the weighted vectors up into only one
     for ind in range(len(copy_weights)):
          copy_mat[ind, :] *= copy_weights[ind]
     return copy_mat.sum(axis=0)


def main():

     # Parse the input parameters
     parser = argparse.ArgumentParser(
          description="Command-line script for interpolating the missing census data")
     parser.add_argument("-g", "--geo", required=True, help="The path of geo data by zipcodes")
     parser.add_argument("-c", "--census", required=True, help="The path of census data by zipcodes")
     parser.add_argument("-o", "--output", required=True, help="The path of output")
     parser.add_argument("-y", "--years", required=True, help="Years the census data has")
     args = parser.parse_args()

     year_list = args.years.split(",")
     # Validate the input params
     assert os.path.exists(args.geo), "geo data file %s does not exist" % args.geo
     assert os.path.exists(args.census), "census data file %s does not exist" % args.census
     assert len(year_list), "Years list %s is empty" % args.years 

     # Read data from files
     with open(args.geo, "r") as geo_h, open(args.census, "r") as census_h:
          # Extract geolocation of centers of the zipcodes regions. 
          # - zip_list: list of N zipcodes
          # - geo_mat:  [ [lat_1, long_1], ..., [lat_N, lat_N] ]
          geo_data = [ g.strip("\n").split(",") for g in geo_h ]
          zip_list = [ line[0] for line in geo_data ]
          geo_mat  = np.delete(np.array(geo_data), 0, axis=1).astype("float")
          # Extract census data in terms of (zipcode & year)
          # - feature_fields: list of names of M features
          # - existed_zips:   list of zipcodes which appear in the census data at least once
          # - unknown_zips:   list of zipcodes which have never appeared in the census data but exist in zip_list
          # - census_mat:     [size of zip_list] * [size of year_list] * [size of feature_fields]
          census_data    = [ c.strip("\n").split(",") for c in census_h ]
          existed_zips   = list(set([ census[0] for census in census_data[1:] ]))
          unknown_zips   = list(set(zip_list) - set(existed_zips))
          feature_fields = census_data[0][2:]
          census_mat     = np.zeros((len(existed_zips), len(year_list), len(feature_fields)))
          for census in census_data[1:]:
               census_mat[existed_zips.index(census[0]), year_list.index(census[1])] = \
                    np.array(map(lambda x: float(x) if x not in unknown_dict.keys() else unknown_dict[x], census[2:]))
          # Estimate new census data for unknown zipcode region
          new_census_mat = np.zeros((len(unknown_zips), len(year_list), len(feature_fields)))
          for unknown_zip in unknown_zips:
               # Calculate the euclidean distances between the geo of the current unknown zipcode and 
               # each of the geos of the existed zipcodes
               dists = np.array([ 
                    np.linalg.norm(
                         geo_mat[zip_list.index(unknown_zip)] - \
                         geo_mat[zip_list.index(existed_zip)])
                    for existed_zip in existed_zips ])
               # Weight each of the census data in the mat (same zipcode in different years), 
               # and sum them up as the weighted new census data
               for year in year_list:
                    # Normalize the dists list, making them all add up to 1. 
                    # Use the normalized distances as weighted vector
                    new_census_mat[unknown_zips.index(unknown_zip), year_list.index(year)] = \
                         weighted_vector(dists, census_mat[:, year_list.index(year), :])
          # Write the estimated new census data to file
          with open(args.output, "w") as output_h:
               for unknown_zip in unknown_zips:
                    for year in year_list:
                         line = ",".join(map(str, new_census_mat[
                              unknown_zips.index(unknown_zip), 
                              year_list.index(year)].tolist()))
                         output_h.write("%s,%s,%s\n" % (unknown_zip, year, line))



if __name__ == "__main__":
     main()