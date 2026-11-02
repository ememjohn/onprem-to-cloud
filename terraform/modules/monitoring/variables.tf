variable "project_name" {
  description = "Global project prefix"
  type        = string
  default     = "sabay-bank"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the Application Load Balancer for CloudWatch metrics"
  type        = string
}

variable "target_group_arn_suffix" {
  description = "ARN suffix of the Target Group for CloudWatch metrics"
  type        = string
}

variable "db_instance_id" {
  description = "Identifier of the RDS instance for CloudWatch metrics"
  type        = string
}
