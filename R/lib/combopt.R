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

# Cost function for evaluating the variance of workload over all the zones
# given one possible solution.
variance.workload = function (beat.design.df) {
  zone.workloads.df = aggregate(workload ~ zone, beat.design.df, sum)
  variance = var(zone.workloads.df$workload)
  return(variance)
}

# A helper function for checking the connectivities of each cluster (sub graph)
# in terms of the given beat design.
check.connectivity = function (beat.design.df, graph.df) {
  zone.set = as.vector(unique(beat.design.df$zone))
  for (zone in zone.set) {
    sub.beats    = as.vector(beat.design.df[beat.design.df$zone==zone, 'beat'])
    sub.graph.df = graph.df[sub.beats, sub.beats]
    sub.net      = graph.adjacency(as.matrix(sub.graph.df), mode='undirected')
    if (length(subcomponent(sub.net, sub.beats[1], mode='all')) != length(sub.beats)) {
      return(FALSE)
    }
  }
  return(TRUE)
}

# A function for looking for the continuum neighborhood solutions according 
# to the adjacency matrix. The changes can only be made when the edges
# exist in the graph. In terms of a solution, a change is to include one
# of the adjacent nodes (in the other clusters) into the current cluster 
# given an arbitrary node in the graph.
library('igraph')
conti.neighbor = function (beat.design.df, beats, graph.df) {
  new.design.dfs = list()
  for (beat in beat.design.df$beat) {
    # zone for the current beat
    beat.zone       = as.character(beat.design.df[beat.design.df$beat == beat, 'zone'])
    # neighborhoods of the current beat in the graph
    beat.neighbors  = beats[which(graph.df[beat]>0)]
    # neighborhoods in different zones (the candidates for making the changes)
    beat.candidates = as.vector(beat.design.df[
      beat.design.df$beat %in% beat.neighbors & beat.design.df$zone != beat.zone, 
      'beat'])
    # for each of candidates, try to make the new design
    for (beat.candidate in beat.candidates) {
      new.design.df = beat.design.df
      # make the change on the candidate beat
      new.design.df[new.design.df$beat==beat.candidate, 'zone'] = beat.zone
      # check the connectivity of the new design
      if (check.connectivity(new.design.df, graph.df)) {
        # append the new design to the list
        new.design.dfs = append(new.design.dfs, list(new.design.df))
      }
    }
  }
  return(new.design.dfs)
}

simulated.annealing = function () {
  
}