import math
import json
from matplotlib import pyplot
from twisted.python import usage

GOLDEN_MEAN = (math.sqrt(5)-1.0)/2.0
INCHES_PER_PT = 1.0 / 72.27

class PlotOptions(usage.Options):
    optParameters = [
        ["figure-width", None, 252.0, "Width of figure in points", float]
    ]

    def parseArgs(self, input_file, output_file=None):
        self['input_file'] = input_file
        self['output_file'] = output_file


def configure_pyplot(figure_width, figure_height, extra_params={}):
    # The following is based on
    # <http://wiki.scipy.org/Cookbook/Matplotlib/LaTeX_Examples>.
    fig_size =  [figure_width*INCHES_PER_PT, figure_height*INCHES_PER_PT]
    params = {'backend': 'pdf', 'text.usetex': True, 'figure.figsize': fig_size}
    params.update(extra_params)
    pyplot.rcParams.update(params)
    pyplot.rc("font", size=8, family="sans", serif="Computer Sans")


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def write_figure(output_file):
    if output_file:
        pyplot.savefig(output_file)
    else:
        pyplot.show()
