FROM osrf/ros:humble-desktop

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-nav2-simple-commander \
      ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-navigation2 \
      python3-pandas python3-pytest python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

ENV TURTLEBOT3_MODEL=waffle
ENV GAZEBO_MODEL_PATH=/opt/ros/humble/share/turtlebot3_gazebo/models

WORKDIR /ws
COPY . src/nav_experiments
RUN . /opt/ros/humble/setup.sh && colcon build --symlink-install

CMD ["bash", "-c", ". /opt/ros/humble/setup.bash && . /ws/install/setup.bash && ros2 launch nav_experiments experiment.launch.py headless:=True out:=/ws/results/run.csv"]
