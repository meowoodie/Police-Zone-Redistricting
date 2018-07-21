# R code for visualizing the Atlanta beat & zone and their configurations 
# on an interactive map.
# references: https://rstudio.github.io/leaflet/json.html
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library('leaflet')
library('geojsonio')

root.dir      = 'Desktop/workspace/Atlanta-Zoning'
data.dir      = paste(root.dir, 'data/census', sep='/')
map.path      = paste(root.dir, 'data/cross_map.csv', sep='/')
workload.path = paste(root.dir, 'data/workload.csv', sep='/')
beat.geo.path = paste(root.dir, 'data/apd_beat.geojson', sep='/')
zone.geo.path = paste(root.dir, 'data/apd_zone.geojson', sep='/')

source(paste(root.dir, 'R/preproc.R', sep='/'))

workload.df = read.workload(workload.path)
beats.geo   = geojsonio::geojson_read(beat.geo.path, what = 'sp')
zones.geo   = geojsonio::geojson_read(zone.geo.path, what = 'sp')
cur.year    = '15'

# add information into geojson
# - zone number
beats.geo$zone = sapply(beats.geo$BEAT, function(beat) {
  zone = substr(as.character(beat), 1, 1)
  return(zone)
})
# - workload
beats.geo$workload = sapply(beats.geo$BEAT, function(beat) {
  workload = workload.df[workload.df$Id2==as.character(beat) & workload.df$year==cur.year, 'workload']
  # if there is no value then set NA
  if (length(workload) == 1) { workload = as.numeric(workload) }
  else { workload = NA }
  return(workload)
})

# color settings
pal = colorBin('YlOrRd', domain = beats.geo$workload)

# label settings
labels = sprintf(
  '<strong>Zone %s</strong><br/><strong>Beat %s</strong><br/>%g hours / year',
  beats.geo$zone, beats.geo$BEAT, beats.geo$workload
) %>% lapply(htmltools::HTML)

# loading data into the initial map and adding background tiles
leaflet(beats.geo) %>%
  # load base map
  addTiles() %>% 
  # plot beat polygons
  addPolygons(
    fillColor   = ~pal(workload),
    weight      = 2,
    opacity     = 1,
    color       = 'white',
    dashArray   = '3',
    fillOpacity = 0.5,
    highlight   = highlightOptions(
      weight    = 5,
      color     = '#666',
      dashArray = '',
      fillOpacity  = 0.7,
      bringToFront = FALSE),
    label        = labels,
    labelOptions = labelOptions(
      style     = list('font-weight' = 'normal', padding = '3px 8px'),
      textsize  = '15px',
      direction = 'auto'),
    group       = 'Beats Layer') %>%
  # add legend for beat map
  addLegend(
    pal      = pal, 
    values   = ~workload, 
    opacity  = 0.7, 
    title    = NULL,
    position = 'bottomright') %>%
  # plot zone polygons
  addPolygons(
    data      = zones.geo, 
    fill      = FALSE, 
    weight    = 5, 
    dashArray = '8',
    color     = 'Grey', 
    group     = 'Zones Layer')
  # # add controller for beat and zone layers
  # addLayersControl(
  #   overlayGroups = c('Beats Layer', 'Zones Layer'),
  #   options       = layersControlOptions(collapsed = FALSE)
  # )