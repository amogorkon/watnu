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
    return L

def balance(tasks:list, activity_time_spent) -> list:
    sorted_activity = sorted(activity_time_spent.items(), key=lambda i:i[1])
    neglected = sorted_activity[0]
    filtered_by_activity = filter(lambda t: t.activity_id == neglected[1], tasks)
    sorted_by_last_checked  = sorted(filtered_by_activity, key=lambda t: t.last_checked)
    return sorted_by_last_checked

def schedule(tasks:list) -> list:
    sorted_by_last_checked  = sorted(tasks, key=lambda t: t.last_checked)
    sorted_by_deadline  = sorted(sorted_by_last_checked, key=lambda t: float(t.deadline))
    return sorted_by_deadline