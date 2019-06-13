# R modules for solving the optimization problem in zoning analysis.
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

root.dir           = 'Desktop/workspace/Zoning-Analysis'
workload.path      = paste(root.dir, 'data/workload_by_junzhuo.csv', sep='/')
beat.geo.path      = paste(root.dir, 'data/apd_beat.geojson', sep='/')
beats.graph.path   = paste(root.dir, 'data/beats_graph.csv', sep='/')
beats.centers.path = paste(root.dir, 'data/beats_centroids.csv', sep='/') # for visualization

source(paste(root.dir, 'heuristic/lib/optimizer.R', sep='/'))
source(paste(root.dir, 'heuristic/lib/preproc.R', sep='/'))
source(paste(root.dir, 'heuristic/lib/utils.R', sep='/'))

# Geojson for beats area
beats.geo    = geojsonio::geojson_read(beat.geo.path, what = 'sp')
# Workload dataframe from local file
workload.df  = read.workload(workload.path)
# Graph of the connectivities of the beats according to their adjacency matrix
# Note: set check.names=FALSE in avoid of adding prefix X to the column names.
graph.df     = read.csv(beats.graph.path, header = TRUE, row.names = 1, 
                        sep = ',', stringsAsFactors=FALSE, check.names=FALSE) 
# Centroids coordinates dataframe from local file
centroids.df = read.csv(beats.centers.path, header = TRUE, row.names = 1, 
                        sep = ',', stringsAsFactors=FALSE)
# The year that we are going to analyze
cur.year     = '19'

# a vector of beats
beats        = rownames(centroids.df)
# a vector of initial zones
init.zones = sapply(beats, function (beat) {
  # if (beat == "FID_South" || beat == "FID_North"){
  #   zone = 1
  # }
  # if (beat == "FID_South" || beat == "FID_North" || beat == "114" || beat == "111_West" ||
  #     beat == "407" || beat == "412" || beat == "413" || beat == "414"){
  #   zone = 7
  # }
  # else{
    zone = as.numeric(substr(as.character(beat), 1, 1))
  # }
  return(zone)
})
# dataframe for zones of each beats (columns: beat, zone)
beat.zones.df     = setNames(data.frame(matrix(c(beats, init.zones), nrow=length(beats))), c('beat', 'zone'))
# dataframe for workloads of each beats (columns: beat, workload)
beat.workloads.df = workload.df[
  workload.df$Id2 %in% beats & workload.df$year==cur.year,
  c('Id2', 'workload')]
colnames(beat.workloads.df)[1] = 'beat'
# dataframe for the initial design (columns: beat, zone, workload)
beat.design.df    = merge.mdf(list(beat.zones.df, beat.workloads.df), keys=c('beat'))

# redesign by simulated annealing method
final.res = simulated.annealing(beat.design.df, beats, graph.df, beats.geo, n=100)
print(final.res$iterations)
print(final.res$time)

# Write results to local file
redesign.path = paste(root.dir, 'data/redesign_animation/redesign.csv', sep='/')
write.csv(final.res$solution, file=redesign.path)

# # print the variation of the design
# print(variation.workload(beat.design.df))