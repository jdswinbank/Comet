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

fig, (ax0, ax1, ax2) = pyplot.subplots(nrows=3)
pyplot.subplots_adjust(hspace=0.0, wspace=0.4)

num_bins = 100
plt_range = (0, 0.06)
pyplot.figure(1)

pyplot.subplot(3,1,1)
n, bins, patches = pyplot.hist(noepoll_notmpfs, num_bins, range=plt_range, weights=noepoll_notmpfs_weights)
pyplot.ylim(0, 0.06)
pyplot.xlim(plt_range)
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.text(0.95, 0.85, 'Poll reactor', transform=ax0.transAxes, horizontalalignment="right")

pyplot.subplot(3,1,2)
n, bins, patches = pyplot.hist(epoll_notmpfs, num_bins, range=plt_range, weights=epoll_notmpfs_weights)
pyplot.ylim(0, 0.06)
pyplot.xlim(plt_range)
pyplot.xticks(pyplot.xticks()[0], [])
pyplot.yticks(pyplot.yticks()[0][:-1], pyplot.yticks()[0][:-1])
pyplot.text(0.95, 0.85, 'EPoll reactor', transform=ax1.transAxes, horizontalalignment="right")

pyplot.ylabel("Fraction of events", fontsize="large", labelpad=10)

pyplot.subplot(3,1,3)
n, bins, patches = pyplot.hist(epoll_tmpfs, num_bins, range=plt_range, weights=epoll_tmpfs_weights)
pyplot.xlim(plt_range)
pyplot.yticks(pyplot.yticks()[0][:-2], pyplot.yticks()[0][:-2])
pyplot.text(0.95, 0.85, 'EPoll reactor & tmpfs', transform=ax2.transAxes, horizontalalignment="right")

pyplot.xlabel("Total latency (s)", fontsize="large")

pyplot.show()
