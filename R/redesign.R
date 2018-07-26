# R modules for solving the optimization problem in zoning analysis.
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

root.dir           = 'Desktop/workspace/Atlanta-Zoning'
workload.path      = paste(root.dir, 'data/workload.csv', sep='/')
beats.graph.path   = paste(root.dir, 'data/beats_graph.csv', sep='/')
beats.centers.path = paste(root.dir, 'data/beats_centroids.csv', sep='/') # for visualization

source(paste(root.dir, 'R/lib/combopt.R', sep='/'))
source(paste(root.dir, 'R/lib/preproc.R', sep='/'))

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
cur.year     = '17'

# a vector of beats
beats      = rownames(centroids.df)
# a vector of initial zones
init.zones = sapply(beats, function (beat) {
  zone = as.numeric(substr(as.character(beat), 1, 1))
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
final.res = simulated.annealing(beat.design.df, beats, graph.df, n=100)
