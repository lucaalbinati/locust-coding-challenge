from setuptools import find_packages, setup

setup(
    name="cpu_monitor",
    version="1.0.0",
    author="Luca Albinati",
    author_email="luca.albinati@gmail.com",
    description="A script to monitor CPU usage.",
    url="https://github.com/lucaalbinati/locust-coding-challenge",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "requests",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "cpu_monitor=cpu_monitor.cpu_monitor:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
