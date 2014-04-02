import sys
import os
import numpy
import glob
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

overall = {}

for n_subscribers in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
    directory = "%d_subscribers" % (n_subscribers)
    data = []
    for filename in glob.glob(os.path.join(directory, "*log")):
        with open(filename, "r") as f:
            data.extend(f.readlines())
    overall[n_subscribers] = numpy.array([float(x) for x in data])

#print overall
x_vals, y_vals, y_errs, y_min, y_max = [], [], [], [], []
for key, value in sorted(overall.items()):
    x_vals.append(key)
    y_vals.append(value.mean())
    y_errs.append(value.std())
    y_min.append(value.min())
    y_max.append(value.max())
    print("%d subscribers: %f/%f/%f/%f min/max/mean/std" % (key, value.min(), value.max(), value.mean(), value.std()))

#pyplot.plot(x_vals, y_vals)
pyplot.errorbar(x_vals, y_vals, yerr=y_errs, fmt='b-')
pyplot.plot(x_vals, y_min, 'g--')
pyplot.plot(x_vals, y_max, 'g--')
pyplot.xscale("log")
pyplot.yscale("log")
pyplot.xlabel("Number of subscribers")
pyplot.ylabel("Latency (s)")

pyplot.savefig(sys.argv[1])
