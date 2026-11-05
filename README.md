# ROS 2 Autonomous Navigation Experiments

![CI](https://github.com/Sravan-n-dev/ros2-nav-experiments/actions/workflows/ci.yml/badge.svg)

Repeatable navigation experiments for a simulated TurtleBot3 using ROS 2 Humble, Nav2 and
Gazebo. A Python node sends a list of goals to Nav2, measures what happens (success, time,
distance travelled, path efficiency, recovery behaviours), and writes one CSV row per goal.
An analysis tool then summarises results per scenario.

The point is to treat navigation as something you *measure*: change a parameter or a map,
rerun the same scenarios, and compare numbers instead of eyeballing RViz.

## What is in the repo

| Path | Purpose |
|---|---|
| `nav_experiments/goal_runner.py` | ROS 2 node: runs scenarios through Nav2 (`BasicNavigator`), logs metrics |
| `nav_experiments/metrics.py` | ROS-free helpers: path length from odometry, efficiency, CSV writer |
| `nav_experiments/analyze.py` | Summarises CSVs: success rate, mean time/path/efficiency, recoveries |
| `launch/experiment.launch.py` | Starts Gazebo + Nav2 (`nav2_bringup` TurtleBot3 simulation) and the runner |
| `config/scenarios.yaml` | Initial pose, timeout, goals and repetitions |
| `scripts/record_bag.sh` | Records `/odom /scan /imu /cmd_vel` to a bag for the Robot Telemetry & Data Platform |
| `Dockerfile` | ROS 2 Humble + Nav2 + TurtleBot3 environment, reproducible setup |

## Metrics per goal

`status` (SUCCEEDED / FAILED / CANCELED / TIMEOUT), `duration_s`, `path_length_m`
(integrated from `/odom`), `straight_line_m`, `path_efficiency` (straight / travelled, capped at 1),
`recoveries` (max Nav2 recovery count reported in feedback).

## Run it

With Docker (headless Gazebo):

```bash
docker build -t nav-experiments .
docker run --rm -v "$PWD/results:/ws/results" nav-experiments
python3 -m nav_experiments.analyze results/run.csv      # or: ros2 run nav_experiments analyze results/run.csv
```

Native Ubuntu 22.04 + ROS 2 Humble:

```bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-turtlebot3-gazebo \
                 ros-humble-nav2-simple-commander
export TURTLEBOT3_MODEL=waffle
mkdir -p ws/src && cd ws/src && git clone https://github.com/Sravan-n-dev/ros2-nav-experiments.git nav_experiments
cd .. && colcon build --symlink-install && source install/setup.bash
ros2 launch nav_experiments experiment.launch.py headless:=False use_rviz:=True
```

Before trusting any numbers, open RViz once and check the goal coordinates in
`config/scenarios.yaml` are in free space on your map; adjust if not.

## Tests

`python -m pytest -q` runs 6 unit tests for the ROS-free logic (path length, efficiency, CSV output,
summary statistics). They run in CI. Full simulation runs need the Docker image or a ROS 2 install.

## Using it with the Robot Telemetry & Data Platform

Record a bag during a run with `scripts/record_bag.sh`, then ingest it into
[robot-data-platform](https://github.com/Sravan-n-dev/robot-data-platform) to get topic rates,
time-range queries and automatic data-quality checks on the run.

## Results

*Add your measured results here after running the experiments, for example a table from
`analyze` and one or two observations (what changed success rate or path efficiency).*

## Limitations

- Simulation only (TurtleBot3 in Gazebo). Uses a pre-built map with AMCL localization, not live SLAM.
- Goal coordinates are starting values and may need tuning per map.
- Path length is computed from odometry, which drifts slightly; it is a relative measure, not ground truth.
- The simulation launch/runner code requires ROS 2 Humble; it is not exercised by CI.
