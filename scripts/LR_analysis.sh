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
cat data/census_by_zip.csv  temp/census_by_zip_new.csv | sort -k1,1 -k2,2 -t',' > temp/census_by_zip_complete.csv


# Step 2: Autoregression
#
python modules/pred_future_census.py \
	-c temp/census_by_zip_complete.csv \
	-o temp/census_by_zip_future.csv \
	-y 2011,2012,2013,2014,2015 \
	-f 2016,2017,2018 \
	-l 2

# Concatenate 
awk 'NR>2 {print l} {l=$0}' temp/census_by_zip_complete.csv > temp/tmp.census_by_zip_complete.rm_first_row
awk 'NR==1' temp/census_by_zip_complete.csv > temp/tmp.census_by_zip_complete.first_row
cat temp/tmp.census_by_zip_complete.rm_first_row temp/census_by_zip_future.csv | sort -k1,1 -k2,2 -t',' > temp/tmp.census_by_zip.rm_first_row
cat temp/tmp.census_by_zip_complete.first_row temp/tmp.census_by_zip.rm_first_row > temp/census_by_zip.csv
rm temp/tmp.*

# Step 3: 
#

python modules/zip2beat.py \
	-b data/zip_beat.csv \
	-c temp/census_by_zip.csv \
	-o temp/census_by_beat.csv \
	-y 2011,2012,2013,2014,2015,2016,2017,2018

# Step 4: Linear Regression
#

python modules/pred_future_workload.py \
	-w data/workload_by_beat.csv \
	-c temp/census_by_beat.csv \
	-o temp/workload_by_beat_future.csv \
	-f 2017,2018