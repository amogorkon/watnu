from PyQt6 import QtWidgets
from PyQt6.QtCore import QItemSelectionModel, Qt
from PyQt6.QtSql import QSqlTableModel

import src.ui as ui


class SkillChooser(QtWidgets.QDialog, ui.choose_skills.Ui_Dialog):
    def __init__(self, editor: "ux.task_editor.Editor", task=None):
        super().__init__()
        self.setupUi(self)
        self.task = task
        self.editor = editor
        model = QSqlTableModel()
        model.setTable("skills")
        model.setSort(1, Qt.SortOrder.AscendingOrder)
        model.select()
        self.listView.setModel(model)
        self.listView.setModelColumn(1)

        if task:
            # holy crap, that was a difficult birth..
            self.listView.selectionModel().clear()
            for index in range(model.rowCount()):
                if model.itemData(model.index(index, 0))[0] in task.skill_ids:
                    self.listView.selectionModel().select(
                        model.index(index, 1),
                        QItemSelectionModel.Select,
                    )

    def accept(self):
        super().accept()
        self.editor.skill_ids = [
            self.listView.model().record(idx.row()).value("skill_id")
            for idx in self.listView.selectedIndexes()
        ]


import src.ux as ux  # noqa: E402
