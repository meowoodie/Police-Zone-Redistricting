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
library('sp')
library('maptools')
merge.beats = function (beat.geo, beat.design.df) {
  # Generate SpatialPolygons objects for each of beats according to 
  # their coordinates in geojson
  beats        = c()
  zones        = c()
  polygons     = list()
  for (i in 1:length(beats.geo@polygons)) {
    beat      = as.character(beats.geo@data$BEAT[i])
    zone      = as.character(beat.design.df[beat.design.df$beat==beat, 'zone'])
    if (length(zone) == 0) {
      zone = as.character(substr(as.character(beat), 1, 1))
    }
    # TODO: Fix the issue if the polygons object have multiple polygons
    coord = beats.geo@polygons[[i]]@Polygons[[1]]@coords
    # Patch:
    if (beat == '406') {
      coord = beats.geo@polygons[[i]]@Polygons[[2]]@coords
    }
    polygon  = spatial.polygon(coord, beat)
    # append to the lists
    polygons = append(polygons, polygon)
    beats    = c(beats, beat)
    zones    = c(zones, zone)
  }
  print(beats)
  # Remove No. 9 elements (corresponding to beat 606),
  # which is an invalid polygons due to data imperfection
  beats          = beats[-9]
  zones          = zones[-9]
  beats          = beats[-8] # beat 050
  zones          = zones[-8] # beat 050
  polygons[[9]]  = NULL
  polygons[[8]]  = NULL      # beat 050
  # Merge spatial polygons objects into one
  joined = SpatialPolygons(lapply(polygons, function(x){x@polygons[[1]]}))
  merged = unionSpatialPolygons(joined, zones)
  # Add features to the merged spatial polygons data frame
  merged$zone = sort(unique(zones))
  merged$workload = sapply(sort(unique(zones)), function (zone) {
    workload = sum(beat.design.df[beat.design.df$zone==zone, 'workload'])
    return(workload)
  })
  return(merged)
}

# A function for calculating the eccentricity of zones in the SpatialPolygons object
# References: original design
# zone         eccentricity
# 1    1 0.000236723272114583
# 2    2 0.000220620626924161
# 3    3 0.000207236485459834
# 4    4 0.000305890475295111
# 5    5 5.60310770383178e-05
# 6    6 0.000109180329312426
# 7   50 1.98755895981793e-05
library('pdist')
calculate.eccentricity = function (zones.geo) {
  eccentricities.df = data.frame()
  n.zones = length(zones.geo@polygons)
  for (i in 1:n.zones) {
    zone  = as.character(zones.geo@data$zone[i])
    if (zone != "0") {
      coord    = zones.geo@polygons[[i]]@Polygons[[1]]@coords
      polygon  = spatial.polygon(coord, zone)
      centroid = colMeans(coord)
      eccentricity      = var(pdist(rbind(centroid, coord), 
                                    indices.A=1, indices.B=2:nrow(coord)+1)@dist)
      eccentricity.df   = setNames(data.frame(
        matrix(c(zone, eccentricity), ncol = 2, nrow = 1)), 
        c('zone', 'eccentricity'))
      eccentricities.df = rbind(eccentricities.df, eccentricity.df)
    }
  }
  return(eccentricities.df)
}