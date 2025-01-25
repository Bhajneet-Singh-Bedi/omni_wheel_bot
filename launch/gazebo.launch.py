from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, 
    SetEnvironmentVariable, 
    IncludeLaunchDescription, 
    SetLaunchConfiguration,
    ExecuteProcess
)
from launch.substitutions import (
    PathJoinSubstitution, 
    LaunchConfiguration, 
    TextSubstitution
)
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
import xacro


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_omni_wheel_bot = get_package_share_directory('omni_wheel_bot')

    xacro_file = os.path.join(get_package_share_directory('omni_wheel_bot'), 'urdf', 'omni_wheel_bot.urdf.xacro')  
    assert os.path.exists(xacro_file), "The omni_wheel_bot.urdf.xacro doesnt exist in "+str(xacro_file)  



    # Some default names
    default_entity_name = 'omni_wheel_bot'
    default_x = '0.0'
    default_y = '0.0'
    default_z = '0.0'

    rviz_launch_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Open RViz.'
    )


    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
        ),
        launch_arguments={
                'gz_args': [
                    PathJoinSubstitution([pkg_omni_wheel_bot, 'worlds', 'gazebo.world'])
                ],
                'on_exit_shutdown': 'True'
            }.items(),
    )

    spawn = Node(
            package="ros_gz_sim",
            executable="create",
            name="ros_gz_create_bot",
            output="screen",
            arguments=[
               "-file", xacro_file,
               "-param", "robot_description",
               "-name", default_entity_name,
               "-allow_renaming", "true",
               "-x", default_x,
               "-y", default_y,
               "-z", default_z
            ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': xacro.process_file(xacro_file).toxml()}
        ]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'source_list': ['joint_state_publisher']}
        ]
    )
    return LaunchDescription([
        rviz_launch_arg,
        gazebo,
        spawn,
        robot_state_publisher,
        joint_state_publisher
    ])

    
