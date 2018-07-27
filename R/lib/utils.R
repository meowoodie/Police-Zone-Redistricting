# R functions of utilities
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# A function for plotting the result of variable selection by glmnet.
# note: 
# cv.fit = cv.glmnet(x, y, alpha=1)
# mod    = glmnet(x, y)
plot.cv.fit = function (cv.fit, mod) {
  # plot linear regression result
  glmcoef       = coef(mod, cv.fit$lambda.min)
  coef.increase = dimnames(glmcoef[glmcoef[,1]>0,0])[[1]]
  coef.decrease = dimnames(glmcoef[glmcoef[,1]<0,0])[[1]]
  # get ordered list of variables as they appear at smallest lambda
  allnames = names(coef(mod)[ ,ncol(coef(mod))][order(coef(mod)[ ,ncol(coef(mod))], decreasing=TRUE)])
  # remove intercept
  allnames = setdiff(allnames, allnames[grep("Intercept",allnames)])
  # assign colors
  cols = rep("gray", length(allnames))
  cols[allnames %in% coef.increase] = "red"      # higher mpg is good
  cols[allnames %in% coef.decrease] = "blue"     # lower mpg is not
  plot_glmnet(cv.fit$glmnet.fit, label=TRUE, s=cv.fit$lambda.min, col=cols)
}

# A helper function to create SpatialPolygons objects
spatial.polygon = function(coord, ID) {
  SpatialPolygons(
    list(Polygons(list(Polygon(coord)), ID = ID))
  )
}

# A function for merging beats into zones
# References:
# - Join multiple Polygons into one data frame
#   https://gis.stackexchange.com/questions/180682/merge-a-list-of-spatial-polygon-objects-in-r
# - Merge polygons of a dataframe accordingly
#   https://gis.stackexchange.com/questions/63577/joining-polygons-in-r
library(ggplot2)
merge.beats = function (beat.geo, beat.design) {
  # Generate SpatialPolygons objects for each of beats according to 
  # their coordinates in geojson
  beats        = c()
  zones        = c()
  polygons     = list()
  for (i in 1:length(beats.geo@polygons)) {
    beat      = as.character(beats.geo@data$BEAT[i])
    zone      = as.character(beat.design[beat.design$beat==beat, 'zone'])
    if (length(zone) == 0) {
      zone = as.character(substr(as.character(beat), 1, 1))
    }
    coord     = beats.geo@polygons[[i]]@Polygons[[1]]@coords
    polygon   = spatial.polygon(coord, beat)
    # append to the lists
    polygons     = append(polygons, polygon)
    beats        = c(beats, beat)
    zones        = c(zones, zone)
  }
  # Remove No. 9 elements (corresponding to beat 606),
  # which is an invalid polygons due to data imperfection
  beats         = beats[-9]
  zones         = zones[-9]
  polygons[[9]] = NULL
  # Merge spatial polygons objects into one
  joined = SpatialPolygons(lapply(polygons, function(x){x@polygons[[1]]}))
  merged = unionSpatialPolygons(joined, zones)
  # Add features to the merged spatial polygons data frame
  merged$zone = sort(unique(zones))
  merged$workload = sapply(sort(unique(zones)), function (zone) {
    workload = sum(beat.design[beat.design$zone==zone, 'workload'])
    return(workload)
  })
  return(merged)
}