variable "project_name" {
  description = "Project identifier for resource tagging"
  type        = string
  default     = "sabay-bank"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "db_subnet_group_name" {
  description = "Name of the RDS DB Subnet Group from networking module"
  type        = string
}

variable "db_security_group_id" {
  description = "Security Group ID allowing access to the database"
  type        = string
}

variable "db_name" {
  description = "Name of the default PostgreSQL database"
  type        = string
  default     = "orders_db"
}

variable "db_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  default     = "dbadmin"
}

variable "allocated_storage" {
  description = "Allocated storage size in gigabytes"
  type        = number
  default     = 20
}

variable "instance_class" {
  description = "Database compute instance type"
  type        = string
  default     = "db.t4g.micro"
}
