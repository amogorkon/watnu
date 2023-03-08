class Character(QtWidgets.QDialog, ui.character.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.skills_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.build_skill_table()

    def build_skill_table(self):
        query = submit_sql(
            """
        SELECT skill_id, task_id FROM task_trains_skill;
        """
        )
        if not query:
            return

        self.skills_table.setSortingEnabled(False)

        skills_trained_by = defaultdict(lambda: [])

        for row in iter_over(query):
            skills_trained_by[row(0)].append(row(1))

        for i, skill in enumerate(skills_trained_by):
            query = submit_sql(
                f"""
            SELECT name FROM skills WHERE skill_id=={skill};
            """
            )

            self.skills_table.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(query.value(0))
            self.skills_table.setItem(i, 0, item)
            item.setData(Qt.ItemDataRole.UserRole, skill)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item = QtWidgets.QTableWidgetItem(str(len(skills_trained_by[skill])))
            self.skills_table.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(
                str(sum(Task(x).total_time_spent for x in skills_trained_by[skill]) // (60 * 60))
            )
            self.skills_table.setItem(i, 2, item)

        self.skills_table.setSortingEnabled(True)
        self.update()
