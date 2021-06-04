#!/usr/bin/env python3

# This file is actually loaded twice, once as the __main__ module via
# the #! above, and again by locust, as ... via locust.  As a result,
# we can have custom command line options that set values in __main__
# that can then be accessed by the locust test module.  See the --help
# for more information.

from locust import HttpUser, task
import __main__, argparse, json, locust.main, os, sys, yaml

sys.path[:0] = [os.getcwd() + '/locust']

from pdb.util import log, read_query_data


class PuppetDbLoadTest(HttpUser):
    def response_printer(self, opts, response):
        if response.status_code == 0:
            print(response.error)
            exit(1)
        elif response.status_code != 200:
            print(
                "Request: " + opts['name'] + " \n" +
                "Method: " + opts['method'] + " \n" +
                "Response status: " + str(response.status_code) + " \n" +
                "Response body: " + response.text + " \n" +
                "-------------------------------------------" + " \n")

    @task
    def swarm(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/config.yaml') as stream:
            config = yaml.safe_load(stream)
            for opts in config:
                if (opts['method'] == 'GET'):
                    url = opts['path'] + "?" + opts['query']
                    with self.client.request(opts['method'], url, opts['name']) as response:
                        self.response_printer(opts, response)
                elif (opts['method'] == 'POST'):
                    json_obj = json.dumps(opts['query'])
                    with self.client.request(opts['method'], opts['path'], opts['name'], data=json_obj, headers=opts['headers']) as response:
                        self.response_printer(opts, response)


# Anything that shouldn't be available in the test module, should be
# guarded by this test.

def merge_args(defaults, program_args):
    additional_args = []
    for default_arg in defaults:
        found = False
        for arg in program_args:
            if arg == default_arg[0]:
                found = True
        if found == False:
            additional_args += default_arg

    return additional_args


if __name__ == '__main__':
    default = [['--headless'], ['-H', 'http://localhost:8080'],
               ["-u", '1'], ["-r", '1'], ["-t", '1m']]
                #"--csv", prefix, "--html", prefix + "_report.html"

    missing_defaults = []

    missing_defaults = merge_args(default, sys.argv)
    sys.argv = sys.argv + ['-f', __file__] + missing_defaults

    sys.exit(locust.main.main())
