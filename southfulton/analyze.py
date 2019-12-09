import statistics
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
matplotlib.rcParams['text.usetex'] = True

from designinit import beat_with_max_workload

def mean_variance_calculation(prefix, call_fname, n_beat_range):

    beat_vars  = []
    beat_means = [] 
    for n_beat in n_beat_range:
        fname = "result/grid-%s%s-nbeat-%d.npy" % (prefix, call_fname, n_beat)
        grid_table = np.load(fname) 
        _, beats_set, beats_workload = beat_with_max_workload(grid_table)
        beats_workload = np.array(beats_workload) / 3600
        var  = statistics.variance(beats_workload)
        mean = statistics.mean(beats_workload)
        beat_vars.append(var)
        beat_means.append(mean)
    print(beat_means)
    print(beat_vars)
    return np.array(beat_means), np.array(beat_vars)

if __name__ == "__main__":
    call_fname   = "Jan-APR-2019-PD"
    n_beat_range = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    init_beat_means, init_beat_vars = mean_variance_calculation("", call_fname, n_beat_range)
    reds_beat_means, reds_beat_vars = mean_variance_calculation("redesign-", call_fname, n_beat_range)

    with PdfPages("workload-mean-chart.pdf") as pdf:
        fig, ax = plt.subplots()

        ax.plot(n_beat_range, reds_beat_means/365)
        plt.xlabel('number of beats')
        plt.ylabel('average workload (hours/day)')
        pdf.savefig(fig)

    with PdfPages("workload-var-chart.pdf") as pdf:
        fig, ax = plt.subplots()

        l1 = ax.plot(n_beat_range, init_beat_vars)
        l2 = ax.plot(n_beat_range, reds_beat_vars)
        plt.xlabel('number of beats')
        plt.ylabel('variance of beat workload')

        ax.legend(('greedy dichotomy', 'heuristic refined'))
        pdf.savefig(fig)

        # color = 'tab:red'
        # ax1.set_xlabel('number of beats')
        # ax1.set_ylabel('average workload (hours/year)', color=color)
        # l1 = ax1.plot(n_beat_range, beat_means, color=color)
        # ax1.tick_params(axis='y', labelcolor=color)
        # # ax1.yaxis.grid(True, color=color, linestyle='--')

        # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        # color = 'tab:blue'
        # ax2.set_ylabel('variance of zone workload', color=color)  # we already handled the x-label with ax1
        # l2 = ax2.plot(n_beat_range, beat_vars, color=color)
        # ax2.tick_params(axis='y', labelcolor=color)
        # # ax2.yaxis.grid(True, linestyle='--')

        # # color = 'tab:blue'
        # # ax2.plot([2018, 2019], [161256471666666.53, 190791481666666.66], '*', color=color)
        # # # plot vertical dash line
        # # ax2.plot([2018, 2018], [161256471666666.53, var_w[5]], 'k--', lw=.8)
        # # ax2.plot([2019, 2019], [190791481666666.66, var_w[6]], 'k--', lw=.8)

        # # axl  = plt.gca()
        # # axl1 = axl.plot([], [], '*', color='red')
        # # axl2 = axl.plot([], [], '*', color='blue')
        # # # axl3 = axl.plot([], [], '*', color='blue')
        # # axl.legend((axl1, axl2), ('initialization mean', 'initialization variance'), loc=2)

        # # ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))

        # fig.tight_layout()  # otherwise the right y-label is slightly clipped
        # # plt.show()
        # pdf.savefig(fig)

