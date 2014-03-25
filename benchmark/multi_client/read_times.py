import os
import numpy
import glob
from matplotlib import pyplot

overall = {}

for n_subscribers in [2, 4, 8, 16, 32, 64, 256]:
    directory = "%d_subscribers" % (n_subscribers)
    data = []
    for filename in glob.glob(os.path.join(directory, "*log")):
        with open(filename, "r") as f:
            data.extend(f.readlines())
    overall[n_subscribers] = numpy.array([float(x) for x in data])

#print overall
x_vals, y_vals = [], []
for key, value in sorted(overall.items()):
    x_vals.append(key)
    y_vals.append(value.mean())
    print("%d subscribers: %f/%f/%f/%f min/max/mean/std" % (key, value.min(), value.max(), value.mean(), value.std()))

pyplot.plot(x_vals, y_vals)
pyplot.show()
