import os
import anydbm
import glob
import numpy
import json

NUM_SENT = 10000

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

def count_missing(filename):
    db = anydbm.open(filename)
    return NUM_SENT - len(db.keys())

def calculate_rates():
    rate = {}
    for latency in [0,100,200,300,400,500]:
        rate[latency] = {}
        for num_connections in [1,2,4,8,16,32,64,128,256,512]:
            missing = 0

            author_times = numpy.array(
                [
                    read_author_time(filename) for filename in
                    glob.glob("%dms/%dc/run*/author.log" % (latency, num_connections))
                ]
            )
            author_rate = NUM_SENT / author_times

            broker_times = numpy.array(
                [
                    read_database_time(filename) for filename in
                    glob.glob("%dms/%dc/run*/broker.db" % (latency, num_connections))
                ]
            )
            broker_rate = NUM_SENT / broker_times

            subscriber_times = numpy.array(
                [
                    read_database_time(filename) for filename in
                    glob.glob("%dms/%dc/run*/subscriber.db" % (latency, num_connections))
                ]
            )
            subscriber_rate = NUM_SENT / subscriber_times

            for filename in glob.glob("%dms/%dc/run*/subscriber.db" %
                                      (latency, num_connections)):
                missing += count_missing(filename)

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

if __name__ == "__main__":
    with open('rate.json', 'w') as f:
        json.dump(calculate_rates(), f, indent=4)
