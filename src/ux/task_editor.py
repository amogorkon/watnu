from collections import namedtuple
from functools import partial

import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QVariant
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtWidgets import QWizard

import ui
from classes import ILK, Task, get_activity_name
from logic import retrieve_task_by_id
from stuff import app, db

_translate = QCoreApplication.translate


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
        self.setupUi(self)

        self.gui_timer = QTimer()
        self.gui_timer.start(100)

        @self.gui_timer.timeout.connect
        def gui_timer_timeout():
            if app.win_running:
                self.button5.setEnabled(False)
            else:
                self.button5.setEnabled(True)

        self.task = task
        self.cloning = cloning
        self.templating = templating
        self.as_sup = as_sup
        self.current_space = current_space
        self.draft = draft

        if not task:
            query = db.execute("""INSERT INTO tasks (do, draft) VALUES ("",True);""")
            db.commit()
            self.task = retrieve_task_by_id(db, query.lastrowid)
            self.draft = True
        else:
            self.task = task

        self.setButtonText(QWizard.WizardButton.CustomButton1, "als Entwurf speichern")

        @self.button(QWizard.WizardButton.CustomButton1).clicked.connect
        def _():
            self.draft = True
            self.save_task()
            self.done(12)

        self.setButtonText(QWizard.WizardButton.FinishButton, "Fertig")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Abbrechen")

        self.activateWindow()

        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.accept)

        if cloning:
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))

        if templating:
            self.setWindowTitle(_translate("Wizard", "Bearbeite verknüpfte Aufgabe"))

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

        menu = QtWidgets.QMenu()
        menu.addAction("ohne Vorlage", self.create_task)
        menu.addAction("als Klon von dieser Aufgabe", self.clone)
        self.button6.setMenu(menu)

        query = db.execute(
            """
        SELECT activity_id, name FROM activities;
        """
        )

        for i, (activity_id, name) in enumerate(query.fetchall()):
            self.primary_activity.addItem(name, QVariant(activity_id))
            self.secondary_activity.addItem(name, activity_id)

        # editing a task - need to set all values accordingly
        if task:
            self.deadline = task.deadline
            self.skill_ids = self.task.skills
            self.priority.setValue(task.priority)
            for url, ID in task.resources:
                self.resources.addItem(url, ID)

            self.desc.document().setPlainText(task.do)

            match task.ilk:
                case ILK.habit:
                    self.is_habit.setChecked(True)
                case ILK.tradition:
                    self.is_tradition.setChecked(True)
                    self.button8.setEnabled(True)
                case ILK.routine:
                    self.is_routine.setChecked(True)
                    self.button8.setEnabled(True)

            print(repr(task))
            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findText(self.task.space))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.primary_activity.setCurrentIndex(
                self.primary_activity.findText(get_activity_name(self.task.primary_activity_id))
            )

            self.secondary_activity.setCurrentIndex(
                self.primary_activity.findText(get_activity_name(self.task.primary_activity_id))
            )
            self.repeats = self.task.get_repeats()
            self.constraints = x if (x := self.task.get_constraints()) is not None else np.zeros((7, 144))
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
                db.execute(
                    f"""
INSERT OR IGNORE INTO resources
(url)
VALUES ('{text}')
"""
                )
                db.commit()
                query = db.execute(
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
        def set_status():
            pass

        @self.button2.clicked.connect
        def time_constraints_button():
            chooser.Chooser(self, self.task, kind="constraints").exec()

        @self.button3.clicked.connect
        def organise():
            pass

        @self.button4.clicked.connect
        def _():
            pass

        @self.button5.clicked.connect
        def start_button():
            self.save_task()
            self.done(12)
            task_running.Running(self.task)

        @self.button6.clicked.connect
        def _():
            pass

        @self.button7.clicked.connect
        def deadline():
            chooser.Chooser(self, self.task, kind="deadline").exec()

        @self.button8.clicked.connect
        def repeats_button():
            chooser.Chooser(self, self.task, kind="repeats").exec()

        @self.button9.clicked.connect
        def skills_button():
            chooser.Chooser(self, self.task, kind="skills").exec()

        @self.space.currentIndexChanged.connect
        def _():
            space_id = self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))
            if space_id is not None:
                for primary_activity_id, secondary_activity_id in db.execute(
                    f"""
SELECT primary_activity_id, secondary_activity_id
FROM spaces
WHERE space_id = {space_id}
                """
                ).fetchall():
                    if primary_activity_id is not None:
                        self.primary_activity.setCurrentIndex(
                            self.primary_activity.findData(QVariant(primary_activity_id))
                        )
                    else:
                        self.primary_activity.setCurrentIndex(0)
                    if secondary_activity_id is not None:
                        self.secondary_activity.setCurrentIndex(
                            self.secondary_activity.findData(QVariant(secondary_activity_id))
                        )
                    else:
                        self.secondary_activity.setCurrentIndex(0)

    def save_task(self):
        app.last_edited_space = self.space.currentText()

        task_type = ILK.task
        if self.is_habit.isChecked():
            task_type = ILK.habit
        if self.is_routine.isChecked():
            task_type = ILK.routine
        if self.is_tradition.isChecked():
            task_type = ILK.tradition

        db.executescript(
            f"""
BEGIN;
UPDATE tasks 
SET do = '{self.desc.toPlainText()}',
    priority = {self.priority.value()},
    level_id = {self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))},
    primary_activity_id = {x if (x := self.primary_activity.currentData()) is not None else "NULL"},
    secondary_activity_id = {x if (x := self.secondary_activity.currentData()) is not None else "NULL"},
    space_id = {x if (x := self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))) is not None else 0},
    ilk = {task_type.value},
    draft = {self.draft}
WHERE id={self.task.id};
-- need to clean up first
DELETE FROM task_requires_task WHERE task_of_concern == {self.task.id};
DELETE FROM task_requires_task WHERE required_task == {self.task.id};
DELETE FROM task_uses_resource WHERE task_id = {self.task.id};
DELETE FROM task_trains_skill WHERE task_id = {self.task.id};
DELETE FROM constraints WHERE task_id = {self.task.id};
DELETE FROM deadlines WHERE task_id = {self.task.id};
DELETE FROM repeats WHERE task_id = {self.task.id};
COMMIT;
"""
        )
        # enter fresh, no matter whether new or old
        db.executemany(
            f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES ({self.task.id}, ?)
;
""",
            self.subtasks,
        )
        db.executemany(
            f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES (?, {self.task.id})
;
""",
            self.supertasks,
        )
        db.executemany(
            f"""
INSERT INTO task_trains_skill
(task_id, skill_id)
VALUES ({self.task.id}, ?);
""",
            self.skill_ids,
        )

        db.executemany(
            f"""
INSERT INTO task_uses_resource
(task_id, resource_id)
VALUES ({self.task.id}, ?);
""",
            (self.resources.itemData(i) for i in range(self.resources.count())),
        )
        if np.any(self.constraints):
            db.execute(
                f"""
    INSERT INTO constraints
    (task_id, flags)
    VALUES ({self.task.id}, '{''.join(str(x) for x in self.constraints.flatten())}')
            """
            )
        if self.deadline != float("inf"):
            db.execute(
                f"""
INSERT INTO deadlines
(task_id, time_of_reference)
VALUES ({self.task.id}, '{self.deadline}')
            """
            )

        if self.repeats is not None:
            db.execute(
                f"""
INSERT INTO repeats
(task_id, every_ilk, x_every, min_distance, x_per)
VALUES (
{self.task.id}, 
{self.repeats.every_ilk.value},
{self.repeats.x_every},
{self.repeats.x_per},
{self.repeats.per_ilk.value}
)
            """
            )
        db.commit()

        for win in app.list_of_task_lists:
            win.build_task_list()
        
        # it's possible to edit a task while whatnow is open - so we need to update the whatnow window        
        app.win_what.lets_check_whats_next()

    def accept(self):
        self.draft = False
        self.save_task()
        super().accept()

    def reject(self):
        super().reject()
        if self.task.do == "" and self.task.notes == "":
            db.execute(
                f"""
                DELETE FROM tasks where id == {self.task.id}
"""
            )

    def create_task(self):
        win = Editor()
        app.list_of_task_editors.append(win)
        win.show()

    def clone(self):
        win = Editor()
        win.supertasks = self.supertasks
        win.subtasks = self.subtasks
        win.desc.document().setPlainText(self.desc.document().toRawText())
        win.notes.document().setPlainText(self.notes.document().toRawText())
        win.space.setCurrentIndex(self.space.currentIndex())
        win.level.setCurrentIndex(self.level.currentIndex())
        win.constraints = self.constraints
        win.deadline = self.deadline
        win.repeats = self.repeats
        win.skill_ids = self.skill_ids
        win.priority.setValue(self.priority.value())

        app.list_of_task_editors.append(win)
        win.show()

    def set_as(self, status: str, set_flag):
        if status == "done" and set_flag:
            task_finished.Task_Finished(self.task).exec()
        else:
            db.execute(
                f"""
UPDATE tasks
SET '{property}' = {set_flag}
WHERE id == {self.task.id}
"""
            )
            db.commit()
        setattr(self.task, status, set_flag)
        self.build_button1_menu()

    def build_button1_menu(self):
        menu = QtWidgets.QMenu()
        if self.task.done:
            menu.addAction("nicht erledigt", partial(self.set_as, "done", False))
        else:
            menu.addAction("erledigt", partial(self.set_as, "done", True))

        if self.task.draft:
            menu.addAction("kein Entwurf", partial(self.set_as, "draft", False))
        else:
            menu.addAction("Entwurf", partial(self.set_as, "draft", True))

        if self.task.deleted:
            menu.addAction("nicht gelöscht", partial(self.set_as, "deleted", False))
        else:
            menu.addAction("gelöscht", partial(self.set_as, "deleted", True))

        if self.task.inactive:
            menu.addAction("aktiv", partial(self.set_as, "inactive", False))
        else:
            menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
        self.button1.setMenu(menu)


from ux import chooser, task_finished, task_running
