# -*- coding: utf-8 -*-

import httplib
import json
from lxml import html
from lxml.html import soupparser
from lxml import etree

log_port = 8041

class JobHistoryServer(object):
    def __init__(self, host, port):
        self.connection = httplib.HTTPConnection(host, port)

    def _request(self, method, url, params = {}, body = '', headers = {}):
        if len(params) > 0:
            url += '?' + '&'.join(['%s=%s' % kv for kv in params.items()])
        self.connection.request(method, url, body, headers)
        response = self.connection.getresponse()
        return json.loads(response.read())

    def jobs(self,
             user = None,
             state = None,
             queue = None,
             limit = None,
             startedTimeBegin = None,
             startedTimeEnd = None, 
             finishedTimeBegin = None,
             finishedTimeEnd = None):

        params = {}
        if user is not None:
            params['user'] = user
        if state is not None:
            params['state'] = state
        if limit is not None:
            params['limit'] = limit
        if startedTimeBegin is not None:
            params['startedTimeBegin'] = time_to_ms(startedTimeBegin)
        if startedTimeEnd is not None:
            params['startedTimeEnd'] = time_to_ms(startedTimeEnd)
        if finishedTimeBegin is not None:
            params['finishedTimeBegin'] = time_to_ms(finishedTimeBegin)
        if finishedTimeEnd is not None:
            params['finishedTimeEnd'] = time_to_ms(finishedTimeEnd)

        return self._request('GET', '/ws/v1/history/mapreduce/jobs', params)

    def job(self, jobid):
        return self._request('GET', '/ws/v1/history/mapreduce/jobs/%s' % jobid)['job']

    def tasks(self, jobid, type=None):
        params = {}
        if type is not None:
            params['type'] = type

        return self._request('GET', '/ws/v1/history/mapreduce/jobs/%s/tasks' % jobid, params)['tasks']['task']

    def task_attempts(self, jobid, taskid):
        url = '/ws/v1/history/mapreduce/jobs/%s/tasks/%s/attempts' % (jobid, taskid)
        attempts = self._request('GET', url)['taskAttempts']['taskAttempt']
        return attempts

    def task_attempt(self, jobid, taskid, attemptid):
        url = '/ws/v1/history/mapreduce/jobs/%s/tasks/%s/attempts/%s' % (jobid, taskid, attemptid)
        return self._request('GET', url)['taskAttempt']

    def task_attempt_counter(self, jobid, taskid, attemptid):
        url = '/ws/v1/history/mapreduce/jobs/%s/tasks/%s/attempts/%s/counters' % (jobid, taskid, attemptid)
        return self._request('GET', url)['jobTaskAttemptCounters']

    def logs(self, node, containerId, taskAttemptID, user, kind = 'syslog'):
        url = '/jobhistory/logs/%s:%d/%s/%s/%s/%s?start=0' % (node, log_port, containerId, taskAttemptID, user, kind)
        self.connection.request('GET', url, '', {})
        response = self.connection.getresponse()

        # NOTE:
        # lxml.html.fromstring() cannnot parse very very long log html file.
        # Thus, I use lxml.html.soupparser.fromstring().

        c = soupparser.fromstring(response.read())

        t = c.find("table")
        tb = t.find("tbody")
        tr = tb.find("tr")
        td = tr.findall("td")

        return td[1].text_content()
