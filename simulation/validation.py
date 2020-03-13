import sys
import arrow
import copy
import random
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statistics as stats
from itertools import combinations
from matplotlib.backends.backend_pdf import PdfPages
from collections import defaultdict
from hypercubeq import HypercubeQ
from traveltime import travel_time_from_patrol, travel_time_from_distance
from sklearn.impute import SimpleImputer
from tqdm import tqdm

# year configuration
years = ["2013", "2014", "2015", "2016", "2017"]



def matrix_selection(mat, selected_beats, all_beats):
    """Helper function for matrix selection"""
    cols = [ all_beats.index(beat) for beat in selected_beats ]
    rows = [ [col] for col in cols ]
    return mat[rows, cols]


    
def data_preparation():
    """Data Preparation"""
    # 1. get workload and count per beat (for building the arrival rates vectors `Lam`)
    beat_info = defaultdict(lambda: defaultdict(lambda: {"workload": 0, "count": 0}))
    n_calls, serv_t = 0, 0
    with open("../data/rawdata/911.calls.concise.txt", "r", encoding='utf-8', errors='ignore') as f:
        for line in f.readlines():
            off_id, lat, lng, beat, call_t, disp_t, arv_t, clr_t = line.strip("\n").split("\t")
            beat     = beat.strip()
            n_calls += 1
            serv_t  += float(clr_t) - float(arv_t)
            workload = float(clr_t) - float(disp_t)
            year     = str(arrow.get(clr_t).year)
            if beat is not "" and workload > 0:
                beat_info[beat][year]["workload"] += workload
                beat_info[beat][year]["count"]    += 1
    mu      = float(serv_t) / float(n_calls)                       # service rate Mu
    w_beats = list(beat_info.keys())
    # print("[%s] workload for beats: %s" % (arrow.now(), w_beats), file=sys.stderr)

    # 2. get travel time (for building the traffic matrix `T`)
    t_beats, Tau = travel_time_from_patrol()
    # - complete the missing entries in tau matrix
    imputer = SimpleImputer(missing_values=0., strategy='mean')
    Tau     = imputer.fit_transform(Tau)                           # traffic matrix
    # print("[%s] travel time for beats: %s" % (arrow.now(), t_beats), file=sys.stderr)

    # 3. get beats pairwise distance (for building the preference matrix `P`)
    d_beats, Dist = travel_time_from_distance()                    # preference matrix                                     
    # print("[%s] beats distance for beats: %s" % (arrow.now(), d_beats), file=sys.stderr)

    # 4. get current design (`D`)
    design  = defaultdict(lambda: [])                              # zone design
    for beat in w_beats:
        design[beat[0]].append(beat)
    print("[%s] current design: %s" % (arrow.now(), design), file=sys.stderr)

    return beat_info, mu, t_beats, Tau, d_beats, Dist, design



def plot_barchart(x_name, x, y_name, title, data_1, data_2, path):
    """Plot evaluation results as a barchart"""

    with PdfPages(path) as pdf:
        # Create lists for the plot
        
        x_pos   = np.arange(data_1.shape[0])

        x_pos_1 = np.arange(data_1.shape[0]) - 0.15
        CTEs_1  = data_1.mean(axis=1)
        error_1 = data_1.std(axis=1)

        x_pos_2 = np.arange(data_2.shape[0]) + 0.15
        CTEs_2  = data_2.mean(axis=1)
        error_2 = data_2.std(axis=1)

        # Build the plot
        fig, ax = plt.subplots()
        b1 = ax.bar(x_pos_1, CTEs_1, 
            yerr=error_1, align='center', alpha=0.5, ecolor='black', capsize=3, width=.3)
        b2 = ax.bar(x_pos_2, CTEs_2, 
            yerr=error_2, align='center', alpha=0.5, ecolor='black', capsize=3, width=.3)
        ax.set_ylabel(y_name)
        ax.set_xlabel(x_name)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x)
        # ax.set_title(title)
        ax.yaxis.grid(True)

        ax.legend((b1[0], b2[0]), ('simulated output', 'real data'))

        # Save the figure and show
        plt.tight_layout()
        # plt.show()
        pdf.savefig(fig)



