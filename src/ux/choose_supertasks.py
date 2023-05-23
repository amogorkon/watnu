import ui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QItemSelectionModel, Qt
from PyQt6.QtSql import QSqlTableModel


class SuperTaskChooser(QtWidgets.QDialog, ui.choose_skill.Ui_Dialog):
    def __init__(self, editor, task=None):
        super().__init__()
        self.setupUi(self)
        self.task = task
        self.editor = editor
        model = QSqlTableModel()
        model.setTable("tasks")
        model.setSort(1, Qt.SortOrder.AscendingOrder)
        model.select()
        self.listView.setModel(model)
        self.listView.setModelColumn(1)

        if task:
            # holy crap, that was a difficult birth..
            self.listView.selectionModel().clear()
            for index in range(model.rowCount()):
                if model.itemData(model.index(index, 0))[0] in [t.id for t in task.supertasks]:
                    self.listView.selectionModel().select(model.index(index, 1), QItemSelectionModel.Select)

    def accept(self):
        self.editor.supertasks = [
            self.listView.model().record(idx.row()).value("id") for idx in self.listView.selectedIndexes()
        ]
