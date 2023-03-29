
from functools import wraps
from time import time, sleep
def cached_getter(func):
    last_called = 0
    last_results = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        nonlocal last_called, last_results
        if self not in last_results:
            res = func(*args, **kwargs)
            last_results[self] = res
        else:
            res = last_results[self]

        last_called = time()
        return res

    return wrapper

class Test:
    __slots__ = "id", 
    @property
    def foo(self):
        sleep(2)
        return 23
    
    def set_(self, name, value):
        object.__setattr__(self, name, value)
    
    def __setattr__(self, name, value):
        raise UserWarning("Can't directly assign attributes. Please use Task.set_()")

t = Test()