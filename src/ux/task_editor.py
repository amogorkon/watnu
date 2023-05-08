import webbrowser
from collections import namedtuple
from functools import partial
from typing import Literal

import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, QSize, Qt, QTimer, QVariant
from PyQt6.QtGui import QCursor, QIcon, QKeySequence, QShortcut
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtWidgets import QPushButton, QWizard

import src.ui as ui
from src.classes import ACTIVITY, ILK, Task
from src.functions import typed
from src.stuff import app, config, db
from src.ux import space_editor, task_finished, task_list
from src.ux.helper_functions import get_space_priority, build_space_list

_translate = QCoreApplication.translate


class Editor(QtWidgets.QWizard, ui.task_editor.Ui_Wizard):
    """Editor for new or existing tasks."""

    def __init__(
        self,
        task: Task = None,
        cloning: bool = False,
        templating: bool = False,
        as_sup: Literal[-1] | Literal[0] | Literal[1] = 0,
        current_space: str | None = None,
        draft: bool = False,
    ):
        super().__init__()
        print(f"{repr(task)} {current_space=} {draft=} {cloning=} {templating=} {as_sup=}")
        self.setupUi(self)
        self.original_window_title = self.windowTitle()
        self.statusBar = QtWidgets.QStatusBar()
        self.page_layout.addWidget(self.statusBar)
        self.statusBar.setSizeGripEnabled(False)

        # arguments passed in

        self.task = task
        self.cloning = cloning
        self.templating = templating
        self.as_sup = as_sup
        self.current_space = current_space
        self.draft = draft

        url = "https://www.youtube.com/watch?v=kvZEzEOPRfw"
        self.button(QWizard.WizardButton.HelpButton).clicked.connect(lambda: webbrowser.open(url))

        # custombutton2 should be "löschen"
        self.button(QWizard.WizardButton.CustomButton2).setText(_translate("Wizard", "löschen"))

        # custombutton2 to delete the task
        self.button(QWizard.WizardButton.CustomButton2).clicked.connect(self.delete_task)

        # defaults
        self.deadline = float("inf")
        self.repeats: namedtuple = None
        self.constraints: np.ndarray = np.zeros((7, 288))
        self.subtasks: list[int] = []
        self.supertasks: list[int] = []
        self.skill_ids: list[int] = []

        @self.priority.valueChanged.connect
        def _():
            self.total_priority.setValue(
                self.task.get_total_priority(
                    priority=self.priority.value(),
                    space_priority=get_space_priority(self.space.currentData()),
                )
            )

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)

        build_space_list(self, first_item_text="")

        for item in ACTIVITY:
            if item == ACTIVITY.unspecified:
                continue
            self.primary_activity.addItem(item.name, QVariant(item.value))
            self.secondary_activity.addItem(item.name, QVariant(item.value))

        model = QSqlTableModel()
        model.setTable("levels")
        model.setSort(0, Qt.SortOrder.DescendingOrder)
        model.select()
        self.level.setModel(model)
        self.level.setModelColumn(1)
        self.level.setCurrentIndex(2)

        self.page.registerField("task*", self.do, "plainText", changedSignal=self.do.textChanged)

        # editing a task - need to set all values accordingly
        if task:
            self.deadline = task.deadline
            self.skill_ids = self.task.skill_ids
            self.priority.setValue(task.priority)
            self.total_priority.setValue(task.get_total_priority())
            for url, ID in task.resources:
                self.resources.addItem(url, ID)

            self.do.document().setPlainText(task.do)

            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findData(self.task.space.space_id))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.primary_activity.setCurrentIndex(
                self.primary_activity.findText(self.task.primary_activity.name)
            )

            self.secondary_activity.setCurrentIndex(
                self.secondary_activity.findText(self.task.secondary_activity.name)
            )

            self.repeats = self.task.repeats
            self.constraints = x if (x := self.task.constraints) is not None else np.zeros((7, 288))
            self.task = task
            # set workload_hours and workload_minutes accordingly
            self.workload_hours.setValue(self.task.workload // 60)
            self.workload_minutes.setValue(self.task.workload % 60)

        # new task - preset space by previous edit
        else:
            self.space.setCurrentIndex(self.space.findText(current_space or config.last_edited_space))
            query = db.execute("""INSERT INTO tasks (do, draft) VALUES ("",True);""")
            db.commit()
            self.task = Task.from_id(query.lastrowid)
            app.tasks[self.task.id] = self.task
            self.draft = True

        if self.task.space:
            assert self.task.space_id == self.task.space.space_id, breakpoint()

        self.gui_timer = QTimer()
        self.gui_timer.start(100)

        def show_state_depending():
            statuses = [x for x in ["done", "draft", "deleted", "inactive"] if getattr(self.task, x)]
            title_status = " - " + ", ".join(statuses) if statuses else ""
            self.setWindowTitle(f"{self.original_window_title}{title_status}")

            # disable buttons if task.do is empty
            has_content = bool(self.do.toPlainText())
            self.button(QWizard.WizardButton.CustomButton1).setEnabled(has_content)
            self.button(QWizard.WizardButton.CustomButton2).setEnabled(has_content)
            for i in range(self.num_buttons.count()):
                item = self.num_buttons.itemAt(i).widget()
                if isinstance(item, QPushButton):
                    item.setEnabled(has_content)

            match self.task.ilk:
                case ILK.habit.value:
                    self.is_habit.setChecked(True)
                    self.button8.setText("")
                case ILK.tradition.value:
                    self.is_tradition.setChecked(True)
                    self.button8.setEnabled(True)
                case ILK.routine.value:
                    self.is_routine.setChecked(True)
                    self.button8.setEnabled(True)

            self.organize_supertasks.setToolTip(f"von dieser Aufgabe abhängig: {len(self.task.supertasks)}")
            self.organize_subtasks.setToolTip(f"diese Aufgabe ist abhängig von: {len(self.task.subtasks)}")

            if self.task.deadline == float("inf"):
                self.choose_deadline_button.hide()
            else:
                self.choose_deadline_button.show()

            if not self.task.constraints:
                self.choose_constraints_button.hide()
            else:
                self.choose_constraints_button.show()

            if not self.task.repeats:
                self.choose_repeats_button.hide()
            else:
                self.choose_repeats_button.show()

            if not self.task.skill_ids:
                self.choose_skills_button.hide()
            else:
                self.choose_skills_button.show()

            if not self.task.subtasks:
                self.organize_subtasks.hide()
            else:
                self.organize_subtasks.show()

            if not self.task.supertasks:
                self.organize_supertasks.hide()
            else:
                self.organize_supertasks.show()

            if app.win_running:
                self.button5.setEnabled(False)

        show_state_depending()  # first time
        self.gui_timer.timeout.connect(show_state_depending)

        self.setButtonText(QWizard.WizardButton.CustomButton1, "als Entwurf speichern")

        @self.button(QWizard.WizardButton.CustomButton1).clicked.connect
        def _():
            self.draft = True
            self.save()
            self.done(12)

        self.setButtonText(QWizard.WizardButton.FinishButton, "Fertig")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Abbrechen")

        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.accept)

        if cloning:
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))

        if templating:
            self.setWindowTitle(_translate("Wizard", "Bearbeite verknüpfte Aufgabe"))

        # clone as subtask of the given task
        if as_sup == -1:
            self.supertasks = [self.task.id]

        # given task is a subtask of the new task
        if as_sup == 1:
            self.subtasks = [self.task.id]

        menu = QtWidgets.QMenu()
        menu.addAction("ohne Vorlage", self.create_task)
        menu.addAction("als Klon von dieser Aufgabe", self.clone)
        self.button6.setMenu(menu)

        self.activateWindow()

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
                self.resources.addItem(text)

        @self.resource_remove.clicked.connect
        def _():
            self.resources.removeItem(self.resources.currentIndex())

        @self.button1.clicked.connect
        def set_status():
            pass

        @self.button2.clicked.connect
        def time_constraints_button():
            task_finished.Finisher(self.task, direct=True).exec()
            self.accept()
            # self.done(12)

        def organize(depends_on):
            win = task_organizer.Organizer(task=self.task, editor=self, depends_on=depends_on)
            app.list_of_task_organizers.append(win)
            app.list_of_windows.append(win)
            self.hide()
            win.show()
            win.raise_()

        self.button3.clicked.connect(lambda: organize(True))
        self.organize_subtasks.clicked.connect(lambda: organize(True))
        self.organize_supertasks.clicked.connect(lambda: organize(False))
        self.choose_constraints_button.clicked.connect(
            lambda: choose_constraints.ConstraintChooser(self, self.task).exec()
        )
        self.choose_deadline_button.clicked.connect(
            lambda: choose_deadline.DeadlineChooser(self, self.task).exec()
        )

        @self.button4.clicked.connect
        def button4():
            pass

        @self.button5.clicked.connect
        def start_button():
            self.save()
            self.done(12)
            task_running.Running(self.task)

        @self.button6.clicked.connect
        def _():
            pass

        @self.button7.clicked.connect
        def deadline():
            choose_deadline.DeadlineChooser(self, self.task).exec()

        @self.button8.clicked.connect
        def repeats_button():
            choose_repeats.RepeatChooser(self, self.task).exec()

        # button9

        def space_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self, "Neuer Space", "Name des neuen Space", QtWidgets.QLineEdit.EchoMode.Normal, ""
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
                db.commit()
                space_editor.Space_Editor(text).exec()
                self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
                for win in app.list_of_task_editors:
                    build_space_list(win)
                for win in app.list_of_task_lists:
                    build_space_list(win)

        menu = QtWidgets.QMenu()
        menu.addAction("hinzufügen", space_add)

        def space_delete():
            space_name = self.space.currentText()
            if [task for task in app.tasks.values() if task.space.name == space_name]:
                QtWidgets.QMessageBox.information(
                    self,
                    "Sorry..",
                    f"Der Raum '{space_name}' ist nicht leer und kann daher nicht gelöscht werden.",
                )
            else:
                match QtWidgets.QMessageBox.question(
                    self,
                    "Wirklich den ausgewählten Raum löschen?",
                    f"Soll der Raum '{space_name}' wirklich gelöscht werden?",
                ):
                    case QtWidgets.QMessageBox.StandardButton.Yes:
                        db.execute(
                            f"""
DELETE FROM spaces where name=='{space_name}'
"""
                        )
                        db.commit()
                        self.statusBar.showMessage(f"Raum '{space_name}' gelöscht.", 5000)
                        for win in app.list_of_task_lists:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_editors:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_organizers:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

        menu.addAction("löschen", space_delete)

        def space_edit():
            if self.space.currentData() is None:
                self.statusBar.showMessage("Dieser 'Raum' lässt sich nicht bearbeiten.", 5000)
                return
            space_editor.Space_Editor(self.space.currentText()).exec()

        menu.addAction("bearbeiten", space_edit)

        self.button9.setMenu(menu)

        # shortcut for num9 to click button9
        self.button9.setShortcut("9")

        @self.space.currentIndexChanged.connect
        def _():
            space_id = self.space.currentData()
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

            self.total_priority.setValue(
                self.task.get_total_priority(
                    priority=self.priority.value(),
                    space_priority=get_space_priority(self.space.currentData()),
                )
            )

        @self.space.currentIndexChanged.connect
        def space_switched():
            config.last_edited_space = self.space.currentText() or config.last_edited_space
            config.save()

    def save(self):
        config.save()

        self.save_task_details()
        # enter fresh, no matter whether new or old
        self.save_cleanup()
        self.save_subsup()
        self.save_resources()
        self.save_constraints()
        self.save_deadline()
        self.save_repeats()
        db.commit()

        app.tasks[self.task.id] = self.task

        for win in app.list_of_task_lists:
            win.build_task_table()

        # it's possible to edit a task while whatnow is open - so we need to update the whatnow window
        app.win_what.lets_check_whats_next()

    def save_repeats(self):
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

    def save_deadline(self):
        if self.deadline != float("inf"):
            db.execute(
                f"""
INSERT INTO deadlines
(task_id, time_of_reference)
VALUES ({self.task.id}, '{self.deadline}')
            """
            )

    def save_constraints(self):
        if np.any(self.constraints):
            db.execute(
                f"""
    INSERT INTO constraints
    (task_id, flags)
    VALUES ({self.task.id}, '{''.join(str(x) for x in self.constraints.flatten())}')
            """
            )

    def save_resources(self):
        for url in (self.resources.itemText(i) for i in range(self.resources.count())):
            db.execute("INSERT OR IGNORE INTO resources (url) VALUES (?);", (url,))
            resource_id = db.execute("SELECT resource_id FROM resources WHERE url = ?;", (url,)).fetchone()[0]
            db.execute(
                "INSERT INTO task_uses_resource (task_id, resource_id) VALUES (?, ?);",
                (self.task.id, resource_id),
            )

    def save_subsup(self):
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

    def save_cleanup(self):
        db.executescript(
            f"""
BEGIN;
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

    def workload(self):
        """Return the workload in minutes from the GUI."""
        return self.workload_minutes.value() + 60 * self.workload_hours.value()

    def save_task_details(self):
        task_type = ILK.task
        if self.is_habit.isChecked():
            task_type = ILK.habit
        if self.is_routine.isChecked():
            task_type = ILK.routine
        if self.is_tradition.isChecked():
            task_type = ILK.tradition

        # TODO: space_id == 0 is NOT NULL!!!
        db.execute(
            f"""
UPDATE tasks 
SET 
    do = ?,
    notes = ?,
    priority = {self.priority.value()},
    level_id = {self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))},
    primary_activity_id = {x if (x := self.primary_activity.currentData()) is not None else "NULL"},
    secondary_activity_id = {x if (x := self.secondary_activity.currentData()) is not None else "NULL"},
    space_id = {x if (x := self.space.currentData()) is not None else 0},
    ilk = {task_type.value},
    draft = {self.draft},
    fear = {self.fear.value()},
    difficulty = {self.difficulty.value()},
    embarrassment = {self.embarrassment.value()},
    workload = {self.workload()}
