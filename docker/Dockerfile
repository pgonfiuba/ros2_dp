# syntax=docker/dockerfile:1
ARG ROS_DISTRO=jazzy
FROM osrf/ros:${ROS_DISTRO}-desktop-full AS base
ENV ROS_DISTRO=${ROS_DISTRO}
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Herramientas del sistema
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  tmux \
  git \
  vim \
  nano \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-pip \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Paquetes ROS
RUN apt-get update && apt-get install -y \
  # Gazebo + bridge
  ros-${ROS_DISTRO}-gz-sim-vendor \
  ros-${ROS_DISTRO}-ros-gz \
  ros-${ROS_DISTRO}-ros-gz-bridge \
  ros-${ROS_DISTRO}-gz-ros2-control \
  # ROS2 Control
  ros-${ROS_DISTRO}-ros2-control \
  ros-${ROS_DISTRO}-ros2-controllers \
  ros-${ROS_DISTRO}-controller-manager \
  ros-${ROS_DISTRO}-joint-state-broadcaster \
  ros-${ROS_DISTRO}-joint-trajectory-controller \
  ros-${ROS_DISTRO}-diff-drive-controller \
  # MoveIt
  ros-${ROS_DISTRO}-moveit \
  ros-${ROS_DISTRO}-moveit-ros-planning-interface \
  ros-${ROS_DISTRO}-moveit-visual-tools \
  # Herramientas para clases
  ros-${ROS_DISTRO}-plotjuggler-ros \
  ros-${ROS_DISTRO}-teleop-twist-keyboard \
  ros-${ROS_DISTRO}-xacro \
  ros-${ROS_DISTRO}-joint-state-publisher-gui \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Workspace vacío — el código llega por volumen en runtime
RUN mkdir -p /root/ros2_ws/src
WORKDIR /root/ros2_ws

# Source automático
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc && \
    echo "[[ -f /root/ros2_ws/install/setup.bash ]] && source /root/ros2_ws/install/setup.bash" >> ~/.bashrc

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]