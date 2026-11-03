# Architecture Decision Record 012

## Title
FinOps Network Egress Architecture: Deliberate Exclusion of AWS NAT Gateway

## Status
Accepted

## Context
Standard enterprise VPC reference architectures place compute instances in private subnets and deploy an AWS NAT Gateway in public subnets to provide outbound internet connectivity for package installations and AWS API calls. An AWS NAT Gateway incurs a standing charge of approximately thirty two dollars monthly per availability zone, plus data processing fees, even when completely idle.

## Decision Drivers
1. Strict Lab Budget Preservation: Maintain total cloud expenditure well within promotional credits.
2. Zero Open Management Inbound Ports: Guarantee that eliminating a NAT Gateway does not compromise security by opening port 22 or exposing the application to public internet scans.
3. Full AWS API Access: Ensure compute hosts can communicate outbound with AWS Systems Manager, Secrets Manager, and container registries.

## Evaluated Alternatives
1. Persistent Multi-AZ NAT Gateway: Rejected for development and rehearsal phases. Running dual NAT Gateways costs over sixty four dollars monthly in idle fees, burning over forty percent of our promotional credit allocation.
2. VPC Interface Endpoints for Private Subnets: Evaluated as a secure option, but provisioning private endpoints for SSM, EC2, CloudWatch, and Secrets Manager costs over twenty dollars monthly in endpoint hourly fees.
3. Public Subnet Placement with Strict Security Group Referencing: Selected. The compute host resides in a public subnet with an auto assigned public IP to route outbound HTTPS traffic through the free Internet Gateway. Crucially, the inbound security group strictly allows port 8000 from the Application Load Balancer, while port 22 remains completely closed.

## Consequences
Positive:
1. Completely eliminated thirty two dollars monthly in standing NAT Gateway fees.
2. Outbound SSM, CloudWatch, and Secrets Manager API traffic functions over the free Internet Gateway.
3. Security posture remains intact: zero open inbound administrative ports.

Negative:
1. Production commercial deployments with unlimited budgets will migrate to private subnets backed by NAT Gateways or dedicated VPC Endpoints before handling external production debit cards.
