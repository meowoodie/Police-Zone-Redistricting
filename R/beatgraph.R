# R code for generating undirected graph for beat areas depended on
# whether or not shared edges exist between two arbitrary beat areas.
# 
# References:
# - How to get access to the polygons in a SpatialPolygonsDataFrame:
#   https://gist.github.com/mbacou/5880859
# https://gis.stackexchange.com/questions/119624/extract-areas-of-multi-part-polygons-spatialpolygonsdataframe-r
# https://philmikejones.wordpress.com/2015/09/03/dissolve-polygons-in-r/
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library('geojsonio')

root.dir      = 'Desktop/workspace/Atlanta-Zoning'
beat.geo.path = paste(root.dir, 'data/apd_beat.geojson', sep='/')

beats.geo   = geojsonio::geojson_read(beat.geo.path, what = 'sp')

