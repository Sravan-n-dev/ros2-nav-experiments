import os
from glob import glob

from setuptools import find_packages, setup

package_name = "nav_experiments"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Sravan Kumar",
    maintainer_email="sravannarepalem2594@gmail.com",
    description="Repeatable Nav2 navigation experiments with metrics logging",
    license="MIT",
    entry_points={
        "console_scripts": [
            "goal_runner = nav_experiments.goal_runner:main",
            "analyze = nav_experiments.analyze:main",
        ],
    },
)
