import contextlib
import webbrowser
from collections import namedtuple
from functools import partial
from typing import Literal

import numpy as np
from beartype import beartype
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QVariant
from PyQt6.QtGui import QCloseEvent, QHideEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import QPushButton, QWizard

import src.ui as ui
from src import app, config, db
from src.classes import ACTIVITY, ILK, LEVEL, Task
from src.ux import space_editor, task_finished
from src.ux_helpers import SpaceMixin, get_space_priority

_translate = QCoreApplication.translate


@beartype
class TaskEditor(QtWidgets.QWizard, ui.task_editor.Ui_Wizard, mixin.SpaceMixin):
    """Editor for new or existing tasks."""

    def __init__(
        self,
        task: Task = None,
        /,
        *,
        cloning: bool = False,
        templating: bool = False,
        as_sup: Literal[-1, 0, 1] = 0,
        current_space: str | None = None,
        draft: bool = False,
    ):
        super().__init__()
        print(f"{repr(task)} {current_space=} {draft=} {cloning=} {templating=} {as_sup=}")
        self.setupUi(self)

        self._init_defaults(task, cloning, templating, as_sup, current_space, draft)
        self.build_space_list(first_item_text="")
        self._init_task_edit(task) if task else self._init_task_new(current_space)
        self._init_ui_elements()
        self._init_signals()
        self._post_init_setup(cloning, templating, as_sup)

    def _init_defaults(self, task, cloning, templating, as_sup, current_space, draft):
        self.task = task
        self.cloning = cloning
        self.templating = templating
        self.as_sup = as_sup
        self.current_space = current_space
        self.draft = draft

        self.deadline = float("inf")
        self.repeats: namedtuple = None
        self.constraints: np.ndarray = np.zeros((7, 288))
        self.subtasks: list[int] = []
        self.supertasks: list[int] = []
        self.skill_ids: list[int] = []

    def _init_ui_elements(self):
        app.list_of_task_editors.append(self)
        app.list_of_windows.append(self)
        self.setWindowTitle(f"Task {self.task.id}")
        self.original_window_title = self.windowTitle()
        self.statusBar = QtWidgets.QStatusBar()
        self.page1.layout().addWidget(self.statusBar)
        self.statusBar.setSizeGripEnabled(False)
        # fira rules!
        self.do.setFont(app.fira_font)
        self.notes.setFont(app.fira_font)
        self.gui_timer = QTimer()
        self.setButtonText(
            QWizard.WizardButton.CustomButton1,
            "als Entwurf speichern",
        )

        def _show_state_depending():
            statuses = [x for x in ["done", "draft", "deleted", "inactive"] if getattr(self.task, x)]
            title_status = " - " + ", ".join(statuses) if statuses else ""
            self.setWindowTitle(f"{self.original_window_title}{title_status}")

            self.button(QWizard.WizardButton.FinishButton).setEnabled(len(self.do.toPlainText()))

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

        _show_state_depending()  # first time
        self.gui_timer.timeout.connect(_show_state_depending)

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

        def _space_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Neuer Space",
                "Name des neuen Space",
                QtWidgets.QLineEdit.EchoMode.Normal,
                "",
            )
            if okPressed and text != "":
                db.execute(
                    """
INSERT OR IGNORE INTO spaces (name)
VALUES (?)
""",
                    (text,),
                )
                db.commit()
                space_editor.SpaceEditor(text).exec()
                self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
                for win in app.list_of_task_editors:
                    win.build_space_list()
                for win in app.list_of_task_lists:
                    win.build_space_list()

        menu = QtWidgets.QMenu()
        menu.addAction("hinzufügen", _space_add)

        def _space_delete():
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
                            """
DELETE FROM spaces where name==?
""",
                            (space_name,),
                        )
                        db.commit()
                        self.statusBar.showMessage(f"Raum '{space_name}' gelöscht.", 5000)
                        for win in app.list_of_task_lists:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_editors:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_organizers:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

        menu.addAction("löschen", _space_delete)

        def space_edit():
            if self.space.currentData() is None:
                self.statusBar.showMessage("Dieser 'Raum' lässt sich nicht bearbeiten.", 5000)
                return
            space_editor.SpaceEditor(self.space.currentText()).exec()

        menu.addAction("bearbeiten", space_edit)

        self.button9a.setMenu(menu)

        self.setButtonText(QWizard.WizardButton.FinishButton, "Fertig")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Abbrechen")
        self.button(QWizard.WizardButton.CustomButton2).setText(_translate("Wizard", "löschen"))

    def _init_signals(self):
        self.button1.clicked.connect(lambda e: print(e))
        self.button2.clicked.connect(self._time_constraints_button)
        self.button3.clicked.connect(lambda: self.organize(True))
        self.button4.clicked.connect(lambda: None)
        self.button5.clicked.connect(self.start_task)
        self.button6.clicked.connect(lambda: None)
        self.button7.clicked.connect(lambda: choose_deadline.DeadlineChooser(self, self.task).exec())
        self.button8.clicked.connect(lambda: choose_repeats.RepeatChooser(self, self.task).exec())

        url = "https://www.youtube.com/watch?v=kvZEzEOPRfw"
        self.button(QWizard.WizardButton.HelpButton).clicked.connect(lambda: webbrowser.open(url))
        self.button(QWizard.WizardButton.CustomButton2).clicked.connect(self.delete_task)

        # shortcut for num9 to click button9 (Spaces)
        self.button9a.setShortcut("9")

        self.kind_of.buttonToggled.connect(
            lambda: self.button8.setEnabled(self.is_task.isChecked() or self.is_habit.isChecked())
        )

        self.resource_remove.clicked.connect(lambda: self.resources.removeItem(self.resources.currentIndex()))

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(
            lambda: self.showNormal() if self.isFullScreen() else self.showFullScreen()
        )

        # Draft Button
        @self.button(QWizard.WizardButton.CustomButton1).clicked.connect
        def _():
            self.draft = True
            self._save()
            self.done(12)

        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.accept)

        self.organize_subtasks.clicked.connect(lambda: self.organize(True))
        self.organize_supertasks.clicked.connect(lambda: self.organize(False))
        self.choose_constraints_button.clicked.connect(
            lambda: choose_constraints.ConstraintChooser(self, self.task).exec()
        )
        self.choose_deadline_button.clicked.connect(
            lambda: choose_deadline.DeadlineChooser(self, self.task).exec()
        )

        self.space.currentIndexChanged.connect(self._space_index_changed)

    def _init_task_edit(self, task):
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
        self.primary_activity.setCurrentIndex(self.primary_activity.findText(self.task.primary_activity.name))

        self.secondary_activity.setCurrentIndex(
            self.secondary_activity.findText(self.task.secondary_activity.name)
        )

        self.repeats = self.task.repeats
        self.constraints = x if (x := self.task.constraints) is not None else np.zeros((7, 288))
        self.task = task
        # set workload_hours and workload_minutes accordingly
        self.workload_hours.setValue(self.task.workload // 60)
        self.workload_minutes.setValue(self.task.workload % 60)

    def _init_task_new(self, current_space):
        self.space.setCurrentIndex(self.space.findText(current_space or config.last_edited_space))

        query = db.execute("""INSERT INTO tasks (do, draft) VALUES ("",True);""")
        db.commit()
        self.task = Task.from_id(query.lastrowid)
        app.tasks[self.task.id] = self.task
        self.draft = True

    def _post_init_setup(self, cloning, templating, as_sup):
        # clone as subtask of the given task
        if as_sup == -1:
            self.supertasks = [self.task.id]

        # given task is a subtask of the new task
        if as_sup == 1:
            self.subtasks = [self.task.id]

        # just a reminder for the user which task is sub-/supertask
        if as_sup:
            self.do.setPlaceholderText(self.task.do)
            self.do.setPlainText("")
            self.notes.setPlaceholderText(self.task.notes)
            self.notes.setPlainText("")

        for item in ACTIVITY:
            if item == ACTIVITY.unspecified:
                continue
            self.primary_activity.addItem(item.name, QVariant(item.value))
            self.secondary_activity.addItem(item.name, QVariant(item.value))

        for i, item in enumerate(LEVEL):
            self.level.addItem(item.name)
            self.level.setItemData(i, item.value, Qt.ItemDataRole.UserRole)

        self.level.setCurrentIndex(2)

        self.page1.registerField(
            "task*",
            self.do,
            "plainText",
            changedSignal=self.do.textChanged,
        )

        if self.task.space:
            assert self.task.space_id == self.task.space.space_id, breakpoint()

        self.gui_timer.start(100)

        if cloning:
            self.statusBar.showMessage("Bearbeite Klon...", 5000)
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))

        if templating:
            self.setWindowTitle(_translate("Wizard", "Bearbeite verknüpfte Aufgabe"))

        def create_task():
            win = TaskEditor(current_space=self.space.currentText())
            app.list_of_task_editors.append(win)
            app.list_of_windows.append(win)
            win.show()

        menu = QtWidgets.QMenu()
        menu.addAction("ohne Vorlage", create_task)
        menu.addAction("als Klon von dieser Aufgabe", self._clone)
        self.button6.setMenu(menu)

        self.activateWindow()

    def _save(self) -> None:
        config.save()

        self._save_task_details()
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

    def save_repeats(self) -> None:
        if self.repeats is not None:
            db.execute(
                """
                INSERT INTO repeats
                (task_id, every_ilk, x_every, min_distance, x_per)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    self.task.id,
                    self.repeats.every_ilk.value,
                    self.repeats.x_every,
                    self.repeats.x_per,
                    self.repeats.per_ilk.value,
                ),
            )

    def save_deadline(self) -> None:
        if self.deadline != float("inf"):
            db.execute(
                """
                INSERT INTO deadlines
                (task_id, time_of_reference)
                VALUES (?, ?)
                """,
                (self.task.id, self.deadline),
            )

    def save_constraints(self) -> None:
        if np.any(self.constraints):
            db.execute(
                """
                INSERT INTO constraints
                (task_id, flags)
                VALUES (?, ?)
                """,
                (self.task.id, "".join(str(x) for x in self.constraints.flatten())),
            )

    def save_resources(self) -> None:
        for url in (self.resources.itemText(i) for i in range(self.resources.count())):
            db.execute(
                "INSERT OR IGNORE INTO resources (url) VALUES (?);",
                (url,),
            )
            resource_id = db.execute(
                "SELECT resource_id FROM resources WHERE url = ?;",
                (url,),
            ).fetchone()[0]
            db.execute(
                "INSERT INTO task_uses_resource (task_id, resource_id) VALUES (?, ?);",
                (self.task.id, resource_id),
            )

    def save_subsup(self) -> None:
        db.executemany(
            """
            INSERT OR IGNORE INTO task_requires_task
            (task_of_concern, required_task)
            VALUES (?, ?)
            """,
            [(self.task.id, task_id) for task_id in self.subtasks],
        )
        db.executemany(
            """
            INSERT OR IGNORE INTO task_requires_task
            (task_of_concern, required_task)
            VALUES (?, ?)
            """,
            [(task_id, self.task.id) for task_id in self.supertasks],
        )
        db.executemany(
            """
            INSERT INTO task_trains_skill
            (task_id, skill_id)
            VALUES (?, ?);
            """,
            [(self.task.id, skill_id) for skill_id in self.skill_ids],
        )

    def save_cleanup(self) -> None:
        """need to clean up first, because of foreign key constraints"""
        db.executescript(
            """
            BEGIN;
            DELETE FROM task_requires_task WHERE task_of_concern == ?;
            DELETE FROM task_requires_task WHERE required_task == ?;
            DELETE FROM task_uses_resource WHERE task_id = ?;
            DELETE FROM task_trains_skill WHERE task_id = ?;
            DELETE FROM constraints WHERE task_id = ?;
            DELETE FROM deadlines WHERE task_id = ?;
            DELETE FROM repeats WHERE task_id = ?;
            COMMIT;
            """,
            (
                self.task.id,
                self.task.id,
                self.task.id,
                self.task.id,
                self.task.id,
                self.task.id,
                self.task.id,
            ),
        )

    def workload(self) -> int:
        """Return the workload in minutes from the GUI."""
        return self.workload_minutes.value() + 60 * self.workload_hours.value()

    def _save_task_details(self) -> None:
        task_type = ILK.task
        if self.is_habit.isChecked():
            task_type = ILK.habit
        if self.is_routine.isChecked():
            task_type = ILK.routine
        if self.is_tradition.isChecked():
            task_type = ILK.tradition

        data: dict[str, str | int | float] = {
            "do": self.do.toPlainText(),
            "notes": self.notes.toPlainText(),
            "priority": self.priority.value(),
            "level_id": self.level.currentData(),
            "primary_activity_id": self.primary_activity.currentData(),
            "secondary_activity_id": self.secondary_activity.currentData(),
            "space_id": x if (x := self.space.currentData()) is not None else 0,
            "ilk": task_type.value,
            "draft": self.draft,
            "fear": self.fear.value(),
            "difficulty": self.difficulty.value(),
            "embarrassment": self.embarrassment.value(),
            "workload": self.workload(),
        }

        # TODO: space_id == 0 is NOT NULL!!!
        db.execute(
            """
            UPDATE tasks
            SET
                do = :do,
                notes = :notes,
                priority = :priority,
                level_id = :level_id,
                primary_activity_id = :primary_activity_id,
                secondary_activity_id = :secondary_activity_id,
                space_id = :space_id,
                ilk = :ilk,
                draft = :draft,
                fear = :fear,
                difficulty = :difficulty,
                embarrassment = :embarrassment,
                workload = :workload
            WHERE id = :task_id
            """,
            {**data, "task_id": self.task.id},
        )

    def accept(self) -> None:
        self.draft = False
        self._save()
        self.task.reload()
        super().accept()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._kill()

    def hideEvent(self, event: QHideEvent) -> None:
        self._kill()

    def reject(self) -> None:
        super().reject()
        self._kill()

    def _kill(self) -> None:
        self.gui_timer.stop()
        # sometimes Qt hides and then closes the window, so this is called twice
        with contextlib.suppress(ValueError):
            app.list_of_task_editors.remove(self)
        with contextlib.suppress(ValueError):
            app.list_of_windows.remove(self)
        assert self not in app.list_of_task_editors, breakpoint()
        assert self not in app.list_of_windows, breakpoint()

        if self.task.do == "" and self.task.notes == "":
            self.task.really_delete()

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()
        self.close()
        self.deleteLater()

    def _clone(self) -> None:
        win = TaskEditor()
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
        win.show()

    def set_as(self, status: str, set_flag: bool) -> None:
        if status == "done" and set_flag:
            task_finished.Finisher(self.task).exec()
        else:
            db.execute(
                """
UPDATE tasks
SET ? = ?
WHERE id == ?
""",
                (status, set_flag, self.task.id),
            )
            db.commit()
        setattr(self.task, status, set_flag)
        self._build_button1_menu()

    def _build_button1_menu(self) -> None:
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
            menu.addAction(
                "nicht gelöscht",
                partial(self.set_as, "deleted", False),
            )
        else:
            menu.addAction("gelöscht", partial(self.set_as, "deleted", True))

        if self.task.inactive:
            menu.addAction("aktiv", partial(self.set_as, "inactive", False))
        else:
            menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
        self.button1.setMenu(menu)

    def delete_task(self) -> None:
        self.task.delete()
        self.reject()
        app.win_what.lets_check_whats_next()

    def resource_added(self):
        text, okPressed = QtWidgets.QInputDialog.getText(
            self,
            "Resource hinzufügen",
            "Welche URL?",
            QtWidgets.QLineEdit.EchoMode.Normal,
            "",
        )

        if okPressed and text != "":
            self.resources.addItem(text)

    def organize(self, depends_on):
        win = task_organizer.Organizer(task=self.task, editor=self, depends_on=depends_on)
        self.hide()
        win.show()
        win.raise_()

    def start_task(self):
        self._save()
        self.done(12)
        task_running.Running(self.task)

    def _space_index_changed(self):
        space_id = self.space.currentData()
        if space_id is not None:
            for (
                primary_activity_id,
                secondary_activity_id,
            ) in db.execute(
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
        config.last_edited_space = self.space.currentText() or config.last_edited_space
        config.save()

    def _time_constraints_button(self):
        task_finished.Finisher(self.task, direct=True).exec()
        self.accept()


from src.ux import (  # noqa: E402
    choose_constraints,
    choose_deadline,
    choose_repeats,
    task_organizer,
    task_running,
)

# some orphaned code, check if it's needed

#     lambda: self.total_priority.setValue(
# self.resource_add.clicked.connect(self.resource_add)

# self.priority.valueChanged.connect(
#             space_priority=get_space_priority(self.space.currentData()),
#             priority=self.priority.value(),
#         self.task.get_total_priority(
#     )
#         )
# )


def make_new_and_show_all():
    """
    Creates a new task checklist and shows all.
    """
    win = TaskEditor()
    for win in app.list_of_task_editors:
        win.show()
    return win
