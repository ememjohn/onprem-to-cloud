variable "aws_region" {
  description = "Target AWS Region for deployment"
  type        = string
  default     = "eu-north-1"
}

variable "environment" {
  description = "Deployment environment identifier"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Global project prefix for resource naming"
  type        = string
  default     = "sabay-bank"
}

variable "vpc_cidr" {
  description = "Base CIDR allocation for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "alert_email" {
  description = "Email recipient for CloudWatch alarm notifications"
  type        = string
  default     = "officialememjohn@gmail.com"
}
