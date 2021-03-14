from functools import partial

def set_as_done(set_flag=True):
    print(set_flag)
    
p = partial(set_as_done, False)
p()