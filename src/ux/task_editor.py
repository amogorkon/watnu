from collections import namedtuple

import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QVariant
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtSql import QSqlTableModel

_translate = QCoreApplication.translate

import q
import ui
from classes import ILK, Task, iter_over, submit_sql

from .stuff import app, config, db


class Editor(QtWidgets.QWizard, ui.task_editor.Ui_Wizard):
    """Editor for new or existing tasks."""

    def __init__(
        self,
        task: Task = None,
        cloning: bool = False,
        templating: bool = False,
        as_sup: bool = 0,
        current_space: str = None,
        draft: bool = False,
    ):
        super().__init__()
        self.activateWindow()
        self.setupUi(self)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.accept)

        if cloning:
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))

        if templating:
            self.setWindowTitle(_translate("Wizard", "Bearbeite verknüpfte Aufgabe"))

        self.setOption(QtWidgets.QWizard.WizardOption.HaveFinishButtonOnEarlyPages, True)
        self.task: Task = task
        self.cloning = cloning
        self.templating = templating
        self.subtasks: list[int] = []
        self.supertasks: list[int] = []
        self.skill_ids: list[int] = []

        # clone as subtask of the given task
        if as_sup == -1:
            self.supertasks = [self.task.id]

        # given task is a subtask of the new task
        if as_sup == 1:
            self.subtasks = [self.task.id]

        self.page_basics.registerField("task*", self.desc, "plainText", changedSignal=self.desc.textChanged)
        model = QSqlTableModel()
        model.setTable("levels")
        model.setSort(0, Qt.SortOrder.DescendingOrder)
        model.select()
        self.level.setModel(model)
        self.level.setModelColumn(1)
        self.level.setCurrentIndex(2)

        model = QSqlTableModel()
        model.setTable("spaces")
        model.setSort(1, Qt.SortOrder.AscendingOrder)
        model.select()
        self.space.setModel(model)
        self.space.setModelColumn(1)
        self.constraints: str = None
        self.deadline = float("inf")
        self.repeats: namedtuple = None

        query = submit_sql(
            """
        SELECT activity_id, name FROM activities;
        """
        )

        for i, row in enumerate(iter_over(query)):
            self.activity.addItem(row(1), QVariant(row(0)))
            self.secondary_activity.addItem(row(1), QVariant(row(0)))

        # editing a task - need to set all values accordingly
        if task:
            self.deadline = task.deadline
            self.skill_ids = self.task.skill_ids
            self.priority.setValue(task.priority)

            for url, ID in task.resources:
                self.resources.addItem(url, ID)

            self.desc.document().setPlainText(task.do)

            if task.ilk is ILK.habit:
                self.is_habit.setChecked(True)
            if task.ilk is ILK.tradition:
                self.is_tradition.setChecked(True)
            if task.ilk is ILK.routine:
                self.is_routine.setChecked(True)

            if task.ilk in (ILK.tradition, ILK.routine):
                self.button8.setEnabled(True)
            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findText(self.task.space))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.activity.setCurrentIndex(self.activity.findText(self.task.activity))
            self.secondary_activity.setCurrentIndex(
                self.secondary_activity.findText(self.task.secondary_activity)
            )
            self.repeats = self.task.repeats
            self.constraints = x if (x := self.task.constraints) is not None else np.zeros((7, 144))
        # new task - preset space by previous edit
        else:
            self.space.setCurrentIndex(self.space.findText(current_space or app.last_edited_space))

        @self.kind_of.buttonToggled.connect
        def kind_of_toggled():
            if self.is_task.isChecked() or self.is_habit.isChecked():
                self.button8.setEnabled(False)
            else:
                self.button8.setEnabled(True)

        @self.resource_add.clicked.connect
        def resource_added():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Resource hinzufügen",
                "Welche URL?",
                QtWidgets.QLineEdit.EchoMode.Normal,
                "",
            )

            if okPressed and text != "":
                submit_sql(
                    f"""
INSERT OR IGNORE INTO resources
(url)
VALUES ('{text}')
"""
                )
                query = submit_sql(
                    f"""
SELECT resource_id
FROM resources
WHERE url = '{text}'
"""
                )
                query.next()
                resource_id = query.value(0)
                self.resources.addItem(text, resource_id)

        @self.resource_remove.clicked.connect
        def _():
            self.resources.removeItem(self.resources.currentIndex())

        @self.button1.clicked.connect
        def subtasks_button():
            q("button1 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="subtasks")
            dialog.exec()

        @self.button2.clicked.connect
        def time_constraints_button():
            q("button2 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="constraints")
            dialog.exec()

        @self.button3.clicked.connect
        def _():
            q("button3 clicked", self.task)

        @self.button4.clicked.connect
        def _():
            q("button4 clicked", self.task)

        @self.button5.clicked.connect
        def _():
            q("button5 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="deadline")
            dialog.exec()

        @self.button6.clicked.connect
        def _():
            q("button6 clicked", self.task)

        @self.button7.clicked.connect
        def supertasks_button():
            q("button7 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="supertasks")
            dialog.exec()

        @self.button8.clicked.connect
        def _():
            q("button8 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="repeats")
            dialog.exec()

        @self.button9.clicked.connect
        def skills_button():
            q("button9 clicked", self.task)
            dialog = ux.chooser.Chooser(self, self.task, kind="skills")
            dialog.exec()

        @self.space.currentIndexChanged.connect
        def _():
            space_id = self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))
            if space_id is not None:
                for row in iter_over(
                    submit_sql(
                        f"""
SELECT primary_activity_id, secondary_activity_id
FROM spaces
WHERE space_id = {space_id}
                """
                    )
                ):
                    if row(0):
                        self.activity.setCurrentIndex(self.activity.findData(QVariant(row(0))))
                    else:
                        self.activity.setCurrentIndex(0)
                    if row(1):
                        self.secondary_activity.setCurrentIndex(
                            self.secondary_activity.findData(QVariant(row(1)))
                        )
                    else:
                        self.secondary_activity.setCurrentIndex(0)

    def accept(self):
        # TODO check sanity for traditions and routines
        super().accept()
        global last_edited_space

        do = self.desc.toPlainText()
        priority: float = self.priority.value()
        space_id: int = self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))

        last_edited_space = self.space.currentText()
        primary_activity_id = x if (x := self.activity.currentData()) is not None else "NULL"
        secondary_activity_id = x if (x := self.secondary_activity.currentData()) is not None else "NULL"
        level_id: int = self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))

        task_type = ILK.task
        if self.is_habit.isChecked():
            task_type = ILK.habit
        if self.is_routine.isChecked():
            task_type = ILK.routine
        if self.is_tradition.isChecked():
            task_type = ILK.tradition

        task_id: int

        # it really is a new task
        if not self.task or self.cloning or self.templating:
            query = submit_sql(
                f"""
INSERT INTO tasks 
(do, 
space_id, 
primary_activity_id,
secondary_activity_id,
ilk,
level_id
)

VALUES 
('{do}', 
{x if (x := space_id) is not None else 0},
{primary_activity_id},
{secondary_activity_id},
{task_type.value},
{level_id}
);
"""
            )

            task_id = query.lastInsertId()

        else:
            task_id = self.task.id
            submit_sql(
                f"""
UPDATE tasks 
SET do = '{do}',
    priority = {priority},
    level_id = {level_id},
    primary_activity_id = {primary_activity_id},
    secondary_activity_id = {secondary_activity_id},
    space_id = {space_id},
    ilk = {task_type.value}
WHERE id={task_id}
""",
                debugging=True,
            )
            # need to clean up first
            submit_sql(
                f"""
DELETE FROM task_requires_task WHERE task_of_concern == {task_id}
    """
            )
            submit_sql(
                f"""
DELETE FROM task_requires_task WHERE required_task == {task_id}
"""
            )
            submit_sql(
                f"""
DELETE FROM task_uses_resource WHERE task_id = {task_id}
    """
            )
            submit_sql(
                f"""
DELETE FROM task_trains_skill WHERE task_id = {task_id}
    """
            )
            submit_sql(
                f"""
DELETE FROM constraints WHERE task_id = {task_id}
            """
            )
            submit_sql(
                f"""
DELETE FROM deadlines WHERE task_id = {task_id}
            """
            )
            submit_sql(
                f"""
DELETE FROM repeats WHERE task_id = {task_id}
            """
            )

        # enter fresh, no matter whether new or old

        for required_task in self.subtasks:
            submit_sql(
                f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES ({task_id}, {required_task})
;
"""
            )
        for task_of_concern in self.supertasks:
            submit_sql(
                f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES ({task_of_concern}, {task_id})
;
"""
            )
        for skill_id in self.skill_ids:
            submit_sql(
                f"""
INSERT INTO task_trains_skill
(task_id, skill_id)
VALUES (
{task_id}, {skill_id}
    );
"""
            )
        for i in range(self.resources.count()):
            submit_sql(
                f"""
INSERT INTO task_uses_resource
(task_id, resource_id)
VALUES ({task_id}, {self.resources.itemData(i)});
"""
            )
        if np.any(self.constraints):
            submit_sql(
                f"""
    INSERT INTO constraints
    (task_id, flags)
    VALUES ({task_id}, '{''.join(str(x) for x in self.constraints.flatten())}')
            """
            )
        if self.deadline != float("inf"):
            submit_sql(
                f"""
INSERT INTO deadlines
(task_id, time_of_reference)
VALUES ({task_id}, '{self.deadline}')
            """
            )

        if self.repeats is not None:
            submit_sql(
                f"""
INSERT INTO repeats
(task_id, every_ilk, x_every, min_distance, x_per)
VALUES (
{task_id}, 
{self.repeats.every_ilk.value},
{self.repeats.x_every},
{self.repeats.x_per},
{self.repeats.per_ilk.value}
)
            """,
                debugging=True,
            )

        for win in app.list_of_task_lists:
            win.build_task_list()

    def reject(self):
        super().reject()


import ux
