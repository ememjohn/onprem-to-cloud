output "db_instance_id" {
  description = "Identifier of the RDS instance"
  value       = aws_db_instance.postgres.id
}

output "db_endpoint" {
  description = "Connection endpoint address of the RDS instance"
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "Port number on which RDS accepts connections"
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "Default database name"
  value       = aws_db_instance.postgres.db_name
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret storing database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}
