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

output "alb_arn_suffix" {
  description = "ARN Suffix of the Application Load Balancer"
  value       = aws_lb.external.arn_suffix
}

output "target_group_arn_suffix" {
  description = "ARN Suffix of the Target Group"
  value       = aws_lb_target_group.app_tg.arn_suffix
}

output "acm_validation_records" {
  description = "DNS validation records for ACM certificate"
  value = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
}

output "acm_certificate_arn" {
  description = "ARN of the issued ACM certificate"
  value       = aws_acm_certificate.cert.arn
}
