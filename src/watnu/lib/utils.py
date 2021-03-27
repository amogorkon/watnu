from enum import Flag
from functools import wraps
from time import monotonic, perf_counter
from types import MethodType

import q

list_len = []

def check_list(func):
    def decorator(self, *args, **kwargs):
        global list_len
        try:
            print(len(list_len))
            list_len.append(len(self.tasks, func.__name__))
            return func(self, *args, **kwargs)
        except TypeError:
            return func(*args, **kwargs)
    return decorator


def write_test():
    global list_len
    print(len(list_len))
    with open("test", "w+") as f:
        for x in list_len:
            f.write(x)
            f.write("\n")

ASPECT = Flag("Aspect", "property_set property_get")

def aspectized(decorator, aspect=ASPECT.property_get, pattern=None):
    def wrapping (cls):
        if ASPECT.property_get in aspect:
            for name, attr in cls.__dict__.items():
                if not name.startswith("__") and type(attr) is property:
                    setattr(cls, name, property(decorator(attr), attr.fset))
        return cls
    return wrapping

def logged(func):
    def wrapper(*args, **kwargs):
        if type(func) is property:
            q(args[0], "=>",  func.fget.__name__)
            res = func.fget(*args, **kwargs)
            q(args[0], func.fget.__name__, "=>", res)
            return res
        return func(*args, **kwargs)
    return wrapper

def timed(func):
    def wrapper(*args, **kwargs):
        before = perf_counter()
        res = func(*args, **kwargs)
        after = perf_counter()
        print(func.__name__, after - before, "seconds")
        q(after-before, func, args, kwargs)
        return res
    return wrapper
    