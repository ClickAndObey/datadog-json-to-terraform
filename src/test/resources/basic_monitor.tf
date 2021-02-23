resource "datadog_monitor" "basic_datadog_metric_count_monitor" {
  name = "Basic Datadog Metric Count: 2"
  type = "query alert"
  message = "Some Message about how to\n\n handle it."
  query = "some query"
  escalation_message = "escalation\n\n message"

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
}