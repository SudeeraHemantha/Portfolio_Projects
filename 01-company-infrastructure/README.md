# 🏢 Enterprise Company Infrastructure (Project 01)

![Domain](https://img.shields.io/badge/Domain-DevOps%20%26%20Infrastructure-blue)
![Status](https://img.shields.io/badge/Status-Completed-success)
![Kubernetes](https://img.shields.io/badge/Kubernetes-High%20Availability%20(3%20Replicas)-326CE5)
![Docker](https://img.shields.io/badge/Docker-Multi--Container-2496ED)
![FastAPI](https://img.shields.io/badge/FastAPI-Security%20Hardened-009688)

---

## 📌 Architecture Overview

The **Enterprise Company Infrastructure** project provides a production-grade, highly available, and containerized infrastructure foundation. It orchestrates state persistence, high-speed in-memory caching/messaging, and microservice business logic using **Docker Compose** for local deployment and **Kubernetes** for enterprise cloud orchestration.

```mermaid
graph TD
    Client[Client / Ingress] -->|HTTP / REST| AM_Svc["agent-manager-service:8000"]
    
    subgraph Cluster["K8s Cluster / Docker Network"]
        subgraph HA_Deploy["Agent Manager HA Deployment (Replicas: 3)"]
            Pod1["Agent Manager Pod 1"]
            Pod2["Agent Manager Pod 2"]
            Pod3["Agent Manager Pod 3"]
        end

        AM_Svc --> Pod1
        AM_Svc --> Pod2
        AM_Svc --> Pod3

        Pod1 -->|TCP 5432| DB_Svc["PostgreSQL Service"]
        Pod2 -->|TCP 5432| DB_Svc
        Pod3 -->|TCP 5432| DB_Svc

        Pod1 -->|TCP 6379| Redis_Svc["Redis Broker Service"]
        Pod2 -->|TCP 6379| Redis_Svc
        Pod3 -->|TCP 6379| Redis_Svc

        DB_Svc --> DB_PV[("PersistentVolumeClaim 10Gi")]
        Redis_Svc --> Redis_Vol[("Redis AppendOnly Data")]
    end

```

---

## 🛠️ Technology Stack & Core Components

| Component | Technology | Purpose | Configuration File |
| --- | --- | --- | --- |
| **Agent Manager** | Python 3.11 / FastAPI | Microservice orchestration & REST API | [`services/agent-manager/src/main.py`](https://www.google.com/search?q=./services/agent-manager/src/main.py) |
| **Relational Database** | PostgreSQL 16 | Persistent relational state storage | [`k8s/postgres-deployment.yaml`](https://www.google.com/search?q=./k8s/postgres-deployment.yaml) |
| **Message Broker / Cache** | Redis 7 (Alpine) | Async queue broker & in-memory cache | [`k8s/redis-deployment.yaml`](https://www.google.com/search?q=./k8s/redis-deployment.yaml) |
| **Container Engine** | Docker Compose | Multi-container local orchestration | [`docker-compose.yml`](https://www.google.com/search?q=./docker-compose.yml) |
| **Cloud Orchestration** | Kubernetes Manifests | Production HA deployment (3 replicas) | [`k8s/`](https://www.google.com/search?q=./k8s/) |

---

## 🔄 Message Broker & Asynchronous Task Pipeline

The system uses **Redis** as a lightweight, high-performance message broker and cache layer:

1. **Async Event Pipeline**: Agents submit asynchronous telemetry and task requests to Redis Pub/Sub channels (`agent:telemetry`, `agent:tasks`).
2. **Decoupled Task Execution**: The `Agent Manager` instances consume tasks asynchronously, insulating the HTTP frontend from long-running operations.
3. **Cache Layer**: Agent state and node health metrics are cached in Redis with short TTLs to eliminate database read bottlenecks.

---

## 📁 Directory Layout

```text
01-company-infrastructure/
├── 📄 docker-compose.yml                 # Local multi-container deployment
├── 📄 README.md                          # Comprehensive project documentation
├── 📁 docker/                            # Base container definitions & build configs
├── 📁 docs/                              # Architectural diagrams & specifications
├── 📁 k8s/                               # Production Kubernetes manifests
│   ├── 📄 configmap.yaml                 # Cluster configuration settings
│   ├── 📄 postgres-storage.yaml          # PersistentVolumeClaim (10Gi)
│   ├── 📄 postgres-deployment.yaml       # Database Deployment & Service
│   ├── 📄 redis-deployment.yaml          # Redis Broker Deployment & Service
│   └── 📄 agent-manager-deployment.yaml  # 3-Replica HA Deployment & Service
├── 📁 nginx/                             # Reverse proxy & gateway load balancer configs
├── 📁 scripts/                           # Infrastructure verification & automation scripts
├── 📁 terraform/                         # Infrastructure as Code (IaC) provisioning
└── 📁 services/
    └── 📁 agent-manager/                 # Microservice codebase
        ├── 📄 Dockerfile                 # Multi-stage security-hardened Dockerfile
        ├── 📄 requirements.txt           # Pinned Python dependencies
        └── 📁 src/
            ├── 📄 config.py              # Pydantic environment configuration
            └── 📄 main.py                # FastAPI entry point & health probes

```

---

## 🚀 Deployment & Operations Guide

### Option 1: Local Deployment with Docker Compose

1. **Build and Launch All Containers**:
```bash
cd 01-company-infrastructure
docker-compose up -d --build

```


2. **Verify Container Health**:
```bash
docker-compose ps

```


3. **Test Microservice API**:
```bash
curl http://localhost:8000/ready

```


4. **Tear Down**:
```bash
docker-compose down -v

```



---

### Option 2: Production Kubernetes Deployment (HA Mode)

1. **Apply Configuration & Persistent Storage**:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-storage.yaml

```


2. **Deploy Database & Redis Services**:
```bash
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

```


3. **Deploy High-Availability Agent Manager (3 Replicas)**:
```bash
kubectl apply -f k8s/agent-manager-deployment.yaml

```


4. **Verify Deployment & Pod Status**:
```bash
kubectl get pods -l app=agent-manager
kubectl get services

```


5. **Test Readiness and Liveness Probes**:
```bash
kubectl port-forward svc/agent-manager-service 8000:8000
curl http://localhost:8000/ready
curl http://localhost:8000/api/v1/agents

```



---

## 🔐 Security & High-Availability Features

* **Non-Root Container Execution**: The Dockerfile uses `appuser` (UID 1000) to adhere to standard container security practices.
* **Zero-Downtime Rolling Updates**: Kubernetes deployments use `maxSurge: 1` and `maxUnavailable: 0` to maintain service availability during updates.
* **Automated Health Monitoring**: Readiness probes ensure traffic is routed exclusively to pods with active connections to PostgreSQL and Redis.

```
