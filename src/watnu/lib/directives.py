import contextlib
import logging
from ast import literal_eval

from stay import T

logger = logging.getLogger()


def include(result, *args, lines, n, decoder, state, cases):
    with open(args[0]) as f:
        lines[n + 1 : n + 1] = f.readlines()


def inline_comments(*args):
    def do(line):
        stuff, _, comment = line.partition("#")
        return stuff

    return do


def list_to_set(*args):
    def do(token, struct):
        if token is T.list:
            return set(struct)

    return do


def context(*args, s: list):
    from urllib.parse import urlparse

    d = {}
    for l in s:

        def expand(v):
            head, _, tail = v.partition(":")
            if _:
                url = urlparse(v)
                if not url.scheme or not url.netloc:
                    with contextlib.suppress(Exception):
                        v = d[head] + tail
            return v

        k, p, v = (p.strip() for p in l.partition(":"))
        v = expand(v)
        if p:
            d[k] = v

    def do(stuff: str):
        try:
            return d[stuff]
        except Exception:
            return stuff

    return do


def inline_spec(*args):
    case = {
        "int": int,
        "float": float,
        "bool": bool,
    }

    def do(stuff):
        head, _, tail = map(str.strip, stuff.partition("§"))
        if _:
            try:
                return case[tail](head)
            except Exception as e:
                logger.error(e)
        return head

    return do
