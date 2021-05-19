
import json, sys

def read_query_data(f):
    return [x for x in json.load(f) if not isinstance(x, str)]

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
