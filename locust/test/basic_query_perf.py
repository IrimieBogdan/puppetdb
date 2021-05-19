#!/usr/bin/env python3

# This file is actually loaded twice, once as the __main__ module via
# the #! above, and again by locust, as ... via locust.  As a result,
# we can have custom command line options that set values in __main__
# that can then be accessed by the locust test module.  See the --help
# for more information.

from locust import HttpUser, task
import __main__, argparse, json, locust.main, os, sys

sys.path[:0] = [os.getcwd() + '/locust']

from pdb.util import log, read_query_data


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


# Anything that shouldn't be available in the test module, should be
# guarded by this test.

if __name__ == '__main__':

    defaults = ['--headless', '-H', 'http://localhost:8080',
                "-u", '1', "-r", '1', "-t", '1m']
                #"--csv", prefix, "--html", prefix + "_report.html"

    usage = 'basic_query_perf.py [-h] [--method {post,get}] -- LOCUST_ARG ...'
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('--method', choices=['post', 'get'], default='get',
                        help='make queries by GET or POST')

    locust_group = \
        parser.add_argument_group('locust arguments',
                                  'All arguments after a -- are passed directly to locust'
                                  ' (defaults: ' + ' '.join(defaults) + ')')
    locust_group.add_argument('locust_args', nargs=argparse.REMAINDER,
                              help=argparse.SUPPRESS)
    opt = parser.parse_args()
    if opt.locust_args and opt.locust_args[0] == '--':
        opt.locust_args = opt.locust_args[1:]

    with open('test-data/basic-queries.json', 'r') as f:
        basic_queries = read_query_data(f)

    sys.argv = [sys.argv[0]] + ['-f', __file__] + defaults + opt.locust_args
    sys.exit(locust.main.main())
