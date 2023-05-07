tasks = {}


class Task:
    def __init__(self, ID):
        self.ID = ID
        self.subtasks = []

    def __repr__(self) -> str:
        return f"Task({self.ID}, subtasks={self.subtasks})"


tasks = {ID: Task(ID) for ID in range(10)}
tasks[1].subtasks.append(tasks[2])
tasks[2].subtasks.append(tasks[3])
tasks[3].subtasks.append(tasks[1])


def cycle_in_task_dependencies2(tasks: dict[int, Task]) -> list[Task]:
    """Return a list of tasks that are involved in a cycle in their dependencies."""
    visited = set()
    path = []

    def visit(task: Task) -> bool:
        if task in visited:
            return False
        visited.add(task)
        path.append(task)
        for subtask in task.subtasks:
            if subtask in path or visit(subtask):
                return True
        path.pop()
        return False

    return [task for task in tasks.values() if visit(task)]


breakpoint()
print(tasks)
print(cycle_in_task_dependencies2(tasks))
