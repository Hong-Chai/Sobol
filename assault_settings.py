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
from PyQt6 import uic

import sys

app = QApplication(sys.argv)


class AssaultSettingsWindow(QWidget):
    def __init__(self, level_num, frag_cnt, scout_cnt, rooms_ok_cnt, enem):
        super().__init__()
        self.setWindowTitle("Assault Settings")
        self.setFixedSize(690, 300)

        # central_widget = QWidget()
        # self.setCentralWidget(self)
        uic.loadUi("widget.ui", self)

        self.level_num = level_num
        self.frag_cnt = frag_cnt
        self.scout_cnt = scout_cnt
        self.rooms_ok_cnt = rooms_ok_cnt
        self.settings_accepted = False
        self.bonus = False
        self.chance = 0
        self.enem = enem

        self.exit_but.clicked.connect(self.exit)
        self.start_but.clicked.connect(self.accept_settings)
        self.scout_but.clicked.connect(self.scout_f)

        if level_num < 3 or scout_cnt == 0:
            self.scout_cnt = 0
            self.scout_but.setEnabled(0)
            self.scout_but.setStyleSheet("background-color: #8a8a8a")
        self.scout_cnt_l.setText(f"Осталось {str(self.scout_cnt)} разведок")

        if level_num < 2:
            self.m1.setText("НЕДОСТУПНО")
            self.m2.setText("НЕДОСТУПНО")
        else:
            if rooms_ok_cnt >= 2:
                self.m1.setText("ДОСТУПНО")
                self.chance += 10
            else:
                self.m1.setText(f"Прогресс {rooms_ok_cnt}/2")
            if rooms_ok_cnt >= 4:
                self.m2.setText("ДОСТУПНО")
                self.chance += 20
            else:
                self.m2.setText(f"Прогресс {rooms_ok_cnt}/4")

        if level_num < 4 or frag_cnt == 0:
            self.frag_box.setEnabled(0)
            self.frag_box.setStyleSheet("background-color: #8a8a8a")
            self.frag_box.setText("НЕДОСТУПНО")
        else:
            self.frag_box.setText(f"Осталось {str(self.frag_cnt)} FRAG")

    def accept_settings(self):
        self.chance += 100
        self.bonus = self.lethal_box.isChecked()
        if self.bonus:
            self.bonus = 100
            self.chance -= 20
        self.use_frag = self.frag_box.isChecked()
        if self.use_frag:
            self.chance += 30
            self.frag_cnt -= 1
        self.chance -= self.enem * 10
        self.settings_accepted = True
        self.close()

    def scout_f(self):
        self.scout_cnt -= 1
        self.scout_cnt_l.setText(f"Осталось {str(self.scout_cnt)} разведок")
        self.scout_res.setText(f"РЕЗУЛЬТАТ: {self.enem} врагов")
        self.scout_but.setEnabled(0)
        self.scout_but.setStyleSheet("background-color: #8a8a8a")

    def exit(self):
        self.chance = 0
        self.close()


def get_assault_settings(level_num, frag_cnt, scout_cnt, rooms_ok_cnt, enem):
    """Show assault settings window and return the selected options"""
    window = AssaultSettingsWindow(level_num, frag_cnt, scout_cnt, rooms_ok_cnt, enem)
    window.show()

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    while not window.settings_accepted and window.isVisible():
        app.processEvents()

    if not window.settings_accepted:
        window.chance = 0

    return (
        window.chance,
        window.bonus,
        window.frag_cnt,
        window.scout_cnt,
    )