WHERE id={self.task.id}
""",
            (self.do.toPlainText(), self.notes.toPlainText()),
        )

    def accept(self):
        self.draft = False
        self.save()
        self.task.reload()
        super().accept()

    def closeEvent(self, event):
        self.kill()

    def hideEvent(self, event):
        self.kill()

    def kill(self):
        # sometimes Qt hides and then closes the window, so this is called twice
        self.killed = True
        if self.killed:
            return
        self.gui_timer.stop()
        app.list_of_task_editors.remove(self)
        app.list_of_windows.remove(self)

        if self.task.do == "" and self.task.notes == "":  # TODO: this is a hack
            self.task.really_delete()

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()

    def create_task(self):
        win = Editor()
        self.add_win_to_app(win)

    def clone(self):
        win = Editor()
        win.supertasks = self.supertasks
        win.subtasks = self.subtasks
        win.do.document().setPlainText(self.do.document().toRawText())
        win.notes.document().setPlainText(self.notes.document().toRawText())
        win.space.setCurrentIndex(self.space.currentIndex())
        win.level.setCurrentIndex(self.level.currentIndex())
        win.constraints = self.constraints
        win.deadline = self.deadline
        win.repeats = self.repeats
        win.skill_ids = self.skill_ids
        win.priority.setValue(self.priority.value())
        win.total_priority.setValue(self.total_priority.value())

        self.add_win_to_app(win)

    def add_win_to_app(self, win):
        app.list_of_task_editors.append(win)
        app.list_of_windows.append(win)
        win.show()

    def set_as(self, status: str, set_flag):
        if status == "done" and set_flag:
            task_finished.Finisher(self.task).exec()
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

    def delete_task(self):
        self.task.delete()
        self.reject()
        app.win_what.lets_check_whats_next()


from src.ux import (
    choose_constraints,
    choose_deadline,
    choose_repeats,
    choose_skills,
    task_list,
    task_organizer,
    task_running,
)
