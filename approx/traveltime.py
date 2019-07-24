import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.impute import SimpleImputer
from matplotlib.backends.backend_pdf import PdfPages

def travel_time_from_patrol():
    """
    Get travel time estimation from the police patrolling records which includes
    the travel time information for each individual patrol routes associated with
    the officer id.
    """
    # extract route data from file
    routes = []
    beats  = set()
    with open("data/patrol.route.txt", "r") as f:
        for line in f.readlines():
            data = line.strip().split("\t")
            start_beat, end_beat, dt = data[0], data[1], float(data[2])
            routes.append([start_beat, end_beat, dt])
            beats = beats | set({start_beat, end_beat})

    # get beats list
    beats   = list(beats)
    beats.sort()
    n_beats = len(beats) 
    print(beats)
    print(n_beats)

    # calculate total travel time per route (start beat, end beat, travel time)
    total_t = np.zeros((n_beats, n_beats)) # total travel time per route
    total_n = np.zeros((n_beats, n_beats)) # total number of samples per route 
    for route in routes:
        start_idx = beats.index(route[0])
        end_idx   = beats.index(route[1])
        dt        = route[2]
        total_t[start_idx][end_idx] += dt
        total_n[start_idx][end_idx] += 1

    # check if missing routes were inter-zones
    # - missing routes:   925   interzone   37  intrazone
    # - zero time routes: 1898  interzone   45  intrazone
    n_missing_routes   = len(np.where(total_n == 0)[0])
    n_zero_routes      = len(np.where(total_t == 0)[0])
    n_interzone_routes = 0
    n_intrazone_routes = 0
    start_ids, end_ids = np.where(total_t == 0)
    start_zones        = [ beats[start_id][0] for start_id in start_ids.tolist() ]
    end_zones          = [ beats[end_id][0] for end_id in end_ids.tolist() ]  
    for start_zone, end_zone in zip(start_zones, end_zones):
        if start_zone == end_zone:
            n_intrazone_routes += 1
        else:
            n_interzone_routes += 1
    print(n_interzone_routes, n_intrazone_routes, n_missing_routes, n_zero_routes)

    # travel time estimation (missing samples are set to be zero)
    Tau = np.divide(total_t, total_n, out=np.zeros_like(total_t), where=total_n!=0)
    # np.save("data/p_tau", Tau)
    print(Tau)
    return beats, Tau

def travel_time_from_distance():
    """
    Get travel time estimation based on the distances of the centroids of two beats.
    """
    # extract centroids data from file
    beats_centroids = {}
    with open("data/beats_centroids.csv", "r") as f:
        for line in f.readlines():
            beat, lng, lat = line.strip().split(",")
            beats_centroids[beat] = [float(lat), float(lng)]

    # helper function for Hamming distance
    def hamming(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # calculate the pairwise distance between beats
    beats   = list(beats_centroids.keys())
    beats.sort()
    n_beats = len(beats)
    Tau     = np.zeros((n_beats, n_beats))
    for from_beat in beats:
        for to_beat in beats:
            from_beat_idx = beats.index(from_beat)
            to_beat_idx   = beats.index(to_beat)
            Tau[from_beat_idx][to_beat_idx] = hamming(beats_centroids[from_beat], beats_centroids[to_beat])
    # np.save("data/d_tau", Tau)
    print(beats)
    print(n_beats)
    print(Tau)
    return beats, Tau

def travel_time_vs_hamming_distance(p_beats, p_tau, d_beats, d_tau):
    """
    plot the hamming distance between two beats vs its corresponding avg travel time.
    """
    # p_beats, p_tau = travel_time_from_patrol()
    # d_beats, d_tau = travel_time_from_distance()
    # construct x: distance of centroids, y: travel time
    X, Y = [], []
    for start_beat in d_beats:
        for end_beat in d_beats:
            if start_beat in p_beats and end_beat in p_beats:
                p_start_beat_idx, p_end_beat_idx = p_beats.index(start_beat), p_beats.index(end_beat)
                d_start_beat_idx, d_end_beat_idx = d_beats.index(start_beat), d_beats.index(end_beat)
                if p_tau[p_start_beat_idx][p_end_beat_idx] > 0:
                    x, y = d_tau[d_start_beat_idx][d_end_beat_idx], p_tau[p_start_beat_idx][p_end_beat_idx]
                    X.append(x)
                    Y.append(y)

    # plot
    plt.scatter(X, Y, s=0.1)
    plt.xlabel("distance")
    plt.ylabel("travel time")
    plt.show()

    ### Deprecated ###
    # # helper function for Hamming distance
    # def hamming(a, b):
    #     return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # # construct travel time vs hamming distance pairs
    # x = []
    # y = []
    # with open("data/patrol.route.ext.txt", "r") as f:
    #     for line in f.readlines():
    #         start_beat, start_lat, start_lng, end_beat, end_lat, end_lng, dt = line.strip("\n").split("\t")
    #         if float(dt) > 0:
    #             x.append(hamming([float(start_lat), float(start_lng)], [float(end_lat), float(end_lng)]))
    #             y.append(float(dt))
    # print(len(x))
    # # plot
    # plt.scatter(x, y, s=0.1)
    # plt.xlabel("distance")
    # plt.ylabel("travel time")
    # plt.show()
    

if __name__ == "__main__":
    p_beats, p_tau = travel_time_from_patrol()
    # d_beats, d_tau = travel_time_from_distance()
    
    imputer   = SimpleImputer(missing_values=0., strategy='mean')  
    tau_prime = imputer.fit_transform(p_tau)

    print(tau_prime)
    np.save("data/tau", tau_prime)
    with PdfPages("result/tau_prime.pdf") as pdf:
        fig, ax = plt.subplots(1, 1)
        plt.rc('xtick',labelsize=.1)
        plt.rc('ytick',labelsize=.1)
        ticks        = [7, 20, 33, 46, 59, 72]
        ticks_labels = ["zone 1", "zone 2", "zone 3", "zone 4", "zone 5", "zone 6"]
        # plt.imshow(np.log(p_tau + 1e-8))
        plt.imshow(tau_prime)
        ax.grid(False)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(ticks_labels)
        ax.set_yticklabels(ticks_labels)
        pdf.savefig(fig)

    # travel_time_vs_hamming_distance(p_beats, tau_prime, d_beats, d_tau)