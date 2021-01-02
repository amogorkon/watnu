from collections import deque
from datetime import datetime
from math import isinf

def prioritize(tasks:list) -> list:
    sorted_by_last_checked  = sorted(tasks, key=lambda t: t.last_checked)
    sorted_by_level = sorted(sorted_by_last_checked, reverse=True, key=lambda t: t.level_id)
    sorted_by_priority = sorted(sorted_by_level, reverse=True, key=lambda t: t.total_priority)
    L = []
    considered_level = sorted_by_level[0].level_id
    considered_priority = sorted_by_priority[0].total_priority
    for t in sorted_by_priority:
        if t.level_id < considered_level:
            break
        if t.priority < considered_priority:
            break
        L.append(t)
    return deque(L)

def balance(tasks:list, activity_time_spent: dict) -> list:
    sorted_tasks = sorted(tasks, 
                key=lambda t: (-activity_time_spent[t.activity_id], 
                               -t.last_checked))
    return deque(sorted_tasks)

def schedule(tasks:list) -> list:
    filtered_by_infinity = filter(lambda t: not isinf(float(t.deadline)), tasks)
    sorted_by_last_checked  = sorted(filtered_by_infinity, key=lambda t: t.last_checked)
    sorted_by_deadline  = sorted(sorted_by_last_checked, key=lambda t: float(t.deadline))
    return deque(sorted_by_deadline)

    
def check_task_conditions(*, cond:str, done:bool, active:bool, last_finished:int, now: datetime):
    if cond == "daily":
        if (today := now.date()) > (then := datetime.fromtimestamp(last_finished).date()):
            done = False
            print(today, then, "daily not done, resetting")
        else:
            pass
    return done, active