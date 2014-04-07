import os
import numpy
import glob
import json

dataset = {
    "n_subscribers": [],
    "latency": [],
    "std": [],
    "min": [],
    "max": []
}

for n_subscribers in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
    directory = "%d_subscribers" % (n_subscribers)
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

with open('overall.json', 'w') as f:
    json.dump(dataset, f)
