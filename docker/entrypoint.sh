#!/bin/bash
set -e

source /opt/ros/${ROS_DISTRO}/setup.bash

if [ -f "/root/ros2_ws/install/setup.bash" ]; then
    source /root/ros2_ws/install/setup.bash
else
    echo "[entrypoint] Workspace no compilado."
    echo "[entrypoint] Ejecutá:"
    echo "  cd /root/ros2_ws && colcon build --symlink-install"
fi

exec "$@"