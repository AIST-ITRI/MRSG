# -*- coding:utf-8 -*-

from collections import namedtuple

def _nf(v):
    v = v.strip()
    if len(v) == 0:
        return 0.0
    else:
        return float(v)

Event = namedtuple('Event', 'id, task_kind worker time event_kind shuffle_time')

def read_tasks_csv(filename):
    with open(filename) as f:
        # Skip first line. it is header line.
        if not f.readline(): 
            return
        while True:
            line = f.readline()
            if not line:
                break

            items = line.strip().split(',')
            yield Event(
                    items[0],
                    items[1],
                    int(items[2]),
                    float(items[3]),
                    items[4].strip() == 'START',
                    _nf(items[5]))
