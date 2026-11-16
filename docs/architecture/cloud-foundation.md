# Cloud Foundation Architecture Specification: Multi Tier AWS VPC

## Executive Summary
This document establishes the foundational networking architecture deployed in Amazon Web Services. The landing zone provides a defense in depth security posture isolating public ingress, application compute, and database persistence into distinct network tiers across multiple availability zones.

## Network Topology Model

<img width="2880" height="1720" alt="network-vpc" src="https://github.com/user-attachments/assets/a7ddee7d-1f30-4f61-8341-17fe8dc64cb5" />

```

## Subnet Allocation and Routing Matrix
| Subnet Classification | Availability Zone | CIDR Block Allocation | Gateway Route Association | Security Boundary |
| :--- | :--- | :--- | :--- | :--- |
| Public Subnet 1 | us-east-1a | Public Ingress Zone A | Internet Gateway (0.0.0.0/0) | Ingress perimeter for Application Load Balancers |
| Public Subnet 2 | us-east-1b | Public Ingress Zone B | Internet Gateway (0.0.0.0/0) | Multi AZ redundancy for public ingress |
| Private App Subnet 1 | us-east-1a | Private Compute Zone A | Private Route Table (No IGW) | Dedicated to EC2 application compute |
| Private App Subnet 2 | us-east-1b | Private Compute Zone B | Private Route Table (No IGW) | Compute redundancy across availability zones |
| Isolated DB Subnet 1 | us-east-1a | Isolated Database Zone A | Isolated Route Table (No Egress) | Multi AZ RDS PostgreSQL cluster storage |
| Isolated DB Subnet 2 | us-east-1b | Isolated Database Zone B | Isolated Route Table (No Egress) | Multi AZ RDS PostgreSQL standby replica |

## Security Group Defense in Depth Matrix
| Security Group Identifier | Ingress Source | Allowed Ports / Protocols | Egress Target | Operational Scope |
| :--- | :--- | :--- | :--- | :--- |
| sabay-bank-dev-alb-sg | 0.0.0.0/0 (Public Internet) | Port 80 (HTTP), Port 443 (HTTPS) | All Traffic (0.0.0.0/0) | Public load balancer traffic termination |
| sabay-bank-dev-app-sg | sabay-bank-dev-alb-sg (SG Reference) | Port 8000 (ASGI Application) | All Traffic (0.0.0.0/0) | Application instances protected from direct web scans |
| sabay-bank-dev-db-sg | sabay-bank-dev-app-sg (SG Reference) | Port 5432 (PostgreSQL) | Denied (No Outbound Egress) | Managed database protected from compute compromises |
