#!/bin/bash

# Step 1: Interpolation
# Interpolate estimated census data for some of the zipcodes regions 
# that lacked history cencus data. 
# Input: 

python modules/interp_missing_zip.py \
	-g data/zip_geo.csv \
	-c data/census_by_zip.csv \
	-o temp/census_by_zip_new.csv \
	-y 2011,2012,2013,2014,2015

# Concatenate two census data (in terms of zipcode) into one
cat data/census_by_zip.csv  temp/census_by_zip_new.csv > temp/census_by_zip_complete.csv





