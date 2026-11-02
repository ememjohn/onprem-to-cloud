# Modernized Architecture Specification: Microservices on Amazon EKS

## 1. Executive Summary
This document establishes the modernized cloud native target state for Sabay Premium Bank. The architecture decomposes the monolithic core ledger into decoupled microservices running inside a managed Amazon Elastic Kubernetes Service (Amazon EKS) cluster.

## 2. Microservice Domain Decomposition Matrix
| Service Identifier | Domain Scope | Ingress Routing Path | Target Port | Scaling Policy |
| :--- | :--- | :--- | :--- | :--- |
| account-service | Customer KYC and Account Identity | /api/v1/customers | Port 8001 | Fixed 2 Replicas across dual AZs |
| settlement-service | Transaction Intake and Ledger Settlement | /api/v1/orders | Port 8002 | Horizontal Pod Autoscaler (2 to 8 Pods) |

## 3. Kubernetes Resource Governance Matrix
| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Liveness Probe | Readiness Probe |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| account-service | 100m | 250m | 128Mi | 256Mi | HTTP GET /healthz (Port 8001) | HTTP GET /healthz (Port 8001) |
| settlement-service | 150m | 500m | 256Mi | 512Mi | HTTP GET /healthz (Port 8002) | HTTP GET /healthz (Port 8002) |

## 4. Ingress and Inter Service Communication
1. External Ingress: An Application Load Balancer Ingress Controller routes incoming HTTP traffic based on URL path prefixes:
   Path `/api/v1/customers` forwards to `account-service:8001`.
   Path `/api/v1/orders` forwards to `settlement-service:8002`.
2. Inter Service Validation: When the Settlement Service receives a transaction request, it validates the existence of the corporate account target by querying the Account Service internal Kubernetes ClusterIP service name:
   `http://account-service.sabay-core.svc.cluster.local:8001/api/v1/customers/{id}`
3. Fault Tolerance: Inter service HTTP calls enforce a 2.0 second socket timeout with exponential backoff retries.
