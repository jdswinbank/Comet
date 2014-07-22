import os
import glob
import numpy
from matplotlib import pyplot
from twisted.python import usage
from utils import load_json
from utils import write_json
from utils import write_figure
from utils import configure_pyplot
from utils import PlotOptions
from utils import GOLDEN_MEAN

class AggregateOptions(usage.Options):
    def parseArgs(self, input_root, output):
        self['input_root'] = input_root
        self['output_file'] = output


class Options(usage.Options):
    subCommands = [['plot', None, PlotOptions, "Generate plot"],
                   ['aggregate', None, AggregateOptions, "Aggregate data"]]


def aggregate_logs(input_root):
    dataset = {
        "n_subscribers": [],
        "latency": [],
        "std": [],
        "min": [],
        "max": []
    }

    for n_subscribers in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
        directory = os.path.join(input_root, "%d_subscribers" % (n_subscribers))
        data = []
        for filename in glob.glob(os.path.join(directory, "*log")):
            with open(filename, "r") as f:
                data.extend(f.readlines())
        latencies = numpy.array([float(x) for x in data])
        dataset["n_subscribers"].append(n_subscribers)
        dataset["latency"].append(latencies.mean())
        dataset["std"].append(latencies.std())
        dataset["min"].append(latencies.min())
        dataset["max"].append(latencies.max())
    return dataset


def generate_plot(data, figure_width, output_file):
    figure_height = figure_width * GOLDEN_MEAN
    configure_pyplot(figure_width, figure_height,
        {
            'figure.subplot.bottom': 0.15,
            'figure.subplot.left': 0.15,
            'figure.subplot.top': 0.95,
            'figure.subplot.right': 0.97
        }
    )
    normalization = 1.0 / max(data["latency"])
    print [x /256.0  for x in data["n_subscribers"]]
    pyplot.errorbar(data["n_subscribers"], [x * normalization for x in data["latency"]], yerr=[x * normalization for x in data["std"]], fmt='b-')
    pyplot.plot(data["n_subscribers"], [x / 256.0 for x in data["n_subscribers"]], 'g--')

    pyplot.plot(data["n_subscribers"], [x * normalization for x in data["min"]], 'r:')
    pyplot.plot(data["n_subscribers"], [x * normalization for x in data["max"]], 'r:')
    pyplot.xscale("log")
    pyplot.yscale("log")
    pyplot.xlabel("Number of subscribers")
    pyplot.ylabel("Normalized latency")
    write_figure(output_file)

if __name__ == "__main__":
    config = Options()
    config.parseOptions()
    if config.subCommand == "aggregate":
        write_json(
            aggregate_logs(config.subOptions['input_root']),
            config.subOptions['output_file']
        )
    elif config.subCommand == "plot":
        generate_plot(
            load_json(config.subOptions['input_file']),
            config.subOptions['figure-width'], config.subOptions['output_file']
        )
    else:
        print("Nothing to do; exiting")
