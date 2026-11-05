"""ROS-free metric helpers so they can be unit tested without a ROS install."""
from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass, fields
from pathlib import Path


class PathLength:
    """Accumulates travelled distance from a stream of (x, y) odometry samples.

    Samples closer than `min_step` are ignored to avoid counting sensor noise
    while the robot is standing still.
    """

    def __init__(self, min_step: float = 0.01):
        self.min_step = min_step
        self.total = 0.0
        self._last: tuple[float, float] | None = None

    def add(self, x: float, y: float) -> None:
        if self._last is not None:
            step = math.hypot(x - self._last[0], y - self._last[1])
            if step < self.min_step:
                return
            self.total += step
        self._last = (x, y)

    def reset(self) -> None:
        self.total = 0.0
        self._last = None


def straight_line(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def path_efficiency(straight: float, travelled: float) -> float | None:
    """Straight-line distance divided by distance travelled (1.0 = perfect)."""
    if travelled <= 0:
        return None
    return min(straight / travelled, 1.0)


@dataclass
class GoalResult:
    scenario: str
    world: str
    goal_id: str
    repetition: int
    goal_x: float
    goal_y: float
    status: str                 # SUCCEEDED | FAILED | CANCELED | TIMEOUT
    duration_s: float
    path_length_m: float
    straight_line_m: float
    path_efficiency: float | None
    recoveries: int


CSV_FIELDS = [f.name for f in fields(GoalResult)]


def write_results(path: Path, results: list[GoalResult]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
