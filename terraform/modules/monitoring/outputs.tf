output "log_group_name" {
  description = "Name of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "alb_5xx_alarm_name" {
  description = "Name of the ALB 5XX error alarm"
  value       = aws_cloudwatch_metric_alarm.alb_5xx.alarm_name
}

output "rds_connections_alarm_name" {
  description = "Name of the RDS database connections alarm"
  value       = aws_cloudwatch_metric_alarm.rds_dropped_connections.alarm_name
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alarm notifications"
  value       = aws_sns_topic.alerts.arn
}
