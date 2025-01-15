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

    gz_launch_path = PathJoinSubstitution([pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])
    gz_model_path = PathJoinSubstitution([pkg_omni_wheel_bot, 'models'])
    xacro_file = os.path.join(get_package_share_directory('omni_wheel_bot'), 'urdf', 'omni_wheel_bot.urdf.xacro')  
    assert os.path.exists(xacro_file), "The omni_wheel_bot.urdf.xacro doesnt exist in "+str(xacro_file)  



    # Some default names
    default_entity_name = 'omni_wheel_bot'
    default_x = '0.0'
    default_y = '0.0'
    default_z = '0.0'


    return LaunchDescription([
        # Argument for the world file
        DeclareLaunchArgument(
            'world',
            default_value='gazebo',
            description='World to load into Gazebo'
        ),

        # Set the world file configuration
        SetLaunchConfiguration(
            name='world_file',
            value=[
                LaunchConfiguration('world'),
                TextSubstitution(text='.world')
            ]
        ),

        # Set the Gazebo resource path
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_model_path),

        # Include the Gazebo launch file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': [
                    PathJoinSubstitution([pkg_omni_wheel_bot, 'worlds', LaunchConfiguration('world_file')])
                ],
                'on_exit_shutdown': 'True'
            }.items(),
        ),

        # For spawning the robot
        Node(
            package="ros_gz_sim",
            executable="create",
            name="ros_gz_create_bot",
            output="screen",
            arguments=[
               "-file",
               xacro_file,
               "-param",
               "robot_description",
               "-name",
               default_entity_name,
               "-allow_renaming",
               "true",
               "-x",
               default_x,
               "-y",
               default_y,
               "-z",
               default_z,
            ]
        )

    ])
