import arrow
import numpy
from collections import defaultdict
from hypercubeq import HypercubeQ
from traveltime import travel_time_from_patrol, travel_time_from_distance
from sklearn.impute import SimpleImputer

# DATA PREPARATION

# 1. year configuration
years = ["2013", "2014", "2015", "2016", "2017"]

# 2. get workload and count per beat (for building the arrival rates vectors `Lam`)
beat_info = defaultdict(lambda: defaultdict(lambda: {"workload": 0, "count": 0}))
with open("data/911.calls.concise.txt", "r", encoding='utf-8', errors='ignore') as f:
    for line in f.readlines():
        off_id, lat, lng, beat, call_t, disp_t, arv_t, clr_t = line.strip("\n").split("\t")
        workload = float(clr_t) - float(disp_t)
        year     = str(arrow.get(clr_t).year)
        if beat is not "" and workload > 0:
            beat_info[beat][year]["workload"] += workload
            beat_info[beat][year]["count"]    += 1
w_beats = list(beat_info.keys())
print("workload for beats:", w_beats)

# 3. get travel time (for building the traffic matrix `T`)
t_beats, tau = travel_time_from_patrol()
# - complete the missing entries in tau matrix
imputer = SimpleImputer(missing_values=0., strategy='mean')  
Tau     = imputer.fit_transform(tau)
print("travel time for beats:", t_beats)

# 4. get beats pairwise distance (for building the preference matrix `P`)
d_beats, dist = travel_time_from_distance()

# 5. get current design (`D`)
design  = defaultdict(lambda: [])
for beat in w_beats:
    design[beat[0]].append(beat)
print("current design:", design)



# EVALUATION

for zone in design.keys():
    for year in years:
        beats   = design[zone]
        n_atoms = len(beats)
        Lam     = np.array([ beat_info[beat][year]["count"] for beat in beats ])
        T       = np.array()
        P       = np.array()
        Y       = sum([ beat_info[beat][year]["workload"] for beat in beats ])
        hq = HypercubeQ(n_atoms, Lam=None, T=None, P=None, cap="zero", max_iter=10, q_len=100)