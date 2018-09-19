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
# - variance
variance.workload = function (beat.design.df) {
  zone.workloads.df = aggregate(workload ~ zone, beat.design.df, sum)
  variance = var(zone.workloads.df$workload)
  return(variance)
}
# - variation (sum of pairwise differences)
variation.workload = function (beat.design.df) {
  zone.workloads.df = aggregate(workload ~ zone, beat.design.df, sum)
  variation = sum(abs(apply(combn(zone.workloads.df$workload, 2), 2, diff)))
  return(variation)
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

# A helper function for checking the eccentricity of each cluster (sub graph)
# in terms of the given beat design.
check.eccentricity = function (beat.design.df, beats.geo) {
  scale          = 1.01
  new.zone.geo   = merge.beats(beats.geo, beat.design.df)
  eccentricities = calculate.eccentricity(new.zone.geo)
  # eccentricities should not greater than (original eccentricities times alpha)
  # 1    0.000236723272114583
  # 2    0.000220620626924161
  # 3    0.000207236485459834
  # 4    0.000305890475295111
  # 5    5.60310770383178e-05
  # 6    0.000109180329312426
  # print(eccentricities)
  if (as.numeric(as.character(eccentricities[eccentricities$zone==1, 'eccentricity'])) > (0.000236723272114583 * scale) || 
      as.numeric(as.character(eccentricities[eccentricities$zone==2, 'eccentricity'])) > (0.000220620626924161 * scale) ||
      as.numeric(as.character(eccentricities[eccentricities$zone==3, 'eccentricity'])) > (0.000207236485459834 * scale) ||
      as.numeric(as.character(eccentricities[eccentricities$zone==4, 'eccentricity'])) > (0.000305890475295111 * scale) ||
      as.numeric(as.character(eccentricities[eccentricities$zone==5, 'eccentricity'])) > (5.60310770383178e-05 * scale) ||
      as.numeric(as.character(eccentricities[eccentricities$zone==6, 'eccentricity'])) > (0.000109180329312426 * scale)) {
    return(FALSE)
  }
  else {
    return(TRUE)
  }
}

# A function for looking for the continuum neighborhood solutions according 
# to the adjacency matrix. The changes can only be made when the edges
# exist in the graph. In terms of a solution, a change is to include one
# of the adjacent nodes (in the other clusters) into the current cluster 
# given an arbitrary node in the graph.
library('igraph')
conti.neighbor = function (beat.design.df, beats, graph.df, beats.geo) {
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
        # check the eccentricity of the new design only if it was connnected
        # since this step is time-consuming. 
        if (check.eccentricity(new.design.df, beats.geo)) {
          print('legal solution found.')
          # append the new design to the list
          new.design.dfs = append(new.design.dfs, list(new.design.df))
        }
      }
    }
  }
  return(new.design.dfs)
}

# Core function for optimizing the design by simulated annealing.
simulated.annealing = function (beat.design.df, beats, graph.df, beats.geo, n=10) {
  alpha = 0.01      # cooling rate
  beta  = 2         # stage rate
  ptm   = proc.time() # Start the clock!
  
  temp  = 1    # temperature
  stage = 1    # length of stage m   
  
  cost  = variance.workload(beat.design.df)
  iters = c() # init iteration results of cost
  for (j in 1:n){
    print(sprintf('iter: %d', j))
    for (m in 1:stage){
      # get neighborhoods for the current solution
      neighbors        = conti.neighbor(beat.design.df, beats, graph.df, beats.geo)
      res              = c() # init results for cost
      neighbor.indices = c() # init candidates for neighbor
      for (i in 1:length(neighbors)){
        neighbor      = neighbors[[i]]
        neighbor.cost = variance.workload(neighbor) # calculate cost for each neighbor
        if (neighbor.cost < cost){
          res              = c(res, neighbor.cost)
          neighbor.indices = c(neighbor.indices, i)
        }
      }
      # stop criterion
      if (length(res) <= 0){
        # Stop the clock
        dt     = proc.time() - ptm
        result = list("solution"   = beat.design.df,
                      "time"       = dt,
                      "iterations" = iters)
        return(result)
      }
      # randomly pick a neighbor from candidates
      cand.ind      = sample(1:length(res), 1)
      cand.neighbor = neighbors[[neighbor.indices[cand.ind]]]
      cand.cost     = res[cand.ind]
      # accept this solution by accept rate
      acceptRate   = min(1, exp((cost - cand.cost)/temp))
      if (sample(c(TRUE,FALSE), size=1, replace=TRUE, 
                 prob=c(acceptRate,1-acceptRate))){
        beat.design.df = cand.neighbor
        cost           = cand.cost
        iters          = c(iters, cost)
      }
    }
    # update temperature and stage
    temp  = temp/(1+alpha*temp)
    stage = stage * beta
  }
}