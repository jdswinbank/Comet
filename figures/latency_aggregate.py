import json

data = {}

with open('1sub-noepoll-notmpfs.log', 'r') as f:
    data['noepoll_notmpfs'] = [float(x) for x in f.readlines()]

with open('1sub-epoll-notmpfs.log', 'r') as f:
    data['epoll_notmpfs'] = [float(x) for x in f.readlines()]

with open('1sub-epoll-tmpfs.log', 'r') as f:
    data['epoll_tmpfs'] = [float(x) for x in f.readlines()]

with open('latency.json', 'w') as f:
    json.dump(data, f)
