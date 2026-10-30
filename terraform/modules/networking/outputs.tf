output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public ingress subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "IDs of the private application compute subnets"
  value       = aws_subnet.private_app[*].id
}

output "isolated_db_subnet_ids" {
  description = "IDs of the isolated database persistence subnets"
  value       = aws_subnet.isolated_db[*].id
}

output "db_subnet_group_name" {
  description = "Name of the RDS DB Subnet Group"
  value       = aws_db_subnet_group.rds.name
}

output "alb_security_group_id" {
  description = "ID of the Application Load Balancer Security Group"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the Application Compute Security Group"
  value       = aws_security_group.app.id
}

output "db_security_group_id" {
  description = "ID of the Database Security Group"
  value       = aws_security_group.db.id
}
