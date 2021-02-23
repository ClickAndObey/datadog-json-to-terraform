"""
Module used to test out the monitor module for converting monitor json into monitor terraform.
"""

import pytest

from unittest import TestCase

from clickandobey.dd2tf.monitor import Monitor


@pytest.mark.unit
@pytest.mark.Monitor
class MonitorTest(TestCase):
    """
    Class used to test converting a monitor in json to a monitor in terraform.
    """

    __BASIC_MONITOR_IN_TERRAFORM = """resource "datadog_monitor" "basic_datadog_metric_count_monitor" {
  name = "Basic Datadog Metric Count: 2"
  type = "query alert"
  message = "Some Message about how to\\n\\n handle it."
  query = "some query"
  escalation_message = "escalation\\n\\n message"

  thresholds {
    critical = 2
    critical_recovery = 3
    warning = 3
    warning_recovery = 4
  }

  tags = [
    "tag:1",
    "tag:2"
  ]

  notify_audit = false
  locked = true
  renotify_interval = 0
  no_data_timeframe = 2
  include_tags = true
  new_host_delay = 300
  require_full_window = true
  notify_no_data = false
}"""

    __BASIC_MONITOR_JSON = {
        "name": "Basic Datadog Metric Count: 2",
        "type": "query alert",
        "query": "some query",
        "message": "Some Message about how to\n\n handle it.",
        "tags": [
            "tag:1",
            "tag:2"
        ],
        "options": {
            "notify_audit": False,
            "locked": True,
            "silenced": {},
            "include_tags": True,
            "renotify_interval": 0,
            "thresholds": {
                "critical": 2,
                "warning": 3,
                "warning_recovery": 4,
                "critical_recovery": 3
            },
            "escalation_message": "escalation\n\n message",
            "no_data_timeframe": 2,
            "new_host_delay": 300,
            "require_full_window": True,
            "notify_no_data": False
        }
    }

    def test_basic_monitor_json_to_terraform(self):
        """
        Test to ensure we can take a simple monitor from json to terraform.
        """
        monitor = Monitor(self.__BASIC_MONITOR_JSON)
        self.assertEqual(
            monitor.to_terraform(),
            self.__BASIC_MONITOR_IN_TERRAFORM
        )
