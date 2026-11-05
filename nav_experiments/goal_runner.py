"""ROS 2 node: send a list of goals to Nav2 and log per-goal metrics to CSV.

Requires a running Nav2 stack (see launch/experiment.launch.py).
"""
from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import rclpy
import yaml
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from nav_msgs.msg import Odometry

from .metrics import GoalResult, PathLength, path_efficiency, straight_line, write_results


def make_pose(navigator: BasicNavigator, x: float, y: float, yaw: float) -> PoseStamped:
    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def run_goal(navigator: BasicNavigator, odom: dict, pathlen: PathLength, goal: dict,
             timeout_s: float) -> tuple[str, float, int]:
    """Send one goal and block until it ends. Returns (status, duration_s, recoveries)."""
    pathlen.reset()
    navigator.goToPose(make_pose(navigator, goal["x"], goal["y"], goal.get("yaw", 0.0)))
    start = time.monotonic()
    recoveries = 0
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback is not None:
            recoveries = max(recoveries, int(feedback.number_of_recoveries))
        if time.monotonic() - start > timeout_s:
            navigator.cancelTask()
            time.sleep(1.0)
            return "TIMEOUT", time.monotonic() - start, recoveries
    duration = time.monotonic() - start
    result = navigator.getResult()
    status = {TaskResult.SUCCEEDED: "SUCCEEDED", TaskResult.CANCELED: "CANCELED",
              TaskResult.FAILED: "FAILED"}.get(result, "FAILED")
    return status, duration, recoveries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-file", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path("results/run.csv"))
    args, _ = parser.parse_known_args()
    config = yaml.safe_load(args.scenario_file.read_text())

    rclpy.init()
    navigator = BasicNavigator()
    pathlen = PathLength()
    odom: dict = {}

    def on_odom(msg: Odometry) -> None:
        odom["x"], odom["y"] = msg.pose.pose.position.x, msg.pose.pose.position.y
        pathlen.add(odom["x"], odom["y"])

    navigator.create_subscription(Odometry, "/odom", on_odom, 20)

    init = config["initial_pose"]
    navigator.setInitialPose(make_pose(navigator, init["x"], init["y"], init.get("yaw", 0.0)))
    navigator.waitUntilNav2Active()

    results: list[GoalResult] = []
    timeout_s = float(config.get("timeout_s", 120))
    for scenario in config["scenarios"]:
        for rep in range(int(scenario.get("repetitions", 1))):
            for goal in scenario["goals"]:
                start_xy = (odom.get("x", init["x"]), odom.get("y", init["y"]))
                navigator.get_logger().info(
                    f"{scenario['name']} rep {rep + 1}: goal {goal['id']} ({goal['x']}, {goal['y']})")
                status, duration, recoveries = run_goal(navigator, odom, pathlen, goal, timeout_s)
                straight = straight_line(start_xy, (goal["x"], goal["y"]))
                results.append(GoalResult(
                    scenario=scenario["name"], world=config["world"], goal_id=str(goal["id"]),
                    repetition=rep + 1, goal_x=goal["x"], goal_y=goal["y"], status=status,
                    duration_s=round(duration, 3), path_length_m=round(pathlen.total, 3),
                    straight_line_m=round(straight, 3),
                    path_efficiency=path_efficiency(straight, pathlen.total), recoveries=recoveries))
                write_results(args.out, results)     # write after every goal so nothing is lost on a crash
    navigator.get_logger().info(f"done: {len(results)} goals logged to {args.out}")
    navigator.lifecycleShutdown()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
