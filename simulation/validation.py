import arrow
import numpy as np
from collections import defaultdict
from hypercubeq import HypercubeQ
from traveltime import travel_time_from_patrol, travel_time_from_distance
from sklearn.impute import SimpleImputer

# DATA PREPARATION

# 1. year configuration
years = ["2013", "2014", "2015", "2016", "2017"]

# 2. get workload and count per beat (for building the arrival rates vectors `Lam`)
beat_info = defaultdict(lambda: defaultdict(lambda: {"workload": 0, "count": 0}))
n_calls, serv_t = 0, 0
with open("data/911.calls.concise.txt", "r", encoding='utf-8', errors='ignore') as f:
    for line in f.readlines():
        off_id, lat, lng, beat, call_t, disp_t, arv_t, clr_t = line.strip("\n").split("\t")
        n_calls += 1
        serv_t  += float(clr_t) - float(arv_t)
        workload = float(clr_t) - float(disp_t)
        year     = str(arrow.get(clr_t).year)
        if beat is not "" and workload > 0:
            beat_info[beat][year]["workload"] += workload
            beat_info[beat][year]["count"]    += 1
mu      = float(serv_t) / float(n_calls)                       # service rate Mu
w_beats = list(beat_info.keys())
print("[%s] workload for beats: %s" % (arrow.now(), w_beats))

# 3. get travel time (for building the traffic matrix `T`)
t_beats, Tau = travel_time_from_patrol()
# - complete the missing entries in tau matrix
imputer = SimpleImputer(missing_values=0., strategy='mean')
Tau     = imputer.fit_transform(Tau)                           # traffic matrix
print("[%s] travel time for beats: %s" % (arrow.now(), t_beats))

# 4. get beats pairwise distance (for building the preference matrix `P`)
d_beats, Dist = travel_time_from_distance()                    # preference matrix                                     
print("[%s] beats distance for beats: %s" % (arrow.now(), d_beats))

# 5. get current design (`D`)
design  = defaultdict(lambda: [])                              # zone design
for beat in w_beats:
    design[beat[0]].append(beat)
print("[%s] current design: %s" % (arrow.now(), design))



# EVALUATION

def matrix_selection(mat, selected_beats, all_beats):
    cols = [ all_beats.index(beat) for beat in selected_beats ]
    rows = [ [col] for col in cols ]
    return mat[rows, cols]

for zone in design.keys():
    for year in years:
        beats   = design[zone]
        n_atoms = len(beats)
        Eta     = np.array([ beat_info[beat][year]["count"] for beat in beats ])
        Lam     = np.array([ beat_info[beat][year]["count"] for beat in beats ]) # TODO: Use lam estimation
        T       = matrix_selection(Tau, beats, t_beats)
        P       = matrix_selection(Dist, beats, d_beats).argsort()
        print("[%s] for zone %s, year %s" % (arrow.now(), zone, year))
        print("n_atoms", n_atoms)
        print("Lam", Lam)
        print("T", T)
        print("P", P)
        hq = HypercubeQ(n_atoms, Lam=Lam, T=T, P=P, cap="inf", max_iter=10, q_len=100)
        print("[%s] check hq model (%f)" % (arrow.now(), hq.Pi.sum() + hq.Pi_Q.sum()))
        avg_T = hq.Tu               #
        Frac  = hq.Rho_1 + hq.Rho_2
        Y_hat = (Frac * Eta.sum() * (avg_T + mu)).sum()
        Y     = sum([ beat_info[beat][year]["workload"] for beat in beats ])
        print(Y_hat, Y)
        