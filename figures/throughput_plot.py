import sys
import json
import numpy
from matplotlib import pyplot
from matplotlib import gridspec

# The following is based on
# <http://wiki.scipy.org/Cookbook/Matplotlib/LaTeX_Examples>.
fig_width_pt = 252.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (numpy.sqrt(5)-1.0)/2.0
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width
fig_size =  [fig_width,fig_height]
params = {'backend': 'pdf',
          'text.usetex': True,
          'figure.figsize': fig_size,
          'figure.subplot.top': 0.97,
          'figure.subplot.right': 0.95}
pyplot.rcParams.update(params)
pyplot.rc("font", size=8, family="sans", serif="Computer Sans")

log_width = 0.1

aut_ax = []
aut_width = []
aut_mean = []
aut_std = []

sub_ax = []
sub_width = []
sub_mean = []
sub_std = []

total_width = []

missing = []

with open('throughput.json', 'r') as f:
    # We only want the 0ms latency data here
    rate = json.load(f)["0"]

for connections, data in rate.items():
        connections = float(connections)
        log_centre = numpy.log10(connections)
        bottom_edge = 10**(log_centre - log_width)
        top_edge = 10**(log_centre + log_width)
        aut_ax.append(bottom_edge)
        sub_ax.append(connections)
        aut_width.append(connections - bottom_edge)
        sub_width.append(top_edge - connections)
        total_width.append(top_edge - bottom_edge)

        aut_mean.append(data['author']['mean'])
        aut_std.append(data['author']['std'])
        sub_mean.append(data['subscriber']['mean'])
        sub_std.append(data['subscriber']['std'])
        missing.append(data['missing'])

f = pyplot.figure()
gs = gridspec.GridSpec(3, 1, height_ratios=[2,1,1], wspace=0.2, hspace=0.0)

pyplot.subplot(gs[0])
pyplot.bar(left=aut_ax, width=aut_width, height=aut_mean, color="b")
pyplot.bar(left=sub_ax, width=sub_width, height=sub_mean, color="g")
pyplot.legend(["Author", "Subscriber"], ncol=2, fontsize=8)
pyplot.ylim(0,650)
pyplot.ylabel("Throughput (events/second)")
pyplot.xscale("log")
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.xlim(0.5,10**3)
pyplot.yticks(pyplot.yticks()[0][1:-1], [100,200,300,400,500,600])

pyplot.subplot(gs[1])
pyplot.bar(left=aut_ax, width=aut_width, height=aut_std, color="b")
pyplot.bar(left=sub_ax, width=sub_width, height=sub_std, color="g")
pyplot.ylabel("Std. Dev.", labelpad=10)
pyplot.xscale("log")
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.xlim(0.5,10**3)
pyplot.yticks(pyplot.yticks()[0][1:-1], [10,20,30,40,50," 60"])

pyplot.subplot(gs[2])
pyplot.bar(left=aut_ax, width=total_width, height=missing, color="r", log=True)
pyplot.ylabel("Missing events")
pyplot.xscale("log")
pyplot.xlim(0.5,10**3)
pyplot.xlabel("Number of concurrent connections")
pyplot.yticks([10, 100], [10, 100])

pyplot.savefig(sys.argv[1])
