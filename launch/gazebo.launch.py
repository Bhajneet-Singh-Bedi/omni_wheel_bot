from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, 
    SetEnvironmentVariable, 
    IncludeLaunchDescription, 
    RegisterEventHandler,
    ExecuteProcess
)
from launch.event_handlers import OnProcessExit
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
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    urdf_file = os.path.join(get_package_share_directory('omni_wheel_bot'), 'urdf', 'omni_wheel_bot.urdf')  
    assert os.path.exists(urdf_file), "The omni_wheel_bot.sdf doesnt exist in "+str(urdf_file)  
    urdf = open(urdf_file).read()



    # Some default names
    default_entity_name = 'omni_wheel_bot'
    default_x = '0.0'
    default_y = '0.0'
    default_z = '0.0'


    env_path = SetEnvironmentVariable( 'GZ_SIM_RESOURCE_PATH', os.path.join(pkg_omni_wheel_bot, 'meshes') )

    DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),
    

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
        ),
        launch_arguments={
                'gz_args': [
                    PathJoinSubstitution([pkg_omni_wheel_bot, 'worlds', 'gazebo.world']),
                ' -r '],
                'on_exit_shutdown': 'True'
            }.items(),
    )


    spawn = Node(
            package="ros_gz_sim",
            executable="create",
            name="ros_gz_create_bot",
            output="screen",
            arguments=[
               "-file", urdf_file,
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
            {'robot_description': urdf}
        ]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='both',
        arguments=[urdf_file],
    )

    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_joint_trajectory_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'velocity_controller'],
        output='screen'
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )
    return LaunchDescription([
        # Launch gazebo environment
        gazebo,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_joint_trajectory_controller],
            )
        ),
        
        robot_state_publisher,
        spawn,
        # Launch Arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),
        bridge,
    ])

    
