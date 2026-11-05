"""Start Gazebo + Nav2 (TurtleBot3) and run the goal runner.

Usage:
  ros2 launch nav_experiments experiment.launch.py headless:=True
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav2_dir = get_package_share_directory("nav2_bringup")
    pkg_dir = get_package_share_directory("nav_experiments")
    headless = LaunchConfiguration("headless")
    scenario = LaunchConfiguration("scenario_file")
    out = LaunchConfiguration("out")

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_dir, "launch", "tb3_simulation_launch.py")),
        launch_arguments={"headless": headless, "use_rviz": LaunchConfiguration("use_rviz"),
                          "use_sim_time": "True"}.items())

    runner = Node(
        package="nav_experiments", executable="goal_runner", output="screen",
        arguments=["--scenario-file", scenario, "--out", out],
        parameters=[{"use_sim_time": True}])

    return LaunchDescription([
        DeclareLaunchArgument("headless", default_value="True"),
        DeclareLaunchArgument("use_rviz", default_value="False"),
        DeclareLaunchArgument("scenario_file",
                              default_value=os.path.join(pkg_dir, "config", "scenarios.yaml")),
        DeclareLaunchArgument("out", default_value="results/run.csv"),
        sim,
        TimerAction(period=20.0, actions=[runner]),   # give Gazebo/Nav2 time to come up
    ])
