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

with open("../heuristic_result/data/final_workload.csv") as f:
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

plt.rc('text', usetex=True)
plt.rc("font", family="serif")
with PdfPages("workload-var-line-chart.pdf") as pdf:
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('year')
    ax1.set_ylabel('total workload (hours/year)', color=color)
    ax1.plot(t, total_w, color=color)
    ax1.plot(markers_on, total_w[:5], 'x', color=color)
    ax1.plot([2018, 2019], total_w[-2:], 'o', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    # ax1.yaxis.grid(True, color=color, linestyle='--')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('variance of zone workload', color=color)  # we already handled the x-label with ax1
    ax2.plot(t, var_w, color=color)
    ax2.plot(markers_on, var_w[:5], 'x', color=color)
    ax2.plot([2018, 2019], var_w[-2:], 'o', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.grid(True, linestyle='--')

    color = 'tab:blue'
    ax2.plot([2018, 2019], [161256471666666.53, 190791481666666.66], '*', color=color)
    # plot vertical dash line
    ax2.plot([2018, 2018], [161256471666666.53, var_w[5]], 'k--', lw=.8)
    ax2.plot([2019, 2019], [190791481666666.66, var_w[6]], 'k--', lw=.8)

    axl = plt.gca()
    axl1 = axl.plot([], [], 'x', color='gray', lw=2)
    axl2 = axl.plot([], [], 'o', color='gray', lw=2)
    axl3 = axl.plot([], [], '*', color='blue', lw=2)
    axl.legend((axl1[0], axl2[0], axl3[0]), ('data with existing plan', 'prediction with existing plan', 'prediction with redesigned plan'), loc=2)

    ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # plt.show()
    pdf.savefig(fig)