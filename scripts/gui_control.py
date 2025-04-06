#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINT_NAMES = ['joint1', 'joint2']
LIMIT_MIN = -3.14
LIMIT_MAX = 3.14

class JointControllerGUI(Node):
    def __init__(self):
        super().__init__('joint_controller_gui')
        self.publisher_ = self.create_publisher(JointTrajectory, '/position_controller/joint_trajectory', 10)
        self.init_gui()

    def init_gui(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle('Referencias del Control')

        layout = QVBoxLayout()

        self.sliders = {}
        self.text_inputs = {}

        for joint in JOINT_NAMES:
            joint_layout = QHBoxLayout()

            label = QLabel(joint)
            joint_layout.addWidget(label)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(1000)
            slider.setValue(500)
            joint_layout.addWidget(slider)

            input_box = QLineEdit('0.00')
            input_box.setFixedWidth(60)
            joint_layout.addWidget(input_box)

            self.sliders[joint] = slider
            self.text_inputs[joint] = input_box

            # Cuando cambia el slider, actualiza el input_box
            slider.valueChanged.connect(lambda val, j=joint: self.update_input_from_slider(j))

            # Cuando se edita el texto, actualiza el slider
            input_box.editingFinished.connect(lambda j=joint: self.update_slider_from_input(j))

            layout.addLayout(joint_layout)

        send_button = QPushButton('Enviar referencia')
        send_button.clicked.connect(self.send_trajectory)
        layout.addWidget(send_button)

        self.window.setLayout(layout)
        self.window.show()
        self.app.exec_()

    def update_input_from_slider(self, joint):
        slider = self.sliders[joint]
        value = self.slider_to_position(slider.value())
        self.text_inputs[joint].setText(f'{value:.2f}')

    def update_slider_from_input(self, joint):
        try:
            text = self.text_inputs[joint].text()
            value = float(text)
            value = max(min(value, LIMIT_MAX), LIMIT_MIN)
            slider_val = self.position_to_slider(value)
            self.sliders[joint].setValue(slider_val)
        except ValueError:
            pass  # Si el usuario escribió algo inválido, lo ignoramos

    def slider_to_position(self, slider_value):
        return LIMIT_MIN + (LIMIT_MAX - LIMIT_MIN) * slider_value / 1000.0

    def position_to_slider(self, position):
        return int(1000.0 * (position - LIMIT_MIN) / (LIMIT_MAX - LIMIT_MIN))

    def send_trajectory(self):
        msg = JointTrajectory()
        msg.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = [self.slider_to_position(self.sliders[j].value()) for j in JOINT_NAMES]
        point.time_from_start.sec = 1
        point.time_from_start.nanosec = 0
        msg.points.append(point)
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    controller = JointControllerGUI()
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