def generate_design(old_design, min_rmv=2, n_rmv=5):
    """Generate random design given the adjacency strucutre of beats and original design"""

    with open("../data/beats_graph.csv") as f:
        data      = list(f)
        all_beats = [ beat.strip('"') for beat in data[0].strip("\n").split(",")[1:] ]
        graph     = np.zeros((len(all_beats), len(all_beats)))
        for i in range(1, len(data)):
            graph[i-1, :] =  np.array([ int(d.strip('"')) for d in data[i].strip("\n").split(",")[1:] ])

    def adjacent_designs(design):
        adj_designs = []
        for zone in design:
            moved_beat = []
            if zone == "7":
                continue
            for beat in design[zone]:
                beat_id        = all_beats.index(beat)
                neighbor_beats = [ all_beats[i] for i in np.where(graph[beat_id] == 1)[0] ]
                # for each boundary beat
                # if it is out of the zone, then put it into the zone
                for nbeat in neighbor_beats:
                    nzone = None
                    for z in design:
                        if nbeat in design[z]:
                            nzone = z
                            break
                    if nzone != zone and nzone is not None and nbeat not in moved_beat:
                        adj_design = copy.deepcopy(design)
                        adj_design[zone].append(nbeat)
                        adj_design[nzone].pop(adj_design[nzone].index(nbeat))
                        # print("find a new adjacent design!")
                        # print("move beat", nbeat)
                        # print("from zone", nzone, adj_design[nzone])
                        # print("to zone", zone, adj_design[zone])
                        moved_beat.append(nbeat)
                        # add an adjacent design
                        adj_designs.append(adj_design)
        return adj_designs
        
    # select a random subset of the old design as initial design
    n = 5 # number of dropout
    for zone in old_design:
        # get current beats set of the zone
        beats            = old_design[zone]
        random.shuffle(beats)
        # drop out n beats from each zone
        beats            = beats[:len(beats)-n]
        old_design[zone] = beats
    
    # find the adjacent designs
    new_designs  = []
    new_designs += adjacent_designs(old_design)
    print("swap 1 beat", len(new_designs))
    new_designs += adjacent_designs(new_designs[-1])
    print("swap 2 beats", len(new_designs))
    new_designs += adjacent_designs(new_designs[-1])
    print("swap 3 beats", len(new_designs))
    new_designs += adjacent_designs(new_designs[-1])
    print("swap 4 beats", len(new_designs))
    new_designs += adjacent_designs(new_designs[-1])

    return new_designs


def main_1():
    """Evaluate the simulation model"""

    beat_info, mu, t_beats, Tau, d_beats, Dist, design = data_preparation()

    print("finish data preprocessing")

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
            hq    = HypercubeQ(n_atoms, Lam=Lam, T=T, P=P, cap="inf", max_iter=10, q_len=100)
            print("[%s] check hq model (%f)" % (arrow.now(), hq.Pi.sum() + hq.Pi_Q.sum()), file=sys.stderr)
            avg_T = hq.Tu               
            Frac  = hq.Rho_1 + hq.Rho_2
            Y_hat = (Frac * Eta.sum() * (avg_T + mu)).sum()
            Y     = sum([ beat_info[beat][year]["workload"] for beat in beats ])
            print(Y_hat, Y, file=sys.stderr)
            print("%s\t%s\t%f\t%f" % (zone, year, Y, Y_hat))


def main_3():
    """Simulation Model Evaluation"""

    with open("/Users/woodie/Dropbox (GaTech)/Apps/Overleaf/2019 Doing Good with Good OR/references/results.csv") as f:
        data  = [ line.strip("\n").split(",") for line in list(f)[1:] ]
        print(data)
        zones = list(set([ d[0] for d in data ]))
        years = list(set([ d[1] for d in data ]))
        zones.sort()
        years.sort()
        Y     = np.zeros((len(years), len(zones)))
        Y_hat = np.zeros((len(years), len(zones)))
        for d in data:
            zone, year   = d[0], d[1]
            z_idx, y_idx = zones.index(zone), years.index(year)
            Y_hat[y_idx, z_idx] = d[2]
            Y[y_idx, z_idx]     = d[3]    

        plot_barchart("Years", years, "Zone workload (seconds)", "Zone workload over each year", Y_hat, Y, "comparison-year.pdf")

        

