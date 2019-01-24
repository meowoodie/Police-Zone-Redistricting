#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zone Reconfiguration problem solved Gurobi.
"""

from gurobipy import *
import csv
import sys

lam = 1. # weigth of compactness  
m   = 6  # number of zones

# load meta data / data
with open("../data/beats_graph.csv", newline="") as farcs, \
     open("./workload.txt", "r") as fworkload, \
     open("../data/beats_centroids_Jun2018.csv", newline="") as fcentroid:
    data  = list(csv.reader(farcs))
    # lists of nodes
    nodes = [ d for d in data[0] if d != "" ] 
    # lists of zones
    zones = list(range(m))
    # arcs of nodes represented by a dictionary where keys are the nodes, values are lists of adjacent nodes
    arcs  = [ [ int(d) for d in row if d == "1" or d == "0" ] for row in data if row[0] != "" ]
    arcs  = { nodes[i]: [ nodes[j] for j, e in enumerate(arcs[i]) if e != 0 ]  for i in range(len(arcs)) }
    # workloads of nodes represented by a dictionary where keys are the nodes, values are the workloads
    workloads = [ workload.strip("\n").split(",") for workload in fworkload.readlines() ]
    workloads = { workload[0]: float(workload[1]) for workload in workloads }
    # centroids of nodes represented by a dictionary where keys are the nodes, values are the locations of the centroids.
    centroids = list(csv.reader(fcentroid))
    centroids = { centroid[0]: [float(centroid[1]), float(centroid[2])] for centroid in centroids[1:] }

n = len(nodes)
q = n - m + 1 # the maximum number of beats to be chosen in a zone.

# create gurobi model
model = Model("Zone Reconfiguration")

# Variables:
# - decision variable: if node i is in zone k
x = model.addVars(nodes, zones, name="x", vtype=GRB.BINARY)
# - if beat i is selected as a sink in zone k
w = model.addVars(nodes, zones, name="w", vtype=GRB.BINARY)
# - the non-negative flow from node i to node j in zone k
y = model.addVars(nodes, nodes, zones, name="y", vtype=GRB.CONTINUOUS)

# Data
# - workload in node i
u = workloads
s = centroids

# Constraints
# - b: each node can only be allocated to one zone
model.addConstrs(( x.sum(i,"*") == 1 for i in nodes ), "b")
# - c: the net outflow from each node
model.addConstrs(( 
    sum([ y[i,j,k] for j in arcs[i] ]) - sum([ y[j,i,k] for j in arcs[i] ]) >= x[i,k] - q * w[i,k]
    for i in nodes for k in zones ), "c")
# - d: specify the number of nodes that can be used as sinks.
model.addConstr(w.sum() == m, "d")
# - e: ensure that each zone must have only one sink
model.addConstrs(( w.sum("*",j) == 1 for j in zones ), "e")
# - f: ensure that there is no flow into any node i from outside of zone k (where xik = 0), 
#      and that the total inflow of any node in zone k (where xik = 1) does not exceed q − 1.
model.addConstrs(( sum([ y[j,i,k] for j in arcs[i] ]) <= (q - 1) * x[i,k] for i in nodes for k in zones ), "f")
# - g: ensure unless a node i is included in zone k, the node k cannot be a sink in zone k.
model.addConstrs(( w[i,k] - x[i,k] <= 0 for i in nodes for k in zones ), "g")
# - h, i: ensure that there is no flows (inflows and outflows) between different zones which forces eligible contiguity.
model.addConstrs(( y[i,j,k] + y[j,i,k] <= (q - 1) * x[i,k] for i in nodes for j in nodes for k in zones ), "h")
model.addConstrs(( y[i,j,k] + y[j,i,k] <= (q - 1) * x[j,k] for i in nodes for j in nodes for k in zones ), "i")
# - j: non-negative net flow
model.addConstrs(( y[i,j,k] >= 0 for i in nodes for j in nodes for k in zones ), "j")

# objective 1: balancing workload between zones
obj_balance_workload = sum([ 
    (sum([ x[i,k] * u[i] for i in nodes ]) - sum([ u[i] for i in nodes ]) / m) * \
    (sum([ x[i,k] * u[i] for i in nodes ]) - sum([ u[i] for i in nodes ]) / m) \
    for k in zones ])

# objective 2: shape compactness
# obj_compactness = sum([ 
#     sum([ x[ei,k] * x[ej,k] * ((s[ei][0] - s[ej][0]) ** 2 + (s[ei][1] - s[ej][1]) ** 2) # distance between node i and node j in zone k
#           for i, ei in enumerate(nodes) for j, ej in enumerate(nodes) if i > j ]) - 
#     sum([ x[ei,k] * x[ej,k] * ((s[ei][0] - s[ej][0]) ** 2 + (s[ei][1] - s[ej][1]) ** 2) 
#           for i, ei in enumerate(nodes) for j, ej in enumerate(nodes) if i > j ]) / 
#     sum([ x[ei,k] * x[ej,k]
#           for i, ei in enumerate(nodes) for j, ej in enumerate(nodes) if i > j ])
#     for k in zones ])
# obj_compactness = sum([ x[ei,k] * x[ej,k] * ((s[ei][0] - s[ej][0]) ** 2 + (s[ei][1] - s[ej][1]) ** 2) 
#     for i, ei in enumerate(nodes) for j, ej in enumerate(nodes) for k in zones if i > j ])

# set objective for the model
model.setObjective(obj_balance_workload, # + lam * obj_compactness, 
    GRB.MINIMIZE)

# Decision initialization
b = []
z = []
for i in nodes:
    for k in zones:
        # if int(i[0]) == int(k+1):
        #     b.append(int(i))
        #     x[i,k].start = 1
        # else:
        #     x[i,k].start = 0
        x[i,k].start = 1 if int(i[0]) == int(k+1) else 0
            # w[i,k].start = 1 if int(i[1]) == 0 and int(i[-1]) == int(k) else 0 
            # y[i,j,k].start = 

# solve model
model.optimize()

# organize results
if model.SolCount == 0:
    print('No solution found, optimization status = %d' % model.Status, file=sys.stderr)
else:
    print('Solution found, objective = %g' % model.ObjVal, file=sys.stderr)
    with open("./opt_result.csv", "w") as fresult:
        fresult.write(",beat,zone,workload\n")
        no = 1
        for v in model.getVars():
            if v.X == 1. and v.VarName[0] == "x":
                node = v.VarName[2:5]
                zone = v.VarName[6]
                fresult.write("%d,%s,%s,%f\n" % (no, node, zone, workloads[node]))
                print("beat %s in zone %s" % (node, zone), file=sys.stderr)
                no += 1
