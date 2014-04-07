import sys
import os
import numpy
import glob
import json
from matplotlib import pyplot

# The following is based on
# <http://wiki.scipy.org/Cookbook/Matplotlib/LaTeX_Examples>.
fig_width_pt = 252.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (numpy.sqrt(5)-1.0)/2.0
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean
fig_size =  [fig_width,fig_height]
params = {'backend': 'pdf',
          'text.usetex': True,
          'figure.figsize': fig_size,
          'figure.subplot.bottom': 0.15,
          'figure.subplot.left': 0.15,
          'figure.subplot.top': 0.95,
          'figure.subplot.right': 0.97}
pyplot.rcParams.update(params)
pyplot.rc("font", size=8, family="sans", serif="Computer Sans")

with open("multisubscriber.json", "r") as f:
    data = json.load(f)

pyplot.errorbar(data["n_subscribers"], data["latency"], yerr=data["std"], fmt='b-')
pyplot.plot(data["n_subscribers"], data["min"], 'g--')
pyplot.plot(data["n_subscribers"], data["max"], 'g--')
pyplot.xscale("log")
pyplot.yscale("log")
pyplot.xlabel("Number of subscribers")
pyplot.ylabel("Latency (s)")

pyplot.savefig(sys.argv[1])
