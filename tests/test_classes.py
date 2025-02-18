from src.classes import Task


def test_initialize_attributes():
    task = Task(id=1, do="Test Task", notes="Test Notes")
    assert task.id == 1
    assert task.do == "Test Task"
    assert task.notes == "Test Notes"
    assert task.priority == 0
    assert task.deadline == float("inf")
    assert task.repeats == 0
    assert task.constraints == 0
    assert task.subtasks == []
    assert task.supertasks == []
    assert task.skill_ids == []


def test_add_subtask(task):
    subtask = Task(id=2, do="Subtask", notes="Subtask Notes")
    task.add_subtask(subtask)
    assert task.subtasks == [subtask]


def test_add_supertask(task):
    supertask = Task(id=2, do="Supertask", notes="Supertask Notes")
    task.add_supertask(supertask)
    assert task.supertasks == [supertask]


def test_remove_subtask(task):
    subtask = Task(id=2, do="Subtask", notes="Subtask Notes")
    task.add_subtask(subtask)
    task.remove_subtask(subtask)
    assert task.subtasks == []


def test_remove_supertask(task):
    supertask = Task(id=2, do="Supertask", notes="Supertask Notes")
    task.add_supertask(supertask)
    task.remove_supertask(supertask)
    assert task.supertasks == []


def test_set_priority(task):
    task.set_priority(1)
    assert task.priority == 1


def test_set_deadline(task):
    task.set_deadline(1)
    assert task.deadline == 1


def test_set_repeats(task):
    task.set_repeats(1)
    assert task.repeats == 1


def test_set_constraints(task):
    task.set_constraints(1)
    assert task.constraints == 1


def test_task_repr_roundtrip(task: Task):
    assert eval(repr(task)) == task
