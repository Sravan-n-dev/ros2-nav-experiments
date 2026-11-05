#!/usr/bin/env bash
# Record the topics used by the Robot Telemetry & Data Platform while an experiment runs.
# Ingest the result with:  POST /runs/ingest {"path": "<bag folder name>"}
set -euo pipefail
OUT=${1:-bags/nav_run_$(date +%Y%m%d_%H%M%S)}
ros2 bag record -o "$OUT" /odom /scan /imu /cmd_vel
