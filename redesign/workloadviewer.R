# R code for visualizing the Atlanta beat & zone and their configurations 
# with corresponding workload values on an interactive map.
# 
# References: 
# - How to plot geojson on a real map
#   https://rstudio.github.io/leaflet/json.html
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library('devtools')
library('leaflet')
library('geojsonio')
library('shiny')
# devtools::install_github('rstudio/leaflet')

root.dir      = 'Desktop/workspace/Zoning-Analysis'
workload.path = paste(root.dir, 'data/workload.csv', sep='/')
beat.geo.path = paste(root.dir, 'data/apd_beats_Jun2018.geojson', sep='/')
zone.geo.path = paste(root.dir, 'data/apd_zone_Jun2018.geojson', sep='/')
redesign.path = paste(root.dir, 'data/redesign.csv', sep='/')

source(paste(root.dir, 'redesign/lib/preproc.R', sep='/'))

workload.df   = read.workload(workload.path)
new.design.df = read.csv(redesign.path, header = TRUE, row.names = 1, 
                         sep = ',', stringsAsFactors=FALSE, check.names=FALSE) 
beats.geo   = geojsonio::geojson_read(beat.geo.path, what = 'sp')
zones.geo   = geojsonio::geojson_read(zone.geo.path, what = 'sp')
cur.year    = '17'

# add information into geojson
# - zone number
beats.geo$zone = sapply(beats.geo$BEAT, function (beat) {
  zone = substr(as.character(beat), 1, 1)
  return(zone)
})
# - workload for beats
beats.geo$workload = sapply(beats.geo$BEAT, function (beat) {
  workload = workload.df[workload.df$Id2==as.character(beat) & workload.df$year==cur.year, 'workload']
  # if there is no value then set NA
  if (length(workload) == 1) { workload = as.numeric(workload) }
  else { workload = NA }
  return(workload)
})
# - workload for zones
zones.geo$workload = sapply(zones.geo$ZONE, function (zone) {
  workload = sum(workload.df[
    substr(as.character(workload.df$Id2), 1, 1)==as.character(zone) & workload.df$year==cur.year,
    'workload'])
  if (length(workload) == 1 & workload != 0) { workload = as.numeric(workload) }
  else { workload = NA }
  return(workload)
})

# title settings
title = tags$div(HTML(sprintf(
  '<a href="https://cran.r-project.org/"> \
  Worload Analysis of Atlanta City in 20%s </a>', cur.year)))  

# color settings
beat.pal = colorBin('YlOrRd', domain = beats.geo$workload)
zone.pal = colorBin('viridis', domain = zones.geo$workload, reverse = TRUE)

# label settings
beat.label = sprintf(
  '<strong>Zone %s</strong><br/><strong>Beat %s</strong><br/>%g hours / year',
  beats.geo$zone, beats.geo$BEAT, beats.geo$workload
) %>% lapply(htmltools::HTML)
zone.label = sprintf(
  '<strong>Zone %s</strong><br/>%g hours / year',
  zones.geo$ZONE, zones.geo$workload
) %>% lapply(htmltools::HTML)

# loading data into the initial map and adding background tiles
leaflet(beats.geo) %>%
  addControl(title, position = "topright") %>%
  # load base map
  addTiles() %>% 
  # plot beat polygons in beats layer
  addPolygons(
    fillColor   = ~beat.pal(workload),
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
    label        = beat.label,
    labelOptions = labelOptions(
      style     = list('font-weight' = 'normal', padding = '3px 8px'),
      textsize  = '15px',
      direction = 'auto'),
    group       = 'Beats Layer') %>%
  # plot zone polygons in beats layer
  addPolygons(
    data      = zones.geo, 
    fill      = FALSE, 
    weight    = 5, 
    dashArray = '8',
    color     = 'Grey', 
    group     = 'Beats Layer') %>%
  # plot zone polygons in zones layer
  addPolygons(
    data        = zones.geo,
    fillColor   = ~zone.pal(workload),
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
    label        = zone.label,
    labelOptions = labelOptions(
      style     = list('font-weight' = 'normal', padding = '3px 8px'),
      textsize  = '15px',
      direction = 'auto'),
    group       = 'Zones Layer'
  ) %>%
  # add legend for beat map
  addLegend(
    pal      = beat.pal, 
    values   = ~workload, 
    opacity  = 0.7, 
    title    = 'Workload in Beats',
    position = 'bottomright',
    group    = 'Beats Layer') %>%
  # add legend for beat map
  addLegend(
    pal      = zone.pal, 
    values   = ~workload, 
    opacity  = 0.7, 
    title    = 'Worload in Zones',
    position = 'bottomleft',
    group    = 'Zones Layer') %>%
  # add controller for beat and zone layers
  addLayersControl(
    baseGroups = c('Beats Layer', 'Zones Layer'),
    options    = layersControlOptions(collapsed = FALSE)) 