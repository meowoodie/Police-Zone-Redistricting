#!/bin/bash

python modules/scatter_points.py \
	-g data/911calls_info_extraction.txt \
	-d temp/workload_by_beat.csv
	# -d temp/census_by_beat.csv