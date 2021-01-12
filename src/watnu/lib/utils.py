from functools import wraps
from types import MethodType

list_len = []

def aspectized(obj, decorator):
    for name in dir(obj):
        if not name.startswith("__") and callable(func := getattr(obj, name)):
            print("decorated:", name)
            setattr(obj, name, MethodType(decorator(func), obj))
    return obj

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