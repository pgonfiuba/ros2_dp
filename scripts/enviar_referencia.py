#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

def main():
    rclpy.init()

    node = Node("trajectory_sender")
    pub = node.create_publisher(JointTrajectory, '/position_controller/joint_trajectory', 10)

    try:
        joint1 = float(input("Ingrese posición para joint1 [rad]: "))
        joint2 = float(input("Ingrese posición para joint2 [rad]: "))

        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['joint1', 'joint2']

        point = JointTrajectoryPoint()
        point.positions = [joint1, joint2]
        point.time_from_start.sec = 1  # 1 segundo

        traj_msg.points.append(point)

        pub.publish(traj_msg)
        node.get_logger().info(f'Enviada trayectoria: joint1={joint1:.3f}, joint2={joint2:.3f}')

        # Espera un poquito para asegurarse de que se publique antes de cerrar
        rclpy.spin_once(node, timeout_sec=0.5)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

