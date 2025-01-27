#!/usr/bin/env python3

"""
cpu_monitor.py: A script to monitor CPU usage and interact with the locust-coding-challenge API.

Features:
1. Authenticates with the API and obtains an access token.
2. Creates a new TestRun.
3. Measures CPU usage at regular intervals.
4. Sends CPU usage data to the API.
5. Displays current CPU usage.
6. Notifies the user if CPU usage exceeds a threshold.
7. Reports total test duration and time above threshold upon termination.
"""

import argparse
import logging
import signal
import sys
import time
from datetime import datetime

import psutil
import requests
from tabulate import tabulate

logging.basicConfig(
    filename="cpu_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

DEFAULT_API_URL = "http://localhost:8888"
DEFAULT_INTERVAL = 5.0
DEFAULT_THRESHOLD = 75.0


class CPUMonitor:
    def __init__(self, api_url, username, password, name, interval, threshold):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.name = name
        self.interval = interval
        self.threshold = threshold
        self.access_token = None
        self.test_run_id = None
        self.start_time = None
        self.total_above_threshold = 0.0
        self.above_threshold_start = None
        self.running = True

    def authenticate(self) -> str:
        """
        Authenticate with the API and obtain an access token.

        Returns:
            access_token (str): JWT access token.
        """
        login_endpoint = f"{self.api_url}/login"
        payload = {"username": self.username, "password": self.password}

        try:
            response = requests.post(login_endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if not access_token:
                print("Error: access_token not found in the login response.")
                sys.exit(1)

            print(f"Authenticated as {data.get('full_name')}.")
            self.access_token = access_token
            return access_token
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            sys.exit(1)

    def create_test_run(self) -> int:
        """
        Create a new TestRun via the API.

        Args:
            api_url (str): Base URL of the API.
            access_token (str): JWT access token.
            name (str): Optional name for the TestRun.

        Returns:
            test_run_id (int): ID of the created TestRun.
        """
        test_runs_endpoint = f"{self.api_url}/test_runs"
        print(self.access_token)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"name": self.name if self.name else f"TestRun_{int(time.time())}"}

        try:
            response = requests.post(test_runs_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            test_run_id = data.get("id")
            test_run_name = data.get("name")
            if not test_run_id:
                print("Error: TestRun ID not found in the response.")
                sys.exit(1)
            print(f"Created TestRun '{test_run_name}' with ID: {test_run_id}")
            self.test_run_id = test_run_id
            return test_run_id
        except requests.exceptions.RequestException as e:
            print(f"Failed to create TestRun: {e}")
            sys.exit(1)

    def send_cpu_usage(self, usage_percent: float):
        """
        Send CPU usage data to the API.

        Args:
            api_url (str): Base URL of the API.
            access_token (str): JWT access token.
            test_run_id (int): ID of the TestRun.
            usage_percent (float): Current CPU usage percentage.
        """
        cpu_usage_endpoint = f"{self.api_url}/test_runs/{self.test_run_id}/cpu_usage"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"usage_percent": usage_percent}

        try:
            response = requests.post(cpu_usage_endpoint, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send CPU usage data: {e}")

    def end_test_run(self):
        """Mark the TestRun as ended."""
        end_endpoint = f"{self.api_url}/test_runs/{self.test_run_id}/end"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.put(end_endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"TestRun ended at {data.get('end_time')}.")
            logging.info(f"TestRun ended at {data.get('end_time')}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to end TestRun: {e}")
            print(f"Failed to end TestRun: {e}")

    def report(self):
        """Print the test run report."""
        print("\n\n--- Test Run Report ---")
        report_data = [
            ["Total Test Duration (seconds)", f"{self.total_duration:.2f}"],
            [
                f"Total Time CPU > {self.threshold}%",
                f"{self.total_above_threshold:.2f}",
            ],
        ]
        print(tabulate(report_data, headers=["Metric", "Value"], tablefmt="github"))
        print("-----------------------\n")
        logging.info("Test Run Report:")
        logging.info(f"Total Test Duration: {self.total_duration:.2f} seconds")
        logging.info(
            f"Total Time CPU > {self.threshold}%: {self.total_above_threshold:.2f} seconds"
        )

    def signal_handler(self, sig, frame):
        """Handle termination signals to gracefully stop the monitoring."""
        if not self.running:
            # Prevent multiple invocations
            return

        self.running = False
        current_time = datetime.now()
        total_time = (current_time - self.start_time).total_seconds()

        if self.above_threshold_start:
            duration = (current_time - self.above_threshold_start).total_seconds()
            self.total_above_threshold += duration

        self.end_test_run()

        self.total_duration = total_time
        self.report()
        sys.exit(0)

    def run(self):
        """Run the CPU monitoring."""
        # Register the signal handler for graceful termination
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.authenticate()
        self.create_test_run()
        self.start_time = datetime.now()
        print("\nStarting CPU monitoring. Press Ctrl+C to stop.\n")
        logging.info("Starting CPU monitoring.")

        try:
            while self.running:
                current_time = datetime.now()
                usage_percent = psutil.cpu_percent(interval=None)  # Non-blocking

                # Send CPU usage data to the API
                self.send_cpu_usage(usage_percent)

                # Display current CPU usage
                print(
                    f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] CPU Usage: {usage_percent:.2f}%"
                )

                # Check against threshold
                if usage_percent > self.threshold:
                    if not self.above_threshold_start:
                        self.above_threshold_start = datetime.now()
                        print(f"⚠️  CPU usage exceeded {self.threshold}%!")
                        logging.warning(f"CPU usage exceeded {self.threshold}%!")
                else:
                    if self.above_threshold_start:
                        duration = (
                            current_time - self.above_threshold_start
                        ).total_seconds()
                        self.total_above_threshold += duration
                        self.above_threshold_start = None

                # Wait for the next interval
                time.sleep(self.interval)

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            self.signal_handler(None, None)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="CPU Usage Monitoring Script")
    parser.add_argument(
        "--api-url",
        type=str,
        default=DEFAULT_API_URL,
        help=f"Base API URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username for API authentication",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for API authentication",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of test the run.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help=f"Interval in seconds between CPU usage measurements (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=75.0,
        help=f"CPU usage threshold percentage for notifications (default: {DEFAULT_THRESHOLD})",
    )
    return parser.parse_args()


def main():
    """Main function to execute the CPU monitoring."""
    args = parse_arguments()
    monitor = CPUMonitor(
        api_url=args.api_url,
        username=args.username,
        password=args.password,
        name=args.name,
        interval=args.interval,
        threshold=args.threshold,
    )
    monitor.run()


if __name__ == "__main__":
    main()
