output "ec2_instance_id" {
  description = "Identifier of the EC2 application instance"
  value       = aws_instance.app_host.id
}

output "ec2_private_ip" {
  description = "Private IP address of the EC2 application instance"
  value       = aws_instance.app_host.private_ip
}

output "alb_dns_name" {
  description = "Public DNS hostname of the Application Load Balancer"
  value       = aws_lb.external.dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.external.arn
}

output "target_group_arn" {
  description = "ARN of the application Target Group"
  value       = aws_lb_target_group.app_tg.arn
}
