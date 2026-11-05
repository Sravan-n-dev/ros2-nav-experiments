import csv
import math

import pandas as pd
import pytest

from nav_experiments.analyze import summarize
from nav_experiments.metrics import (CSV_FIELDS, GoalResult, PathLength,
                                     path_efficiency, straight_line, write_results)


def test_path_length_straight_and_ignores_jitter():
    p = PathLength(min_step=0.01)
    for x in [0.0, 0.001, 0.5, 0.502, 1.0]:      # tiny moves are ignored
        p.add(x, 0.0)
    assert p.total == pytest.approx(1.0, abs=0.01)


def test_path_length_l_shape():
    p = PathLength()
    for xy in [(0, 0), (3, 0), (3, 4)]:
        p.add(*xy)
    assert p.total == pytest.approx(7.0)


def test_reset():
    p = PathLength()
    p.add(0, 0)
    p.add(1, 0)
    p.reset()
    assert p.total == 0.0
    p.add(5, 5)
    assert p.total == 0.0


def test_straight_line_and_efficiency():
    assert straight_line((0, 0), (3, 4)) == 5.0
    assert path_efficiency(5.0, 10.0) == 0.5
    assert path_efficiency(5.0, 4.0) == 1.0       # capped at 1
    assert path_efficiency(5.0, 0.0) is None


def _result(status, duration, path, rec, scenario="s1"):
    straight = 4.0
    return GoalResult(scenario, "w", "A", 1, 1.0, 1.0, status, duration, path, straight,
                      path_efficiency(straight, path), rec)


def test_write_results_roundtrip(tmp_path):
    out = tmp_path / "r" / "run.csv"
    write_results(out, [_result("SUCCEEDED", 10.0, 5.0, 0)])
    rows = list(csv.DictReader(out.open()))
    assert list(rows[0].keys()) == CSV_FIELDS
    assert rows[0]["status"] == "SUCCEEDED" and float(rows[0]["duration_s"]) == 10.0


def test_summarize_success_rate_and_means():
    df = pd.DataFrame([
        vars(_result("SUCCEEDED", 10.0, 5.0, 0)),
        vars(_result("SUCCEEDED", 20.0, 8.0, 2)),
        vars(_result("FAILED", 30.0, 3.0, 4)),
        vars(_result("TIMEOUT", 120.0, 1.0, 1)),
    ])
    row = summarize(df).iloc[0]
    assert row["runs"] == 4
    assert row["success_rate"] == 0.5
    assert row["mean_time_s"] == 15.0            # averaged over successes only
    assert row["mean_path_m"] == 6.5
    assert row["total_recoveries"] == 7
    assert math.isclose(row["mean_efficiency"], (0.8 + 0.5) / 2, abs_tol=1e-3)
