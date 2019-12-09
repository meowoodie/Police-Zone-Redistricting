# Simulated Annealing for Police Beats

import random
import numpy as np
from collections import defaultdict
from designinit import visualize_grid, beat_with_max_workload

# load data
fname   = "Jan-APR-2019-PD-nbeat-19"
design  = np.load("result/grid-%s.npy" % fname) # a design includes multiple pairs of (grid_id, beat_id, grid_workload)
adj_mat = np.load("data/adjacency_matrix.npy")  # adjacency between grids

# HELPER FUNCTION SET
# objective function
def objective(design):
    beats_set     = set(design[:, 1].astype(np.int32))
    # calculate workload for each zone
    beat_workload = { beat: 0 for beat in beats_set }
    # zone_workload = {i: 0 for i in range(len([ beat for beat in beats_set ]))}
    for grid in design:
        grid_workload   = grid[2]      # workload for certain grid
        grid_assignment = int(grid[1]) # beat id that certain grid belongs to
        beat_workload[grid_assignment] += grid_workload
    variance = np.var([w for w in beat_workload.values()])
    return variance

# temperature
def temperature(fraction):
    return max(0.01, min(1, 1 - fraction))

# acceptance probability
def acceptance_probability(obj, cand_obj, temperature):
    if cand_obj < obj:
        # print("    - Acceptance probabilty = 1 as new_cost = {} < cost = {}...".format(new_cost, cost))
        return 1
    else:
        p = np.exp(-1 * (cand_obj - obj) / temperature)
        # print("    - Acceptance probabilty = {:.3g}...".format(p))
        return p



# SOLUTION SEARCH FUNCTION SET
def compactness(coords):
    """
    calculate the compactness of a set of coordinates 
    """
    # general variance strategy
    coords = np.array(coords)
    mean   = coords.mean(axis=0)
    var    = np.square(coords - mean).sum() / len(coords)
    return var

def compactness_set(x, coords):
    """
    calculate the compactness of each beat in a certain x (design)
    """
    beats_set = list(set(x))
    beats_set.sort()
    beats_pool = [ [] for beat in beats_set ]
    for xi, coord in zip(x, coords):
        beats_pool[beats_set.index(xi)].append(coord)
    compact_vec = np.array([ compactness(beat_coords) for beat_coords in beats_pool ])
    return compact_vec

def check_contiguous(x, adj_mat):
    """
    check if grids in each beat are fully connected (contiguous).
    """
    # DFS
    # reference: https://stackoverflow.com/questions/46659203/python-function-check-for-connectivity-in-adjacency-matrix
    return True

def check_compact(x, coords, thresholds=None, ratio=1.001):
    """
    check if each beat are compact.
    """
    if np.prod(compactness_set(x, coords) < ratio * thresholds):
        return True
    else:
        return False

def neighbor_x(x, adj_mat, coords, thresholds):
    """
    neighborhood solution with respect to current solution x, in which only one single 
    legitimate change is made on x.
    """
    # number of grids
    n_grids     = len(x)
    # list of edges that cross the boundary between beats
    cross_edges = [ 
        (i, j, int(x[i]), int(x[j]))              # (grid i, grid j, beat of i, beat of j)
        for i in range(n_grids) for j in range(n_grids) 
        if adj_mat[i, j] == 1 and int(x[i]) != int(x[j]) ]
    # get all possible changes on each cross edge and convert them back to the format of x
    neighbor_xs = []
    for i, j, beat_i, beat_j in cross_edges:
        left_x     = x.copy()
        left_x[i]  = beat_j
        right_x    = x.copy()
        right_x[j] = beat_i
        # check contiguity and compactness of new x
        if check_contiguous(left_x, adj_mat) and check_compact(left_x, coords, thresholds): 
            neighbor_xs.append(left_x)
        if check_contiguous(right_x, adj_mat) and check_compact(right_x, coords, thresholds): 
            neighbor_xs.append(right_x)
    return neighbor_xs

def select_cand_x(xs, n_beats):
    """
    select one of x from a list of x as the candidate x. 
    """
    # ensure each beat has more than 10 grids
    _xs = []
    for x in xs:
        beats_pool = defaultdict(lambda: 0)
        for xi in x:
            beats_pool[xi] += 1
        beats_size = np.array(list(beats_pool.values()))
        if len(beats_size) == n_beats and np.prod(beats_size >= 10):
            _xs.append(x)
    # random pick strategy
    x_ind  = random.choice(list(range(len(_xs))))
    cand_x = _xs[x_ind]
    return cand_x



if __name__ == "__main__":
    # configuration
    max_iters = 100
    # parameter initialization
    x      = design[:, 1].astype(np.int32)
    coords = design[:, 3:]
    obj    = objective(design)
    thres  = compactness_set(x, coords)
    print(obj)

    for i in range(max_iters):
        print("iter:", i)
        frac   = i / max_iters
        T      = temperature(frac)
        cand_x = select_cand_x(neighbor_x(x, adj_mat, coords, thres), n_beats=len(thres))
        # update candidate design
        cand_design       = design.copy()
        cand_design[:, 1] = cand_x
        cand_obj          = objective(cand_design)
        if acceptance_probability(obj, cand_obj, T) > np.random.uniform(0,1):
            print("var:", cand_obj)
            x   = cand_x
            obj = cand_obj
    
    print(x)
    final_design = cand_design

    _, _, init_beats_workload  = beat_with_max_workload(design)
    _, _, final_beats_workload = beat_with_max_workload(final_design)
    # min_val = min([min(init_beats_workload), min(final_beats_workload)])
    # max_val = max([max(init_beats_workload), max(final_beats_workload)])
    visualize_grid(final_design, "grids", 
        map_fname="redesign-%s" % fname, 
        min_val=min(init_beats_workload)/3600, max_val=max(init_beats_workload)/3600)
    np.save("result/grid-redesign-%s.npy" % fname, final_design)