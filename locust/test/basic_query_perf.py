#!/usr/bin/env python3

from locust import HttpUser, task
import __main__, argparse, json, locust.main, os, sys


class PuppetDbLoadTest(HttpUser):
    def response_printer(self, desc, response):
        if response.status_code == 0:
            log('Fatal response status_code: 0 (Is the server running?)')
            sys.exit(2)
        elif response.status_code != 200:
            print("Request: " + opts['name'] + " \n" +
                  "Method: " + opts['method'] + " \n" +
                  "Response status: " + str(response.status_code) + " \n" +
                  "Response body: " + response.text + " \n" +
                  "-------------------------------------------" + " \n")

    @task
    def swarm(self):
        method = __main__.opt.method
        for q in __main__.basic_queries:
            query = q['query']
            if method == 'get':
                if not isinstance(query, str):
                    query = json.dumps(query)
                url = q['path'] + "?query=" + query
                name = query
                with self.client.request(method, url, name) as response:
                    self.response_printer('%s %r' % (method, url), response)
            elif method == 'post':
                query = json.dumps({'query': query})
                url = ' '.join([q['path'], query])
                name = query
                with self.client.request(method, q['path'], name, data=query,
                                         headers={'content-type': 'application/json'}) as response:
                    self.response_printer('%s %r' % (method, url), response)
            else:
                raise Exception('Unrecognized method:' + method)
