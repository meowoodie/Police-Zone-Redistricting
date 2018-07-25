# R code for generating undirected graph for beat areas depended on
# whether or not shared edges exist between two arbitrary beat areas.
# 
# References:
# - How to get access to the polygons in a SpatialPolygonsDataFrame:
#   https://gist.github.com/mbacou/5880859
# - How to check if two polygons have intersections
#   https://stackoverflow.com/questions/37756480/inconsistent-behavior-of-goverlaps-and-gtouches-when-polygons-intersect-at-a-poi?rq=1
# - Plot undirected graph
#   http://kateto.net/netscix2016
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library('geojsonio')
library('rgeos')
library('sp')

root.dir      = 'Desktop/workspace/Atlanta-Zoning'
beat.geo.path = paste(root.dir, 'data/apd_beat.geojson', sep='/')
colorbar      = c('gray', 'blue', 'black', 'red', 'yellow', 'purple', 'green')

source(paste(root.dir, 'R/lib/utils.R', sep='/'))

# read geojson into beats.geo
beats.geo   = geojsonio::geojson_read(beat.geo.path, what = 'sp')
# zone information for each of the beats
beats.color = sapply(beats.geo$BEAT, function (beat) {
  zone  = as.numeric(substr(as.character(beat), 1, 1))
  color = colorbar[zone + 1]
  return(color)
})
# number of beats
n.beats     = length(beats.geo@polygons)

# Generate SpatialPolygons objects for each of beats according to 
# their coordinates in geojson
beats     = c()
polygons  = list()
centroids = data.frame()
for (i in 1:n.beats) {
  beat      = as.character(beats.geo@data$BEAT[i])
  coord     = beats.geo@polygons[[i]]@Polygons[[1]]@coords
  polygon   = spatial.polygon(coord, beat)
  centroid  = setNames(data.frame(matrix(colMeans(coord), ncol = 2, nrow = 1)), c('longitude', 'latitude'))
  # append to the lists
  polygons  = append(polygons, polygon)
  beats     = c(beats, beat)
  centroids = rbind(centroids, centroid)
}
# Remove No. 9 elements (corresponding to beat 606),
# which is an invalid polygons due to data imperfection
beats         = beats[-9]
polygons[[9]] = NULL
centroids     = centroids[-9,]
beats.color   = beats.color[-9]
n.beats       = n.beats - 1
# # Remove duplicate elements in beats and polygons
# # (due to the redundancies in the geojson file)
# dups.inds = which(duplicated(beats) %in% c(TRUE))
# beats     = beats[!duplicated(beats)]
# polygons[dups.inds] = NULL
# centroids = centroids[!duplicated(beats),]
# n.beats   = n.beats - length(dups.inds)

# Create adjacency matrix for the beats graph
# according to whether or not the touches exist between two arbitrary beats
graph.df = data.frame(matrix(ncol=length(beats), nrow=length(beats)))
colnames(graph.df) = beats
rownames(graph.df) = beats
for (i in 1:n.beats) {
  for (j in 1:n.beats) {
    beat.i   = polygons[[i]]@polygons[[1]]@ID
    beat.j   = polygons[[j]]@polygons[[1]]@ID
    is.touch = gTouches(polygons[[i]], polygons[[j]])
    graph.df[beat.i, beat.j] = as.numeric(is.touch)
  }
}

# Code patch for minor revising graph manually
graph.df['407', '406'] = 1
graph.df['406', '407'] = 1

# Plot undirected graph according to the beats adjacencies.
m   = as.matrix(graph.df)
net = graph.adjacency(m, mode = 'undirected')
plot(net, layout=as.matrix(centroids),
     vertex.color=beats.color, vertex.size=4, 
     vertex.frame.color='gray', vertex.label.color='black', 
     vertex.label.cex=0.8, vertex.label.dist=1)