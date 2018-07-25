# R modules for solving the optimization problem in zoning analysis.
# The scripts includes optimization methods as follow:
# - Simulated Annealing
# 
# These methods are based on searching the neighborhood to find the local
# optimum. The neighborhood of the solution can be only found when the
# edges exist in the adjancency matrix.
# 
# References:
# - Check the connectivity of a graph:
#   http://igraph.org/r/doc/subcomponent.html
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# A helper function for checking the connectivities of each cluster.
check.connectivity = function (graph.df) {
  
}

# A function for looking for the continuum neighborhood solutions according 
# to the adjacency matrix. The changes can only be made when the edges
# exist in the graph. In terms of a solution, a change is to include one
# of the adjacent nodes (in the other clusters) into the current cluster 
# given an arbitrary node in the graph.
conti.neighbor = function (zones, beats, graph.df, k=6) {
  
  # for () {}
}

# Cost function for evaluating the variance of workload over all the zones
# given one possible solution
# Params:
# - zones: a vector of corresponding zone ids of beats
# - beats: a vector of beat ids
# - workloads: a vector of corresponding workloads of beats
variance.workload = function (zones, workloads) {
  unique(zones)
}