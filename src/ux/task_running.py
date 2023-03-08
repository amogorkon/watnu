class Running(QtWidgets.QDialog, ui.task_running.Ui_Dialog):
    def __init__(self, task):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )
        app.win_main.hide()

        app.win_settings.hide()

        self.task: Task = task
        self.skill_levels = [(skill.id, int(skill_level(skill.time_spent))) for skill in task.skills]

        self.paused = False
        self.start_time = time()
        # ticks are easier to work with in the GUI, but start/stop is used for reference in the session
        # ticks is the time tracked during the session in seconds
        self.ticks = 0
        self.paused_ticks = 0
        self.session_adjust_time_spent = 0

        self.task.last_checked = self.start_time
        self.timer = QTimer()
        self.animation_timer = QTimer()
        self.animation_timer.start(15)

        doc = QtGui.QTextDocument(task.notes)
        self.notes.setDocument(doc)

        doc = QtGui.QTextDocument(task.do)
        self.desc.setDocument(doc)

        for task_list in app.list_of_task_lists:
            task_list.button5.setEnabled(False)

        if self.task.resources:
            self.open_resources.setEnabled(True)
            text = "; ".join(url for url, ID in self.task.resources)
            self.open_resources.setText(str(text))

        self.task_space.setText(task.space)

        self.show()
        self.start_task()
        self.timer.start(1000)

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            if self.task is None:
                return
            T = time()
            self.frame.setStyleSheet(
                f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
        stop:0 black, 
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
        stop:0 {activity_color.get(self.task.primary_activity_id, "black")},
        stop:{sin(T * 0.9) * 0.5 + 0.5} {activity_color.get(self.task.secondary_activity_id,
                                                            activity_color.get(self.task.primary_activity_id, "black"))},
        stop:1 white);
}}
"""
            )

        @self.open_resources.clicked.connect
        def _():
            for url, _ in self.task.resources:
                webbrowser.open(url)

        @self.notes.document().contentsChanged.connect
        def _():
            query = statement = f"""
            UPDATE tasks SET notes= {self.notes.document().toMarkdown()}
            WHERE id={self.task.id}
            """
            if not query.exec():
                q("SQL failed:\n" + statement)
                q(query.lastError().text())
            return

        @self.timer.timeout.connect
        # timeout happens every 1 sec
        def _():
            if self.paused:
                self.paused_ticks += 1
                return

            self.ticks += 1

            session_total = self.ticks + self.session_adjust_time_spent

            rst, days = modf(session_total / (24 * 60 * 60))
            rst, hours = modf(rst * 24)
            rst, minutes = modf(rst * 60)
            seconds = rst * 60
            self.LCD_days.setProperty("intValue", days)
            self.LCD_hours.setProperty("intValue", hours)
            self.LCD_minutes.setProperty("intValue", minutes)
            self.LCD_seconds.setProperty("intValue", seconds)

        @self.button1.clicked.connect
        def _():
            pass

        @self.button2.clicked.connect
        def paused():
            if not self.paused:
                self.button2.setText("Unpause")
                self.paused = True
            else:
                self.button2.setText("Pause")
                self.paused = False

        @self.button3.clicked.connect
        def reset_button():
            self.start_time = time()
            self.session_adjust_time_spent = 0
            self.ticks = 0
            self.paused_ticks = 0

        @self.button4.clicked.connect
        def _():
            pass

        @self.button5.clicked.connect
        def stop_for_now_button():
            stop_time = time()
            if self.timer.isActive():
                self.timer.stop()
            self.task.last_checked = stop_time
            self.task.adjust_time_spent = self.session_adjust_time_spent
            self.hide()
            write_session(
                self.task.id, self.start_time, stop_time, finished=False, pause_time=self.paused_ticks
            )
            app.win_main.show()

            if not app.win_what.isHidden():
                app.win_what.raise_()

        @self.button6.clicked.connect
        def _():
            self.paused = True
            win = Editor(draft=True)
            win.exec()
            self.paused = False

        @self.button7.clicked.connect
        def minus5_button():
            if (self.session_adjust_time_spent + self.ticks) >= 5 * 60:
                self.session_adjust_time_spent -= 5 * 60
            else:
                self.session_adjust_time_spent = -self.ticks

        @self.button8.clicked.connect
        def finish_task_button():
            if timer_was_running := self.timer.isActive():
                self.timer.stop()
            win = Task_Finished(self.task, start=self.start_time, pause_time=self.paused_ticks)
            if not win.exec():
                if timer_was_running:
                    self.timer.start()
                return
            self.hide()
            app.win_main.show()
            if not app.win_what.isHidden() and app.win_what:
                app.win_what.raise_()

        @self.button9.clicked.connect
        def plus5_button():
            self.session_adjust_time_spent += 5 * 60

    def cancel(self):
        """Hard cancel - no button for this, just Esc"""
        self.timer.stop()
        self.ticks = 0  #
        self.task.last_checked = time()
        self.task = None

        for win in app.list_of_task_lists:
            win.button5.setEnabled(True)
            win.timer.start(100)
            win.filter_timer.start(1000)

        if app.list_of_task_lists:
            for win in app.list_of_task_lists:
                win.show()
                win.raise_()
        else:
            app.win_what.show()
            app.win_what.raise_()

        super().reject()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel()
        event.accept()

    def start_task(self):
        # check if working conditions are optimal once a day
        query = submit_sql(
            """
        SELECT start 
        FROM sessions
        ORDER BY start DESC;
        """
        )

        last_started = query.value(0) if query.next() else 0
        now = datetime.now()
        then = datetime.fromtimestamp(last_started)

        if now.date() != then.date():
            mb = QtWidgets.QMessageBox()
            mb.setText(
                """
Checkliste für optimale Produktivität:
- Raumtemperatur bei 21°C?
- Ausleuchtung bei 1000 Lux?
- Relative Luftfeuchtigkeit bei ~50%?
- Kaffee/Tee & genug Wasser zur Hand?
- Ausgeruht? Geist fokusiert?
- Körper in Schwung?
- Das Richtige auf den Ohren?
"""
            )
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec()
        query = submit_sql(
            """
        SELECT text, mantra_id
        FROM mantras
        ORDER BY last_time ASC;
        """
        )

        mantra_id = None

        if not query.next():
            mantra = None
        else:
            mantra, mantra_id = query.value(0), query.value(1)

        td = now - then

        mb = QtWidgets.QMessageBox()
        mb.setText(
            f"""
Gesundheitshinweis:
Alle ~25 Minuten kurz Stoßlüften & ausreichend Wasser trinken :)
Und denk dran: 
{mantra or "Always look on the bright side of life!"}
"""
        )

        if mantra:
            submit_sql(
                f"""
    UPDATE mantras
    SET last_time = {int(time())}
    WHERE mantra_id = {mantra_id}
    """
            )
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec()

    def finished(self):
        for win in app.list_of_task_lists:
            win.button5.setEnabled(True)
            win.timer.start(100)
            win.filter_timer.start(1000)


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
        write_session(self.task.id, self.start, time(), finished=True, pause_time=self.pause_time)

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
                win = Editor(task=self.task, draft=True)
                win.exec()
        return True
