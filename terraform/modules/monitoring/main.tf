# 1. CloudWatch Log Group for Application Core Logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ec2/${var.project_name}-${var.environment}-core"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-log-group"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 2. Metric Alarm: Application Load Balancer 5XX Target Errors
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.project_name}-${var.environment}-high-5xx-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Triggered when backend application targets return HTTP 5XX server errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.target_group_arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-5xx-alarm"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 3. Metric Alarm: Amazon RDS Zero Active Database Connections
resource "aws_cloudwatch_metric_alarm" "rds_no_connections" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-zero-connections"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Minimum"
  threshold           = 1
  alarm_description   = "Triggered when active PostgreSQL database connections drop to zero"
  treat_missing_data  = "breaching"

  dimensions = {
    DBInstanceIdentifier = var.db_instance_id
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-zero-conn-alarm"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
