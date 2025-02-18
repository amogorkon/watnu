from __future__ import annotations

import numpy as np
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QKeySequence,
    QShortcut,
)

import src.ui as ui
import src.ux as ux
from src.classes import Task


class ConstraintChooser(QtWidgets.QDialog, ui.choose_constraints.Ui_Dialog):
    def __init__(self, editor: ux.task_editor.TaskEditor, task: Task | None = None):
        super().__init__()
        self.setupUi(self)
        self.editor = editor
        self.table.horizontalHeader().setHighlightSections(False)

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)

        for i, (hour, part) in enumerate((hour, part) for hour in range(24) for part in range(12)):
            item = QtWidgets.QTableWidgetItem(f"{hour}: {part * 5:02d}")
            if i % 6 == 0:
                font = QtGui.QFont()
                font.setItalic(True)
                font.setWeight(90)
                if part % 10 == 0:
                    font.setBold(True)
                item.setFont(font)
            self.table.setVerticalHeaderItem(i, item)
        for column, day in enumerate(editor.constraints):
            for row, value in enumerate(day):
                if value:
                    self.table.setCurrentCell(row, column)

        @self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).clicked.connect
        def reset():
            self.table.clearSelection()

        @self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Discard).clicked.connect
        def discard():
            self.editor.constraints = None
            self.close()

    def accept(self):
        super().accept()
        A = np.zeros(2016, int)
        A[[idx.column() * 288 + idx.row() for idx in self.table.selectedIndexes()]] = 1
        self.editor.constraints = A.reshape(7, 288)
