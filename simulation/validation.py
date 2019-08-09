import sys
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
print("[%s] workload for beats: %s" % (arrow.now(), w_beats), file=sys.stderr)

# 3. get travel time (for building the traffic matrix `T`)
t_beats, Tau = travel_time_from_patrol()
# - complete the missing entries in tau matrix
imputer = SimpleImputer(missing_values=0., strategy='mean')
Tau     = imputer.fit_transform(Tau)                           # traffic matrix
print("[%s] travel time for beats: %s" % (arrow.now(), t_beats), file=sys.stderr)

# 4. get beats pairwise distance (for building the preference matrix `P`)
d_beats, Dist = travel_time_from_distance()                    # preference matrix                                     
print("[%s] beats distance for beats: %s" % (arrow.now(), d_beats), file=sys.stderr)

# 5. get current design (`D`)
design  = defaultdict(lambda: [])                              # zone design
for beat in w_beats:
    design[beat[0]].append(beat)
print("[%s] current design: %s" % (arrow.now(), design), file=sys.stderr)



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
        Lam     = Lam / Lam.sum()
        T       = matrix_selection(Tau, beats, t_beats)
        P       = matrix_selection(Dist, beats, d_beats).argsort()
        print("[%s] for zone %s, year %s" % (arrow.now(), zone, year), file=sys.stderr)
        print("n_atoms", n_atoms, file=sys.stderr)
        print("Lam", Lam, file=sys.stderr)
        print("T", T, file=sys.stderr)
        print("P", P, file=sys.stderr)
        hq = HypercubeQ(n_atoms, Lam=Lam, T=T, P=P, cap="inf", max_iter=10, q_len=100)
        print("[%s] check hq model (%f)" % (arrow.now(), hq.Pi.sum() + hq.Pi_Q.sum()), file=sys.stderr)
        avg_T = hq.Tu               #
        Frac  = hq.Rho_1 + hq.Rho_2
        Y_hat = (Frac * Eta.sum() * (avg_T + mu)).sum()
        Y     = sum([ beat_info[beat][year]["workload"] for beat in beats ])
        print(Y_hat, Y, file=sys.stderr)
        print("%s\t%s\t%f\t%f" % (beat, year, Y, Y_hat))

# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages

# def plot_barchart(x_name, x, y_name, title, data_1, data_2, path):
#     with PdfPages(path) as pdf:
#         # Create lists for the plot
        
#         x_pos   = np.arange(data_1.shape[0])

#         x_pos_1 = np.arange(data_1.shape[0]) - 0.15
#         CTEs_1  = data_1.mean(axis=1)
#         error_1 = data_1.std(axis=1)

#         x_pos_2 = np.arange(data_2.shape[0]) + 0.15
#         CTEs_2  = data_2.mean(axis=1)
#         error_2 = data_2.std(axis=1)

#         # Build the plot
#         fig, ax = plt.subplots()
#         b1 = ax.bar(x_pos_1, CTEs_1, 
#             yerr=error_1, align='center', alpha=0.5, ecolor='black', capsize=3, width=.3)
#         b2 = ax.bar(x_pos_2, CTEs_2, 
#             yerr=error_2, align='center', alpha=0.5, ecolor='black', capsize=3, width=.3)
#         ax.set_ylabel(y_name)
#         ax.set_xlabel(x_name)
#         ax.set_xticks(x_pos)
#         ax.set_xticklabels(x)
#         # ax.set_title(title)
#         ax.yaxis.grid(True)

#         ax.legend((b1[0], b2[0]), ('simulated output', 'real data'))

#         # Save the figure and show
#         plt.tight_layout()
#         # plt.show()
#         pdf.savefig(fig)

# if __name__ == "__main__":
#     with open("/Users/woodie/Dropbox (GaTech)/Apps/Overleaf/2019 Doing Good with Good OR/references/results.csv") as f:
#         data  = [ line.strip("\n").split(",") for line in list(f)[1:] ]
#         print(data)
#         zones = list(set([ d[0] for d in data ]))
#         years = list(set([ d[1] for d in data ]))
#         zones.sort()
#         years.sort()
#         Y     = np.zeros((len(years), len(zones)))
#         Y_hat = np.zeros((len(years), len(zones)))
#         for d in data:
#             zone, year   = d[0], d[1]
#             z_idx, y_idx = zones.index(zone), years.index(year)
#             Y_hat[y_idx, z_idx] = d[2]
#             Y[y_idx, z_idx]     = d[3]    

#         plot_barchart("Years", years, "Zone workload (seconds)", "Zone workload over each year", Y_hat, Y, "comparison-year.pdf")
