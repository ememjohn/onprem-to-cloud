output "vpc_id" {
  description = "VPC Identifier"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs for Application Load Balancer"
  value       = module.networking.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "Private Subnet IDs for EC2 compute"
  value       = module.networking.private_app_subnet_ids
}

output "isolated_db_subnet_ids" {
  description = "Isolated Subnet IDs for Amazon RDS PostgreSQL"
  value       = module.networking.isolated_db_subnet_ids
}

output "db_subnet_group_name" {
  description = "RDS DB Subnet Group Name"
  value       = module.networking.db_subnet_group_name
}

output "alb_security_group_id" {
  description = "ALB Security Group ID"
  value       = module.networking.alb_security_group_id
}

output "app_security_group_id" {
  description = "App Security Group ID"
  value       = module.networking.app_security_group_id
}

output "db_security_group_id" {
  description = "Database Security Group ID"
  value       = module.networking.db_security_group_id
}

output "db_endpoint" {
  description = "RDS PostgreSQL Connection Endpoint"
  value       = module.database.db_endpoint
}

output "db_secret_arn" {
  description = "Secrets Manager ARN for Database Credentials"
  value       = module.database.db_secret_arn
}

output "alb_dns_name" {
  description = "Public DNS Hostname of Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "ec2_private_ip" {
  description = "Private IP of Application Host"
  value       = module.compute.ec2_private_ip
}
