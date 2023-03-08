class What_Now(QtWidgets.QDialog, ui.what_now.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_priority = None
        self.task_timing = None
        self.task_balanced = None
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )
        self.sec_timer = QTimer()
        self.sec_timer.start(1000)
        self.animation_timer = QTimer()
        self.animation_timer.start(15)
        self.cancel.setShortcut(_translate("Dialog", "0"))

        self.balanced_tasks = None
        self.priority_tasks = None
        self.timing_tasks = None

        for L in app.list_of_task_lists:
            L.timer.stop()
            L.filter_timer.stop()
            L.hide()

        @self.edit_priority.clicked.connect
        def edit_priority():
            win = Editor(self.task_priority)
            app.list_of_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.edit_timing.clicked.connect
        def edit_timing():
            win = Editor(self.task_timing)
            app.list_of_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.edit_balanced.clicked.connect
        def edit_balanced():
            win = Editor(self.task_balanced)
            app.list_of_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.sec_timer.timeout.connect
        def sec_timer_timeout():
            T: float
            # every full second
            if self.task_timing:
                T = time()
                diff = self.task_timing.deadline - T
                rst, weeks = modf(diff / (7 * 24 * 60 * 60))
                rst, days = modf(rst * 7)
                rst, hours = modf(rst * 24)
                rst, minutes = modf(rst * 60)
                rst, seconds = modf(rst * 60)

                self.deadline_weeks.setProperty("intValue", weeks)
                self.deadline_days.setProperty("intValue", days)
                self.deadline_hours.setProperty("intValue", hours)
                self.deadline_minutes.setProperty("intValue", minutes)
                self.deadline_seconds.setProperty("intValue", seconds)

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            T = time()
            if self.task_timing:
                self.frame_timing.setStyleSheet(
                    f"""
        * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
                stop:0 black, 
                stop:1 white);
        background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
                stop:0 {activity_color.get(self.task_timing.primary_activity_id, "black")}, 
                stop:{sin(T * 0.1) * 0.5 + 0.5} {activity_color.get(self.task_timing.secondary_activity_id,
                                                                    activity_color.get(
                                                                        self.task_timing.primary_activity_id, "black"))},
                stop:1 white);
        }}
        """
                )
            else:
                self.frame_timing.setStyleSheet("color: grey")

            if self.task_priority:
                self.frame_priority.setStyleSheet(
                    f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {activity_color.get(self.task_priority.primary_activity_id, "black")},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {activity_color.get(self.task_priority.secondary_activity_id,
                                                                activity_color.get(self.task_priority.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """
                )
            else:
                self.frame_priority.setStyleSheet("color: grey")

            if self.task_balanced:
                self.frame_balanced.setStyleSheet(
                    f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {activity_color.get(self.task_balanced.primary_activity_id, "black")},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {activity_color.get(self.task_balanced.secondary_activity_id,
                                                                activity_color.get(self.task_balanced.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """
                )
            else:
                self.frame_balanced.setStyleSheet("color: grey")

        @self.go_priority.clicked.connect
        def go_priority_clicked():
            self.hide()
            app.win_running = Running(self.task_priority)

        @self.skip_priority.clicked.connect
        def skip_priority_clicked():
            old_task = self.task_priority
            self.priority_tasks.rotate(-1)
            self.task_priority.last_checked = time()
            self.task_priority = self.priority_tasks[0]
            self.task_desc_priority.setText(self.task_priority.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.task_priority.space)

            if old_task == self.task_priority:
                mb = QtWidgets.QMessageBox()
                mb.setText(
                    "Sorry, es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.\nAuf gehts!"
                )
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/fast-forward.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec()

        @self.go_balanced.clicked.connect
        def go_balanced_clicked():
            self.hide()
            app.win_running = Running(self.task_balanced)

        @self.skip_balanced.clicked.connect
        def skip_balanced_clicked():
            now = time()
            self.task_balanced.last_checked = now
            self.balanced_tasks.rotate(-1)
            self.task_balanced = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.task_balanced.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.task_balanced.space)

        @self.go_timing.clicked.connect
        def go_timing_clicked():
            self.hide()
            app.win_running = Running(self.task_timing)

        @self.skip_timing.clicked.connect
        def skip_timing_clicked():
            self.timing_tasks.rotate(-1)
            self.task_timing.last_checked = time()
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space)

        @self.cancel.clicked.connect
        def cancel_clicked_():
            self.hide()
            app.win_main.show()

        @self.done_priority.clicked.connect
        def done_priority_clicked():
            win = Task_Finished(self.task_priority)
            win.exec()

        @self.done_balanced.clicked.connect
        def _done_balanced_clicked():
            win = Task_Finished(self.task_balanced)
            win.exec()

        @self.done_timing.clicked.connect
        def done_timing_clicked():
            win = Task_Finished(self.task_timing)
            win.exec()

    def lets_check_whats_next(self):
        seed((config.coin ^ config.lucky_num) * config.count)
        config.count += 1

        self.groups = defaultdict(lambda: [])

        now = datetime.now()

        for t in considered_tasks():
            check_task_conditions(t, now=now)

        self.tasks = list(
            filter(lambda t: t.considered_open and constraints_met(t.constraints, now), considered_tasks())
        )

        if not self.tasks:
            mb = QtWidgets.QMessageBox()
            mb.setText("Es sind noch keine Aufgaben gestellt aus denen ausgewählt werden könnte.")
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec()
            self.hide()
            return False

        self.set_task_priority()
        self.set_task_balanced()
        self.set_timing_task()
        return True

    def reject(self):
        super().reject()
        app.win_main.show()
        self.sec_timer.stop()
        self.animation_timer.stop()
        for L in app.list_of_task_lists:
            L.timer.start(100)
            L.filter_timer.start(1000)
            L.show()

    def set_task_priority(self):
        self.priority_tasks = prioritize(self.tasks)
        self.task_priority = self.priority_tasks[0]
        self.task_desc_priority.setText(self.task_priority.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.task_priority.space)

    def set_timing_task(self):
        try:
            self.timing_tasks = schedule(self.tasks)
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space)

        except IndexError:
            self.task_desc_timing.setText("nix was präsiert")
            self.taskfont.setItalic(True)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(False)
            self.task_timing = None
            self.deadline = None
            self.deadline_weeks.display("")
            self.deadline_days.display("")
            self.deadline_hours.display("")
            self.deadline_minutes.display("")
            self.deadline_seconds.display("")

        else:
            self.taskfont.setItalic(False)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(True)

        self.task_desc_timing.adjustSize()

    @cached_and_invalidated
    def set_task_balanced(self):
        activity_time_spent = defaultdict(lambda: 0)
        query = submit_sql(
            """
SELECT
    activity_id,
    adjust_time_spent
FROM activities
WHERE activity_id not NULL
"""
        )
        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] = typed(row, 1, int)

        query = submit_sql(
            """
SELECT
    primary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    primary_activity_id;
"""
        )

        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] += typed(row, 1, int)
        query = submit_sql(
            """
SELECT
    secondary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    secondary_activity_id;
"""
        )
        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] += int(typed(row, 1, int) * 0.382)
        activity_time_spent[None] = max(activity_time_spent.values())

        self.balanced_tasks = balance(self.tasks, activity_time_spent)

        self.task_balanced = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.task_balanced.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.task_balanced.space)
        self.task_space_balanced.setText(self.task_balanced.space)
        self.task_space_balanced.setText(self.task_balanced.space)