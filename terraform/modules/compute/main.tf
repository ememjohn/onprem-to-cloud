# Query latest official Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for AWS Systems Manager (SSM) - Zero Open SSH Ports
resource "aws_iam_role" "app_instance_role" {
  name = "${var.project_name}-${var.environment}-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-instance-role"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Attach official AWS SSM Managed Policy
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# IAM Instance Profile required for EC2
resource "aws_iam_instance_profile" "app_profile" {
  name = "${var.project_name}-${var.environment}-instance-profile"
  role = aws_iam_role.app_instance_role.name

  tags = {
    Name        = "${var.project_name}-${var.environment}-instance-profile"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# User Data Cloud-Init Script to install Docker and prepare host runtime
locals {
  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y docker git
              systemctl enable --now docker
              usermod -aG docker ec2-user
              EOF
}

# Amazon EC2 Application Host in Private Subnet
resource "aws_instance" "app_host" {
  ami                  = data.aws_ami.amazon_linux_2023.id
  instance_type        = var.instance_type
  subnet_id            = var.private_subnet_id
  iam_instance_profile = aws_iam_instance_profile.app_profile.name

  vpc_security_group_ids      = [var.app_security_group_id]
  associate_public_ip_address = false

  user_data = local.user_data

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true

    tags = {
      Name        = "${var.project_name}-${var.environment}-app-host-root"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-app-host"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Application Load Balancer Target Group with active /healthz probing
resource "aws_lb_target_group" "app_tg" {
  name        = "${var.project_name}-${var.environment}-app-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    path                = "/healthz"
    port                = "8000"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 15
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-app-tg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Register EC2 instance into the Target Group
resource "aws_lb_target_group_attachment" "app_attachment" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_host.id
  port             = 8000
}

# Public Application Load Balancer across multiple AZs
resource "aws_lb" "external" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  drop_invalid_header_fields = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Ingress Listener on Port 80 forwarding to Target Group
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.external.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-http-listener"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
