from collections import deque
from datetime import datetime
from math import isinf

def prioritize(tasks:list) -> list:
    sorted_tasks = sorted(tasks, reverse=True, key=lambda t: (
                t.level_id, t.space_priority + t.priority, -t.last_checked)
                        )
    return deque(sorted_tasks)

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

    
def check_task_conditions(task, now: datetime):
    if task.conditions == "daily":
        if (today := now.date()) > (then := datetime.fromtimestamp(task.last_finished).date()):
            task.done = False
        else:
            pass
    return 

def filter_tasks(tasks, pattern):
    if pattern.isspace() or not pattern:
        return tasks
    return list(filter(lambda t: pattern in t.do.casefold(), tasks))