import numpy as np
from collections import defaultdict

routes = []
beats  = set()
with open("data/patrol.route.txt", "r") as f:
    for line in f.readlines():
        data = line.strip().split("\t")
        start_beat, end_beat, dt = data[0], data[1], float(data[2])
        routes.append([start_beat, end_beat, dt])
        beats = beats | set({start_beat, end_beat})

beats   = list(beats)
beats.sort()
n_beats = len(beats) 
print(beats)
print(n_beats)

total_t = np.zeros((n_beats, n_beats))
total_n = np.zeros((n_beats, n_beats))
for route in routes:
    start_idx = beats.index(route[0])
    end_idx   = beats.index(route[1])
    dt        = route[2]
    total_t[start_idx][end_idx] += dt
    total_n[start_idx][end_idx] += 1

Tau = np.divide(total_t, total_n, out=np.zeros_like(total_t), where=total_n!=0)
print(Tau)
print((n_beats * n_beats - np.count_nonzero(Tau)) / (n_beats * n_beats))
np.save("tau_matrix", Tau)
