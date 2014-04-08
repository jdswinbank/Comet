import numpy
from matplotlib import pyplot
from twisted.python import usage
from utils import load_json
from utils import write_json
from utils import write_figure
from utils import configure_pyplot
from utils import PlotOptions

class AggregateOptions(usage.Options):
    def parseArgs(self, noepoll_notmpfs, epoll_notmpfs, epoll_tmpfs, output):
        self['noepoll_notmpfs'] = noepoll_notmpfs
        self['epoll_notmpfs'] = epoll_notmpfs
        self['epoll_tmpfs'] = epoll_tmpfs
        self['output_file'] = output


class Options(usage.Options):
    subCommands = [['plot', None, PlotOptions, "Generate plot"],
                   ['aggregate', None, AggregateOptions, "Aggregate data"]]


def aggregate_logs(noepoll_notmpfs, epoll_notmpfs, epoll_tmpfs):
    data = {}

    with open(noepoll_notmpfs, 'r') as f:
        data['noepoll_notmpfs'] = [float(x) for x in f.readlines()]

    print("No EPoll, no tmpfs: %f +- %f s; max %f" %
        (
            numpy.array(data['noepoll_notmpfs']).mean(),
            numpy.array(data['noepoll_notmpfs']).std(),
            numpy.array(data['noepoll_notmpfs']).max()
        )
    )

    with open(epoll_notmpfs, 'r') as f:
        data['epoll_notmpfs'] = [float(x) for x in f.readlines()]

    print("EPoll, no tmpfs: %f +- %f s; max %f" %
        (
            numpy.array(data['epoll_notmpfs']).mean(),
            numpy.array(data['epoll_notmpfs']).std(),
            numpy.array(data['epoll_notmpfs']).max()
        )
    )

    with open(epoll_tmpfs, 'r') as f:
        data['epoll_tmpfs'] = [float(x) for x in f.readlines()]

    print("EPoll, tmpfs: %f +- %f s; max %f" %
        (
            numpy.array(data['epoll_tmpfs']).mean(),
            numpy.array(data['epoll_tmpfs']).std(),
            numpy.array(data['epoll_tmpfs']).max()
        )
    )

    return data


def generate_plot(data, figure_width, output_file):
    noepoll_notmpfs = numpy.array(data['noepoll_notmpfs'])
    noepoll_notmpfs_weights = numpy.ones(noepoll_notmpfs.shape) / len(noepoll_notmpfs)

    epoll_notmpfs = numpy.array(data['epoll_notmpfs'])
    epoll_notmpfs_weights = numpy.ones(epoll_notmpfs.shape) / len(epoll_notmpfs)

    epoll_tmpfs = numpy.array(data['epoll_tmpfs'])
    epoll_tmpfs_weights = numpy.ones(epoll_tmpfs.shape) / len(epoll_tmpfs)

    configure_pyplot(figure_width, figure_width,
        {
            'figure.subplot.top': 0.97,
            'figure.subplot.right': 0.95
        }
    )

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

    write_figure(output_file)

if __name__ == "__main__":
    config = Options()
    config.parseOptions()
    if config.subCommand == "aggregate":
        write_json(
            aggregate_logs(
                config.subOptions["noepoll_notmpfs"],
                config.subOptions["epoll_notmpfs"],
                config.subOptions["epoll_tmpfs"]
            ), config.subOptions['output_file']
        )
    elif config.subCommand == "plot":
        generate_plot(
            load_json(config.subOptions['input_file']),
            config.subOptions['figure-width'], config.subOptions['output_file']
        )
    else:
        print("Nothing to do; exiting")
