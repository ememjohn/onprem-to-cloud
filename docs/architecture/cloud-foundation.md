# Cloud Foundation Architecture Specification: Multi Tier AWS VPC

## Executive Summary
This document establishes the foundational networking architecture deployed in Amazon Web Services. The landing zone provides a defense in depth security posture isolating public ingress, application compute, and database persistence into distinct network tiers across multiple availability zones.

## Network Topology Model

```mermaid
graph TD
    Internet[Public Internet: 0.0.0.0/0] --> IGW[AWS Internet Gateway]

    subgraph AWS_VPC [VPC: 10.0.0.0/16]
        subgraph Public_Tier [Public Ingress Subnet Tier: Dual AZ]
            PubSub1[Public Subnet 1: 10.0.1.0/24 in us-east-1a]
            PubSub2[Public Subnet 2: 10.0.2.0/24 in us-east-1b]
            ALB_SG[Security Group: alb-sg - Ingress: 80, 443]
        end

        subgraph Private_App_Tier [Private Application Subnet Tier: Compute]
            AppSub1[Private App Subnet 1: 10.0.10.0/24 in us-east-1a]
            AppSub2[Private App Subnet 2: 10.0.20.0/24 in us-east-1b]
            App_SG[Security Group: app-sg - Ingress: Port 8000 strictly from alb-sg]
        end

        subgraph Isolated_DB_Tier [Isolated Database Subnet Tier: Persistence]
            DBSub1[Isolated DB Subnet 1: 10.0.100.0/24 in us-east-1a]
            DBSub2[Isolated DB Subnet 2: 10.0.200.0/24 in us-east-1b]
            DB_SG[Security Group: db-sg - Ingress: Port 5432 strictly from app-sg]
            DBSubGroup[RDS DB Subnet Group: Dual AZ Persistence]
        end
    end

    IGW --> PubSub1
    IGW --> PubSub2
    PubSub1 --> AppSub1
    PubSub2 --> AppSub2
    AppSub1 --> DBSub1
    AppSub2 --> DBSub2
```

## Subnet Allocation and Routing Matrix
| Subnet Classification | Availability Zone | CIDR Block Allocation | Gateway Route Association | Security Boundary |
| :--- | :--- | :--- | :--- | :--- |
| Public Subnet 1 | us-east-1a | 10.0.1.0/24 | Internet Gateway (0.0.0.0/0) | Ingress perimeter for Application Load Balancers |
| Public Subnet 2 | us-east-1b | 10.0.2.0/24 | Internet Gateway (0.0.0.0/0) | Multi AZ redundancy for public ingress |
| Private App Subnet 1 | us-east-1a | 10.0.10.0/24 | Private Route Table (No IGW) | Dedicated to EC2 application compute |
| Private App Subnet 2 | us-east-1b | 10.0.20.0/24 | Private Route Table (No IGW) | Compute redundancy across availability zones |
| Isolated DB Subnet 1 | us-east-1a | 10.0.100.0/24 | Isolated Route Table (No Egress) | Multi AZ RDS PostgreSQL cluster storage |
| Isolated DB Subnet 2 | us-east-1b | 10.0.200.0/24 | Isolated Route Table (No Egress) | Multi AZ RDS PostgreSQL standby replica |

## Security Group Defense in Depth Matrix
| Security Group Identifier | Ingress Source | Allowed Ports / Protocols | Egress Target | Operational Scope |
| :--- | :--- | :--- | :--- | :--- |
| apex-oms-dev-alb-sg | 0.0.0.0/0 (Public Internet) | Port 80 (HTTP), Port 443 (HTTPS) | All Traffic (0.0.0.0/0) | Public load balancer traffic termination |
| apex-oms-dev-app-sg | apex-oms-dev-alb-sg (SG Reference) | Port 8000 (ASGI Application) | All Traffic (0.0.0.0/0) | Application instances protected from direct web scans |
| apex-oms-dev-db-sg | apex-oms-dev-app-sg (SG Reference) | Port 5432 (PostgreSQL) | Denied (No Outbound Egress) | Managed database protected from compute compromises |
