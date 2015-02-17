#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import argparse
from collections import defaultdict
import mrsg
import matplotlib
matplotlib.use('Agg') # no gui, must be before 'import matplotlib.pyplot'
import matplotlib.pyplot as plt

class Counter(object):
    def __init__(self):
        self.current = 0
        self.history = [(0.0, 0)] # (time, number_of_tasks)

    def append_event(self, event):
        self.history.append((event.time, self.current))
        if event.event_kind: # START
            self.current += 1
        else: # END
            self.current -= 1
        self.history.append((event.time, self.current))

def main():
    parser = argparse.ArgumentParser(description='Plot number of tasks.')
    parser.add_argument('tasks_csv', metavar='FILE', help='task csv file')
    parser.add_argument('image', metavar='FILE', help='output image file')

    args = parser.parse_args()

    counters = defaultdict(Counter)

    for e in mrsg.read_tasks_csv(args.tasks_csv):
        counters[e.task_kind].append_event(e)

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(111)

    max_value_y = 0
    for kind, counter in counters.items():
        x, y = zip(*counter.history)
        max_value_y = max([max_value_y, max(y)])
        ax.plot(x, y, label=kind)
    ax.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
    ax.set_ylim(0, max_value_y * 1.1)
    fig.savefig(args.image, format='PNG', bbox_inches='tight')

    return 0

if __name__ == '__main__':
    sys.exit(main())
