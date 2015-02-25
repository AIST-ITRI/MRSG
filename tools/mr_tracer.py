#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import argparse
import re
import os
import os.path
import Queue
import threading
from socket import gethostname
from job_history_server import JobHistoryServer
from collections import defaultdict

mapoutput_pattern = re.compile('.* org.apache.hadoop.mapreduce.task.reduce.Fetcher: fetcher#\d+ about to shuffle output of map (attempt_\w+) decomp: \d+ len: (\d+) to .*')
attempt_id_pattern = re.compile('attempt_(\d+_\d+_[mr]_\d+)_(\d+)')

def failure(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(1)

def eprint(msg):
    sys.stderr.write(msg + "\n")

def format_counters_to_dict(counters):
    d = {}
    for group in counters['taskAttemptCounterGroup']:
        d[group['counterGroupName']] = dict([(c['name'], c['value']) for c in group['counter']])
    return d

def attempt2task(attempt_id):
    m = attempt_id_pattern.match(attempt_id)
    if m is None:
        failure('unexpect attempt id: %s' % attempt_id)

    return 'task_' + m.group(1)


def get_attempts(queue, jobid, user, server, oq):
    map_cost = {}
    red_cost = {}
    map_input = {}
    map_output = defaultdict(dict)
    try:
        while  True:
            taskid = queue.get_nowait()

            attempts = server.task_attempts(jobid, taskid)

            finish_time = None
            for attempt in attempts:
                if attempt['state'] == 'SUCCEEDED' and (finish_time == None or finish_time > int(attempt['finishTime'])):
                    finish_time= int(attempt['finishTime'])
                    if attempt['type'] == 'MAP':
                        counters = format_counters_to_dict(
                            server.task_attempt_counter(jobid, taskid, attempt['id']))

                        hdfsNRead = counters['org.apache.hadoop.mapreduce.FileSystemCounter']['HDFS_BYTES_READ']
                        cpuTimeMs = counters['org.apache.hadoop.mapreduce.TaskCounter']['CPU_MILLISECONDS']

                        map_cost[taskid]  = cpuTimeMs
                        map_input[taskid] = int(hdfsNRead)

                    elif attempt['type'] == 'REDUCE':
                        node = attempt['nodeHttpAddress'].split(':')[0]
                        cid  = attempt['assignedContainerId']
                        log = server.logs(node, cid, attempt['id'], user)
                        for line in log.split('\n'):
                            m = mapoutput_pattern.match(line)
                            if m:
                                map_output[m.group(1)][taskid] = int(m.group(2))

                        counters = format_counters_to_dict(
                            server.task_attempt_counter(jobid, taskid, attempt['id']))

                        cpuTimeMs = counters['org.apache.hadoop.mapreduce.TaskCounter']['CPU_MILLISECONDS']

                        red_cost[taskid] = cpuTimeMs
    except Queue.Empty:
        oq.put((map_cost, red_cost, map_input, map_output))

def main():
    parser = argparse.ArgumentParser(description='Get execution time and input data size.')
    parser.add_argument('-f', '--force', dest='force', action='store_true', help='overwrite output')
    parser.add_argument('-s', '--hostname', default=gethostname(), help='MapReduce JobHistory Server hostname')
    parser.add_argument('-p', '--port', type=int, default=19888, help='MapReduce JobHistory Server port')

    parser.add_argument('--dfs-replicas', type=int, default=3, help='dfs_replicas of job configuraion')
    parser.add_argument('--map-slots', type=int, default=40, help='map_output of job configuraion')
    parser.add_argument('--reduce-slots', type=int, default=40, help='reduce_output of job configuraion')
    parser.add_argument('-t', '--threads', type=int, default=6, help='number of threads')

    parser.add_argument('jobid', metavar='JOB_ID', help='ID of target job')
    parser.add_argument('power', type=int, metavar='POWER', help='computing node power')

    args = parser.parse_args()

    outputdir = 'mr_trace_%s' % args.jobid

    if os.path.isdir(outputdir):
        if not args.force:
            failure('Output directory %s already exists.' % outputdir)
    else:
        os.mkdir(outputdir)

    server = JobHistoryServer(args.hostname, args.port)
    job = server.job(args.jobid)
    tasks = server.tasks(args.jobid)

    queue = Queue.Queue(-1)
    for task in tasks:
        queue.put(task['id'])

    oq = Queue.Queue(-1)

    ts = []
    for i in range(args.threads):
        if i == 0:
            s = server
        else:
            s = JobHistoryServer(args.hostname, args.port)
        ts.append(threading.Thread(target=get_attempts, args=(queue, job['id'], job['user'], s, oq)))

    for t in ts:
        t.start()

    map_cost = {}
    red_cost = {}
    map_input = {}
    map_output_tmp  = defaultdict(dict)

    for t in ts:
        t.join()

    try:
        while True:
            mc, rc, mi, mo = oq.get_nowait()

            map_cost.update(mc)
            red_cost.update(rc)
            map_input.update(mi)

            for mi, values in mo.items():
                map_output_tmp[mi].update(values)
    except Queue.Empty:
        pass

    map_output = defaultdict(lambda: defaultdict(int))
    for k,v in map_output_tmp.items():
        taskid = attempt2task(k)
        for rid, val in v.items():
            map_output[taskid][rid] += val

    # check map_output
    if len(red_cost) > 0:
        if set(map_cost.keys()) != set(map_output.keys()):
            failure('mismatch map list and reduce fetcher. %s != %s' % (len(map_cost.keys()), len(map_output.keys())) )

        for mid, values in map_output.items():
            if set(red_cost.keys()) != set(values.keys()):
                failure('mismatch map list and reduce fetcher. %s != %s' % (red_cost.keys(), values.keys()) )

    map_keys = sorted(map_cost.keys())
    red_keys = sorted(red_cost.keys())

    with open(outputdir + '/mapcost.txt', 'w') as f:
        for k in map_keys:
            f.write("%f\n" % (map_cost[k] * args.power / 1000.0))

    with open(outputdir + '/redcost.txt', 'w') as f:
        for k in red_keys:
            f.write("%f\n" %  (red_cost[k] * args.power / 1000.0))

    with open(outputdir + '/mapoutput.txt', 'w') as f:
        for mid in map_keys:
            sep = ''
            for rid in red_keys:
                f.write(sep)
                f.write('%d' % map_output[mid][rid])
                sep = ', '
            f.write("\n")

    with open(outputdir + '/job.conf', 'w') as f:
        chunk_size = 0
        if len(map_input) > 0:
            chunk_size = sum(map_input.values())/len(map_input)/(1024*1024) # MB.
        if chunk_size == 0:
            chunk_size = 1
        f.write("reduces    %d\n" % len(red_cost))
        f.write("chunk_size %d\n" % chunk_size)
        f.write("input_chunks %d\n" % len(map_input))
        f.write("dfs_replicas %d\n" % args.dfs_replicas)
        f.write("map_slots %d\n" % args.map_slots)
        f.write("reduce_slots %d\n" % args.reduce_slots)

    with open(outputdir + '/elapsedtime.txt', 'w') as f:
        elapseTimeMs = int(job['finishTime']) - int(job['startTime'])
        f.write(str(elapseTimeMs))

    return 0

if __name__ == '__main__':
    sys.exit(main())