def main_4():
    """Generate random valid design and get corresponding simulation output"""

    beat_info, mu, t_beats, Tau, d_beats, Dist, old_design = data_preparation()
    print("finish data preprocessing")

    new_designs = generate_design(old_design, min_rmv=2, n_rmv=4)
    print("finish design generation")

    validbeats = []
    for z in old_design:
        if z != "7":
            validbeats += [ beat for beat in old_design[z] ]
    print(validbeats)

    Xs = []
    Ys = []
    lY = []
    lX = []
    year = '2017'
    for design in tqdm(new_designs):
        Y = []
        for zone in design:
            if zone == "7":
                continue
            # build operations model
            beats   = design[zone]
            n_atoms = len(beats)
            Eta     = np.array([ beat_info[beat][year]["count"] for beat in beats ])
            Lam     = np.array([ beat_info[beat][year]["count"] for beat in beats ])
            Lam     = Lam / Lam.sum()
            T       = matrix_selection(Tau, beats, t_beats)
            P       = matrix_selection(Dist, beats, d_beats).argsort()
            hq    = HypercubeQ(n_atoms, Lam=Lam, T=T, P=P, cap="inf", max_iter=10, q_len=100)
            avg_T = hq.Tu               
            Frac  = hq.Rho_1 + hq.Rho_2
            Y_hat = (Frac * Eta.sum() * (avg_T + mu)).sum()
            Y.append(Y_hat)
        output = [ str(year), str(stats.variance(Y)) ] + [ str(y) for y in Y ]
        Ys.append(output)
        # build approximation model
        zones = list(design.keys())
        x = np.zeros((len(validbeats), 6)) 
        for z in design:
            if z == "7":
                continue
            for beat in validbeats:
                if beat in design[z]:
                    x[validbeats.index(beat), zones.index(z)] = 1
        # x = np.zeros(len(validbeats)) 
        # for beat in validbeats:
        #     x[validbeats.index(beat)] = beat_info[beat][year]["count"] * Tau[t_beats.index(beat),:].sum()
        lY.append(stats.variance(Y))
        lX.append(x.flatten())

    with open("sim_output.txt", "w") as f:
        for Y in Ys:
            f.write("%s\n" % ",".join(Y))

    # linear regression model
    lX = np.array(lX)
    nlX = (lX - lX.min()) / (lX.max() - lX.min())
    lY = np.array(lY)
    nlY = (lY - lY.min()) / (lY.max() - lY.min())

    # X       = sm.add_constant(X)
    model   = sm.OLS(nlY, nlX)
    results = model.fit()
    approxs = results.predict(nlX)
    approxs = approxs * (lY.max() - lY.min()) + lY.min()
    approxs = np.array(approxs) #.reshape([len(new_designs), 6]).sum(axis=1)
    print(results.summary())
    print(approxs)

    with open("sim_output.txt", "w") as f:
        for i in range(len(Ys)):
            Ys[i].append(str(approxs[i]))
            f.write("%s\n" % ",".join(Ys[i]))



if __name__ == "__main__":
    np.random.seed(2)
    main_4()

    # import matplotlib.pyplot as plt
    # from matplotlib.backends.backend_pdf import PdfPages

    # with open("sim_output.txt", "r") as f:
    #     data = [ line.strip("\n").split(",") for line in f ]

    # x     = list(range(len(data)))
    # y     = np.array([ float(d[1]) for d in data ]) / (10**14)
    # y_hat = np.array([ float(d[-1]) for d in data ]) / (10**14)

    # plt.rc('text', usetex=True)
    # plt.rc("font", family="serif")

    # with PdfPages("sim-approx-res.pdf") as pdf:
    #     fig, ax = plt.subplots()

    #     # Using set_dashes() to modify dashing of an existing line
    #     line1, = ax.plot(x, y, label=r"$f(D_i)$ simulated objectives", linestyle="-", color="blue", linewidth=2)
    #     line2, = ax.plot(x, y_hat, label=r"$\tilde{f}(D_i)$ approximated objectives", linestyle="-.", color="red", linewidth=1.5)

    #     for i in [50, 77]:
    #         plt.axvline(x=i, ymin=0, ymax=y[i] * 1.5, linestyle=":", color="gray", linewidth=1)

    #     ax.set_xlabel(r"decision index $i$")
    #     ax.set_ylabel(r"scaled objective value")

    #     ax.legend()
    #     # plt.show()
    #     pdf.savefig(fig)

