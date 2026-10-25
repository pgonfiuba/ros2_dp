# Copyright 2025 pgonzal@fi.uba.ar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Argumento del tiempo simulado
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    # Defino la ubicación de los modelos (por ejemplo un escritorio que quiera poner en el .world de gazebo)
    gazebo_models_path = 'models'
    pkg_share_gazebo = FindPackageShare('dp').find('dp')    
    gazebo_models_path = os.path.join(pkg_share_gazebo, gazebo_models_path)
    
    # Si la variable ya existe, la extendemos; si no, la creamos
    set_env_vars_resources = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        gazebo_models_path
    )
    print(f"GZ_SIM_RESOURCE_PATH set to: {gazebo_models_path}")


    # Obtener URDF via xacro
    robot_description_content = Command(
        [
            FindExecutable(name='xacro'),
            ' ',
            PathJoinSubstitution(
                [FindPackageShare('dp'),
                 'urdf', LaunchConfiguration('xacro_file')]
            ),
        ]
    )
    
    # En caso de tener el URDF en vez del xacro es más simple pero menos funcional
    #urdf_path = os.path.join(
    #    FindPackageShare('dp').find('dp'),
    #    'urdf', 'double_pendulum.urdf'
    #)

    # Leer el URDF como string
    #with open(urdf_path, 'r') as urdf_file:
    #    robot_description_content = urdf_file.read()

    robot_description = {'robot_description': robot_description_content}
    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare('dp'),
            'config',
            'ros2_controllers.yaml',
        ]
    )    
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description',
                    '-name', 'double_pendulum', '-allow_renaming', 'true'
                    '-x', '0.0',      # Coordenada X
                    '-y', '0.0',      # Coordenada Y
                    '-z', '0.55'     # Coordenada Z (altura del escritorio)
                    ],

    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    # Este es un típico control de lazo cerrado que toma referencias de posición y entrega esfuerzos a generar    
    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'position_controller',
            '--param-file',
            robot_controllers
            ],
        condition=IfCondition(LaunchConfiguration('closed_loop'))
    )
    
    # Con un "controlador de esfuerzos" en realidad puedo aplicar directamente torque en los ejes
    # No hay tal cosa como un control de lazo cerrado
    effort_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'effort_controller',
            '--param-file',
            robot_controllers
            ],
        condition=UnlessCondition(LaunchConfiguration('closed_loop'))
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=['-d', os.path.join(get_package_share_directory('dp'), 'config', 'display.rviz')]
    )
    
    gui_effort_reference_node = Node(
        package='dp',
        executable='gui_set_torque.py',
        name='gui_set_torque',
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('closed_loop'))
    )

    gui_joint_reference_node = Node(
        package='dp',
        executable='gui_control.py',
        name='gui_control',
        output='screen',
        condition=IfCondition(LaunchConfiguration('closed_loop'))
    )

    return LaunchDescription([
        # Argumentos de lanzamiento
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='True para usar un clock simulado'),
        DeclareLaunchArgument(
            'xacro_file',
            default_value='dp_base.xacro',
            description='Archivo de definición del robot'
        ),
        # Argumento para definir el tipo de control
        DeclareLaunchArgument(
            'closed_loop',
            default_value='true',  # Valor por defecto
            description='Tipo de control: true (posición) o false (esfuerzo ... open_loop)'
        ),
         # Declarar el argumento del mundo con un valor por defecto
        DeclareLaunchArgument(
            'world_name',
            default_value='dp_mundo_vacio.world',
            description='Nombre del archivo del mundo para Gazebo'
        ),

        set_env_vars_resources, # Setea las variables de entorno para los modelos de gazebo
    
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [PathJoinSubstitution([
                    FindPackageShare('ros_gz_sim'),
                    'launch',
                    'gz_sim.launch.py'
                ])]
            ),
            launch_arguments=[(
                'gz_args',
                ['-r -v 1 ', PathJoinSubstitution([
                    FindPackageShare('dp'),
                    'worlds',
                    LaunchConfiguration('world_name')
                ])]
            )]
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        #RegisterEventHandler(
        #    event_handler=OnProcessExit(
        #        target_action=joint_state_broadcaster_spawner,
        #        on_exit=[joint_trajectory_controller_spawner],
        #    )
        #),
        joint_trajectory_controller_spawner,
        effort_controller_spawner,
        bridge,
        node_robot_state_publisher,
        gz_spawn_entity,
        rviz_node,
        gui_joint_reference_node,
        gui_effort_reference_node,
    ])    
