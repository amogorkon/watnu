from PyQt6 import QtWidgets

from src import db


class SkillEditor(QtWidgets.QDialog):
    def __init__(self, skill_name: str):
        super().__init__()
        self.skill_name = skill_name
        self.setWindowTitle(f"Skill bearbeiten: {self.skill_name}")
        self.setModal(True)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.name_label = QtWidgets.QLabel("Name:")
        self.name_edit = QtWidgets.QLineEdit(self.skill_name)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_skill)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def save_skill(self):
        self.accept()

    def accept(self):
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.skill_name:
            try:
                db.execute(
                    """
                    UPDATE skills
                    SET name = ?
                    WHERE name = ?
                    """,
                    (new_name, self.skill_name),
                )
                db.commit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update skill: {e}")
                return
        super().accept()
