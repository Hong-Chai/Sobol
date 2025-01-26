from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt

import sys

app = QApplication(sys.argv)


class AssaultSettingsWindow(QMainWindow):
    def __init__(self, level_num):
        super().__init__()
        self.setWindowTitle("Assault Settings")
        self.setFixedSize(300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("Configure Assault Settings")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.lethal_checkbox = QCheckBox("Lethal Mode")
        layout.addWidget(self.lethal_checkbox)

        self.flashbang_checkbox = QCheckBox("Use Flashbang")
        self.flashbang_checkbox.setEnabled(level_num >= 2)
        layout.addWidget(self.flashbang_checkbox)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.accept_settings)
        layout.addWidget(self.confirm_button)

        self.lethal_mode = False
        self.use_flashbang = False
        self.settings_accepted = False
        self.start = False

    def accept_settings(self):
        self.start = True
        self.lethal_mode = self.lethal_checkbox.isChecked()
        self.use_flashbang = self.flashbang_checkbox.isChecked()
        self.settings_accepted = True
        self.close()


def get_assault_settings(level_num):
    """Show assault settings window and return the selected options"""
    window = AssaultSettingsWindow(level_num)
    window.show()

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    while not window.settings_accepted and window.isVisible():
        app.processEvents()

    return window.start, window.lethal_mode, window.use_flashbang
