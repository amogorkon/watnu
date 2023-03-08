class Statistics(QtWidgets.QDialog, ui.statistics.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        query = submit_sql(
            """
select max(id) from tasks
                           """
        )
        ok = QIcon("./extra/feathericons/check.svg")
        nok = QIcon("./extra/feathericons/x.svg")
        query.first()
        self.total_num_tasks.setText(str(typed(query.value, 0, int, default=0)))
        query = submit_sql(
            """
SELECT
    space_id, name
FROM
    spaces
"""
        )
        for i, (space_id, name) in enumerate(
            ((typed(row, 0, int), typed(row, 1, str)) for row in iter_over(query))
        ):
            self.space_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            self.space_stats.setItem(i, 0, item)

            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    space_id == {space_id} AND done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.space_stats.setItem(i, 1, item)
            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    space_id == {space_id} AND NOT done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.space_stats.setItem(i, 2, item)

            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    space_id == {space_id} AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.space_stats.setItem(i, 3, item)

        for i, (level_id, name) in enumerate(
            ((-2, "MUST NOT"), (-1, "SHOULD NOT"), (0, "COULD"), (1, "SHOULD"), (2, "MUST"))
        ):
            self.level_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            self.level_stats.setItem(i, 0, item)
            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.level_stats.setItem(i, 1, item)

            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.level_stats.setItem(i, 2, item)

            inner_query = submit_sql(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed(inner_query.value, 0, int, default=0)))
            self.level_stats.setItem(i, 3, item)

        query = submit_sql(
            """
SELECT
session_id, task_id, start, stop, finished, pause_time
FROM
sessions                           
"""
        )

        for i, (session_id, task_id, start, stop, finished, pause_time) in enumerate(
            (
                typed(row, 0, int),
                typed(row, 1, int),
                typed(row, 2, int),
                typed(row, 3, int),
                typed(row, 4, int),
                typed(row, 5, int),
            )
            for row in iter_over(query)
        ):
            self.session_stats.setRowCount(i + 1)
            inner_query = submit_sql(
                f"""
SELECT
    do
FROM
    tasks
WHERE
    id == {task_id}
"""
            )
            item = QtWidgets.QTableWidgetItem(typed(inner_query.value, 0, str))
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            self.session_stats.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(start)))
            self.session_stats.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(stop)))
            self.session_stats.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem()
            item.setIcon(ok if finished else nok)
            self.session_stats.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(f"{(stop - start) // 60:04}")
            self.session_stats.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(f"{pause_time // 60:04}")
            self.session_stats.setItem(i, 5, item)
