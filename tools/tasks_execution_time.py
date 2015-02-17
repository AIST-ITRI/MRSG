#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import argparse
import mrsg

def main():
    parser = argparse.ArgumentParser(description='print execution time of tasks.')
    parser.add_argument('file', metavar='FILE', help='task CSV file')

    args = parser.parse_args()

    tasks = {}
    for e in mrsg.read_tasks_csv(args.file):
        if e.event_kind: # START
            if e.id in tasks:
                sys.stderr.write('%s has already started.' % e.id)
                sys.exit(1)
            tasks[e.id] = e
        else: # END
            if e.id not in tasks:
                sys.stderr.write('%s has not started.' % e.id)
                sys.exit(1)
            se = tasks[e.id]
            print('%s\t%s\t%s\t%s' % (e.id, e.task_kind, e.worker, e.time - se.time))
    return 0

if __name__ == '__main__':
    sys.exit(main())

