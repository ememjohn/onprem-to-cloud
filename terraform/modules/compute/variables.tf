variable "project_name" {
  description = "Global project prefix for resource naming"
  type        = string
  default     = "sabay-bank"
}

variable "environment" {
  description = "Deployment environment identifier"
  type        = string
  default     = "dev"
}

variable "vpc_id" {
  description = "VPC Identifier from networking module"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the Application Load Balancer"
  type        = list(string)
}

variable "private_subnet_id" {
  description = "Private subnet ID where the EC2 application instance resides"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security Group ID for the Application Load Balancer"
  type        = string
}

variable "app_security_group_id" {
  description = "Security Group ID for the EC2 compute instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.small"
}
