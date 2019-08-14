import branca
import folium
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import statsmodels.api as sm
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable
from collections import defaultdict

data = defaultdict(lambda: defaultdict(lambda: 0))

with open("heuristic_result/data/final_workload.csv") as f:
    for line in list(f)[1:]:
        beat, year, workload = line.strip("\n").split(",")
        zone     = beat[0]
        workload = float(workload)
        if zone != "7" and zone != "0":
            data[year][zone] += workload

# Create some mock data
t = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
markers_on = [2013, 2014, 2015, 2016, 2017]
total_w = np.array([ sum(list(data[year].values())) for year in data ])
var_w   = np.array([ np.var(list(data[year].values())) for year in data ])

print(total_w)
print(var_w)
with PdfPages("workload-var-line-chart.pdf") as pdf:
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('year')
    ax1.set_ylabel('total workload (seconds)', color=color)
    ax1.plot(t, total_w, color=color)
    ax1b1 = ax1.plot(markers_on, total_w[:5], 'x', color=color)
    ax1b2 = ax1.plot([2018, 2019], total_w[-2:], 'o', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    # ax1.yaxis.grid(True, color=color, linestyle='--')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('variance of zone workload', color=color)  # we already handled the x-label with ax1
    ax2.plot(t, var_w, color=color)
    ax2b1 = ax2.plot(markers_on, var_w[:5], 'x', color=color)
    ax2b2 = ax2.plot([2018, 2019], var_w[-2:], 'o', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.grid(True, linestyle='--')

    axl = plt.gca()
    axl1 = axl.plot([], [], 'x', color='gray')
    axl2 = axl.plot([], [], 'o', color='gray')
    axl.legend((axl1[0], axl2[0]), ('data', 'prediction'), loc=2)

    ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # plt.show()
    pdf.savefig(fig)