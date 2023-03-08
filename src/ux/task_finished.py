from math import modf
from time import time

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox

import ui
from algo import skill_level
from classes import ILK, Task, submit_sql
from config import Config
from ux import app, task_editor

config: Config
app: app.Application
db: QSqlDatabase


class Task_Finished(QtWidgets.QDialog, ui.task_finished.Ui_Dialog):
    def __init__(
        self,
        task: Task,
        start: float = None,
        stop: float = None,
        old_skills=None,
        pause_time: int = 0,
    ):
        """
        Window to finish a task.

        Works either from Running or TaskList. Running will have a session open, so we need to close it, when the task really is finished.


        Args:
            task (Task): current task.
            ticks (int, optional): . Defaults to 0.
            start (int, optional): Time task was started current session. Defaults to None.
            stop (int, optional): Time task was stopped current session. Defaults to None.
            old_skills (_type_, optional): _description_. Defaults to None.
            pause_time (int, optional): Pause time of the current session. Defaults to 0.
        """
        super().__init__()
        self.setupUi(self)
        self.task = task
        self.start = start or time()
        self.stop = stop or self.start
        self.pause_time = pause_time
        self.old_skills = old_skills or [
            (skill.id, int(skill_level(skill.time_spent))) for skill in task.skills
        ]

        self.task_desc.setText(task.do)
        # let's ask the DB for previous sessions and add the current time
        current_session_time = self.stop - self.start

        self.total = task.time_spent + task.adjust_time_spent + current_session_time - self.pause_time
        rst, days = modf(self.total / (60 * 60 * 24))
        rst, hours = modf(self.total / (60 * 60))
        rst, minutes = modf(rst * 60)

        self.days.setValue(int(days))
        self.hours.setValue(int(hours))
        self.minutes.setValue(int(minutes))

    def accept(self):
        super().accept()
        if self.task.ilk not in (ILK.habit, ILK.routine):  # ? is that right?
            total = self.hours.value() * 60 * 60 + self.minutes.value() * 60 - self.pause_time
        else:
            total = (
                self.task.time_spent
                + self.task.adjust_time_spent
                + self.hours.value() * 60 * 60
                + self.minutes.value() * 60
            )

        submit_sql(
            f"""
    UPDATE tasks 
    SET adjust_time_spent = {total - self.task.time_spent},     
        done=TRUE
    WHERE id={self.task.id};
    """
        )
        app.write_session(self.task.id, self.start, time(), finished=True, pause_time=self.pause_time)

        new_skills = [(skill.id, int(skill_level(skill.time_spent))) for skill in self.task.skills]

        for x, y in zip(self.old_skills, new_skills):
            if x[1] < y[1]:
                mb = QtWidgets.QMessageBox()
                mb.setText(
                    """
YEAH! You made it to the next LEVEL in {y[0]}: {y[1]}!
"""
                )
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/star.svg"))
                mb.setWindowTitle("LEVEL UP")
                mb.exec()

        for win in app.list_of_task_lists:
            win.button5.setEnabled(True)
            win.build_task_list()
        app.win_what.lets_check_whats_next()

        if self.task.ilk is ILK.tradition:
            mb = QMessageBox()
            mb.setText(
                """
Die beendete Aufgabe ist eine Tradition - soll jetzt ein neuer Eintrag für den nächsten Stichtag erstellt werden?
"""
            )
            mb.setInformativeText("Bitte bestätigen!")
            mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            mb.setDefaultButton(QMessageBox.Yes)
            # TODO check on edit if deadline and repeat is set for tradition
            if mb.exec():
                win = task_editor.Editor(task=self.task, draft=True)
                win.exec()
        return True