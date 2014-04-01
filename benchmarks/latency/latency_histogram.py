import sys
import numpy
from matplotlib import pyplot

with open('1sub-noepoll-notmpfs.log', 'r') as f:
    noepoll_notmpfs = numpy.array([float(x) for x in f.readlines()])
    noepoll_notmpfs_weights = numpy.ones(noepoll_notmpfs.shape) / len(noepoll_notmpfs)

with open('1sub-epoll-notmpfs.log', 'r') as f:
    epoll_notmpfs = numpy.array([float(x) for x in f.readlines()])
    epoll_notmpfs_weights = numpy.ones(epoll_notmpfs.shape) / len(epoll_notmpfs)

with open('1sub-epoll-tmpfs.log', 'r') as f:
    epoll_tmpfs = numpy.array([float(x) for x in f.readlines()])
    epoll_tmpfs_weights = numpy.ones(epoll_tmpfs.shape) / len(epoll_tmpfs)


print("No EPoll, no tmpfs: %f +- %f s; max %f" %
    (noepoll_notmpfs.mean(), noepoll_notmpfs.std(), noepoll_notmpfs.max())
)

print("EPoll, no tmpfs: %f +- %f s; max %f" %
    (epoll_notmpfs.mean(), epoll_notmpfs.std(), epoll_notmpfs.max())
)

print("EPoll, tmpfs: %f +- %f s; max %f" %
    (epoll_tmpfs.mean(), epoll_tmpfs.std(), epoll_tmpfs.max())
)

# The following is based on
# <http://wiki.scipy.org/Cookbook/Matplotlib/LaTeX_Examples>.
fig_width_pt = 252.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width
fig_size =  [fig_width,fig_height]
params = {'backend': 'pdf',
          'text.usetex': True,
          'figure.figsize': fig_size}
pyplot.rcParams.update(params)
pyplot.rc("font", size=8, family="sans", serif="Computer Sans")

fig, (ax0, ax1, ax2) = pyplot.subplots(nrows=3)
pyplot.subplots_adjust(hspace=0.0, wspace=0.2)

num_bins = 50
plt_range = (0, 0.06)
pyplot.figure(1)

pyplot.subplot(3,1,1)
n, bins, patches = pyplot.hist(noepoll_notmpfs, num_bins, range=plt_range, weights=noepoll_notmpfs_weights, histtype="step")
pyplot.ylim(0, 0.12)
pyplot.xlim(plt_range)
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.yticks(pyplot.yticks()[0][1:-1], pyplot.yticks()[0][1:-1])
pyplot.text(0.95, 0.85, 'Poll reactor', transform=ax0.transAxes, horizontalalignment="right")

pyplot.subplot(3,1,2)
n, bins, patches = pyplot.hist(epoll_notmpfs, num_bins, range=plt_range, weights=epoll_notmpfs_weights, histtype="step")
pyplot.ylim(0, 0.12)
pyplot.xlim(plt_range)
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.yticks(pyplot.yticks()[0][1:-1], pyplot.yticks()[0][1:-1])
pyplot.text(0.95, 0.85, 'EPoll reactor', transform=ax1.transAxes, horizontalalignment="right")

pyplot.ylabel("Fraction of events", labelpad=2)

pyplot.subplot(3,1,3)
n, bins, patches = pyplot.hist(epoll_tmpfs, num_bins, range=plt_range, weights=epoll_tmpfs_weights, histtype="step")
pyplot.ylim(0, 1.0)
pyplot.xlim(plt_range)
pyplot.yticks(pyplot.yticks()[0][1:-1], pyplot.yticks()[0][1:-1])
pyplot.text(0.95, 0.85, 'EPoll reactor \& tmpfs', transform=ax2.transAxes, horizontalalignment="right")

pyplot.xlabel("Total latency (s)")

pyplot.savefig(sys.argv[1])
