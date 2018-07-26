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

workload.df  = read.workload(workload.path)
# Note: set check.names=FALSE in avoid of adding prefix X to the column names.
graph.df     = read.csv(beats.graph.path, header = TRUE, row.names = 1, 
                        sep = ',', stringsAsFactors=FALSE, check.names=FALSE) 
centroids.df = read.csv(beats.centers.path, header = TRUE, row.names = 1, 
                        sep = ',', stringsAsFactors=FALSE)
cur.year     = '17'

beats      = rownames(centroids.df)
init.zones = sapply(beats, function (beat) {
  zone  = as.numeric(substr(as.character(beat), 1, 1))
  # color = colorbar[zone + 1]
  return(color)
})
# workloads  =