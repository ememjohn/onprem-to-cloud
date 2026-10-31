terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

module "networking" {
  source = "../../modules/networking"

  vpc_cidr     = var.vpc_cidr
  environment  = var.environment
  project_name = var.project_name

  availability_zones       = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24"]
  private_app_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]
  isolated_db_subnet_cidrs = ["10.0.100.0/24", "10.0.200.0/24"]
}

module "database" {
  source = "../../modules/database"

  project_name         = var.project_name
  environment          = var.environment
  db_subnet_group_name = module.networking.db_subnet_group_name
  db_security_group_id = module.networking.db_security_group_id
  db_name              = "orders_db"
  db_username          = "dbadmin"
}

module "compute" {
  source = "../../modules/compute"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  private_subnet_id     = module.networking.private_app_subnet_ids[0]
  alb_security_group_id = module.networking.alb_security_group_id
  app_security_group_id = module.networking.app_security_group_id
  instance_type         = "t3.small"
}
