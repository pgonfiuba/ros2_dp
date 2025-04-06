#!/usr/bin/env python3
import sys
import subprocess
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

CONTROLLER_NAME = "position_controller"

def strip_ansi_codes(s):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', s)

def get_controller_state():
    try:
        result = subprocess.run(
            ["ros2", "control", "list_controllers"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        for line in result.stdout.splitlines():
            clean_line = strip_ansi_codes(line)
            parts = clean_line.strip().split()
            if len(parts) >= 3 and parts[0] == CONTROLLER_NAME:
                return parts[2]  # "active" o "inactive"
    except subprocess.CalledProcessError:
        return "error"
    return "unknown"

class ControllerToggle(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROS 2 Controller Toggle")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.toggle_button = QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_controller)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.status_label)

        # Obtener el estado actual al arrancar
        current_state = get_controller_state()
        is_active = current_state == "active"
        self.toggle_button.setChecked(is_active)
        self.status_label.setText(f"Estado actual: {current_state}")
        self.update_button_style(is_active)

        # Si querés que lo active automáticamente si está apagado, descomentá esto:
        # if not is_active:
        #     self.toggle_controller(True)

    def toggle_controller(self, checked):
        state = "active" if checked else "inactive"
        try:
            subprocess.run(
                ["ros2", "control", "set_controller_state", CONTROLLER_NAME, state],
                check=True
            )
            self.status_label.setText(f"Estado actual: {state}")
            self.update_button_style(checked)
        except subprocess.CalledProcessError:
            self.status_label.setText(f"⚠️ Error al cambiar a '{state}'")

    def update_button_style(self, is_active):
        if is_active:
            self.toggle_button.setText("Desactivar controlador")
            self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            self.toggle_button.setText("Activar controlador")
            self.toggle_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControllerToggle()
    window.show()
    sys.exit(app.exec_())

