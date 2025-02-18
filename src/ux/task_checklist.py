from PyQt6.QtWidgets import QDialog

import src.ui as ui
from src import app


class CheckList(QDialog, ui.task_checklist.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        app.list_of_task_checklists.append(self)
        app.list_of_windows.append(self)

    def reject(self):
        """
        Reimplemented to remove the current task checklist from the list of task checklists and windows,
        and to raise the previous window in the list of windows.
        """
        super().reject()
        app.list_of_task_checklists.remove(self)
        app.list_of_windows.remove(self)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()


def make_new_and_show_all():
    """
    Creates a new task checklist and shows all.
    """
    win = CheckList()
    for win in app.list_of_task_checklists:
        win.show()
    return win
