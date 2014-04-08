import os
import glob
import numpy
import anydbm
from matplotlib import pyplot
from matplotlib import gridspec
from twisted.python import usage
from utils import load_json
from utils import write_json
from utils import write_figure
from utils import configure_pyplot
from utils import PlotOptions

class AggregateOptions(usage.Options):
    optParameters = [
        ['num_sent', None, 10000, "Number of events sent", int]
    ]

    def parseArgs(self, input_root, output):
        self['input_root'] = input_root
        self['output_file'] = output


class Options(usage.Options):
    subCommands = [['plot', None, PlotOptions, "Generate plot"],
                   ['aggregate', None, AggregateOptions, "Aggregate data"]]


def read_author_time(filename):
    with open(filename, 'r') as f:
        f.seek(0, os.SEEK_END)
        f.seek(f.tell() - 1000, os.SEEK_SET)
        line = f.readlines()[-2]
    return float(line.split("time: ")[1][:-2])

def read_database_time(filename):
    db = anydbm.open(filename)
    timestamps = sorted(float(val) for val in db.values())
    return timestamps[-1] - timestamps[0]

def count_missing(filename, num_sent):
    db = anydbm.open(filename)
    return num_sent - len(db.keys())

def calculate_rates(input_root, num_sent):
    rate = {}
    for latency in [0,100,200,300,400,500]:
        rate[latency] = {}
        for num_connections in [1,2,4,8,16,32,64,128,256,512]:
            missing = 0

            author_times = numpy.array(
                [
                    read_author_time(filename) for filename in
                    glob.glob(
                        os.path.join(input_root,
                            "%dms/%dc/run*/author.log" % (latency, num_connections)
                        )
                    )
                ]
            )
            author_rate = num_sent / author_times

            broker_times = numpy.array(
                [
                    read_database_time(filename) for filename in
                    glob.glob(
                        os.path.join(input_root,
                            "%dms/%dc/run*/broker.db" % (latency, num_connections)
                        )
                    )
                ]
            )
            broker_rate = num_sent / broker_times

            subscriber_times = numpy.array(
                [
                    read_database_time(filename) for filename in
                    glob.glob(
                        os.path.join(input_root,
                            "%dms/%dc/run*/subscriber.db" % (latency, num_connections)
                        )
                    )
                ]
            )
            subscriber_rate = num_sent / subscriber_times

            for filename in glob.glob(
                os.path.join(input_root,
                    "%dms/%dc/run*/subscriber.db" % (latency, num_connections)
                )
            ):
                missing += count_missing(filename, num_sent)

            rate[latency][num_connections] = {
                "author": {
                    "min": author_rate.min(),
                    "max": author_rate.max(),
                    "mean": author_rate.mean(),
                    "std": author_rate.std()
                },
                "broker": {
                    "min": broker_rate.min(),
                    "max": broker_rate.max(),
                    "mean": broker_rate.mean(),
                    "std": broker_rate.std()
                },
                "subscriber": {
                    "min": subscriber_rate.min(),
                    "max": subscriber_rate.max(),
                    "mean": subscriber_rate.mean(),
                    "std": subscriber_rate.std()
                },
                "missing": missing
            }
    return rate


def generate_plot(rate, figure_width, output_file):
    configure_pyplot(figure_width, figure_width,
        {
            'figure.subplot.top': 0.97,
            'figure.subplot.right': 0.95
        }
    )
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

    for connections, data in rate['0'].items():
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

    write_figure(output_file)


if __name__ == "__main__":
    config = Options()
    config.parseOptions()
    if config.subCommand == "aggregate":
        write_json(
            calculate_rates(
                config.subOptions['input_root'], config.subOptions['num_sent']
            ),
            config.subOptions['output_file']
        )
    elif config.subCommand == "plot":
        generate_plot(
            load_json(config.subOptions['input_file']),
            config.subOptions['figure-width'], config.subOptions['output_file']
        )
    else:
        print("Nothing to do; exiting")
