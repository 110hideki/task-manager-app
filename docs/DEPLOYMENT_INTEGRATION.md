# Deployment Integration Guide

This document explains how the Task Manager container receives MongoDB credentials when deployed by infrastructure projects (cnap-tech-exercise-aws, cnap-tech-exercise-gcp).

## Architecture Overview

```
Infrastructure Repo (Terraform)          Task Manager Container
┌─────────────────────────┐             ┌──────────────────────┐
│                         │             │                      │
│ Terraform Variables:    │             │ Environment Vars:    │
│ ├─ mongodb_admin_user   │   Injected  │ ├─ MONGODB_USERNAME  │
│ └─ mongodb_admin_pass   │────────────>│ └─ MONGODB_PASSWORD  │
│        ↑                │     via     │                      │
│        │                │  Kubernetes │ Flask app.py reads   │
│   AWS KMS / GCP KMS     │   Secrets   │ env vars and builds  │
│   Secret Manager        │             │ connection string    │
└─────────────────────────┘             └──────────────────────┘
```

## How It Works

### 1. Application Code (task-manager-app)

The Flask application (`src/app.py`) reads MongoDB credentials from **environment variables**:

```python
# MongoDB Configuration from environment variables
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', '27017'))
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')  # ← Injected by infrastructure
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')  # ← Injected by infrastructure
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'taskdb')

def get_db_connection():
    """Create and return MongoDB connection"""
    if MONGODB_USERNAME and MONGODB_PASSWORD:
        # Use authenticated connection
        connection_string = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}?authSource=admin"
    else:
        # Use non-authenticated connection (local dev)
        connection_string = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}"
```

**Key Points:**
- ✅ Container is **stateless** - no hardcoded credentials
- ✅ Same container image works in **all environments** (dev/staging/prod, AWS/GCP/Azure)
- ✅ Credentials are **injected at runtime** by Kubernetes
- ✅ Supports **both authenticated and non-authenticated** MongoDB (detects if credentials are provided)

### 2. Infrastructure Code (cnap-tech-exercise-aws / cnap-tech-exercise-gcp)

The infrastructure repositories control the deployment and inject credentials:

#### Terraform Variables (terraform.tfvars)

```hcl
# MongoDB Credentials (Retrieved from KMS)
mongodb_admin_username = "your_mongodb_admin_username"
mongodb_admin_password = "your_mongodb_admin_password"
```

#### Kubernetes Secret Creation (via Terraform)

**AWS Example:**
```hcl
# Retrieve from AWS Secrets Manager
data "aws_secretsmanager_secret_version" "mongodb_credentials" {
  secret_id = "mongodb-credentials"
}

locals {
  mongodb_creds = jsondecode(data.aws_secretsmanager_secret_version.mongodb_credentials.secret_string)
}

# Create Kubernetes Secret
resource "kubernetes_secret" "mongodb_credentials" {
  metadata {
    name      = "mongodb-credentials"
    namespace = "default"
  }

  data = {
    mongodb-username = local.mongodb_creds.username
    mongodb-password = local.mongodb_creds.password
  }
}
```

**GCP Example:**
```hcl
# Retrieve from GCP Secret Manager
data "google_secret_manager_secret_version" "mongodb_username" {
  secret = "mongodb-admin-username"
}

data "google_secret_manager_secret_version" "mongodb_password" {
  secret = "mongodb-admin-password"
}

# Create Kubernetes Secret
resource "kubernetes_secret" "mongodb_credentials" {
  metadata {
    name      = "mongodb-credentials"
    namespace = "default"
  }

  data = {
    mongodb-username = data.google_secret_manager_secret_version.mongodb_username.secret_data
    mongodb-password = data.google_secret_manager_secret_version.mongodb_password.secret_data
  }
}
```

#### Kubernetes Deployment (via Terraform)

The infrastructure repo creates the Kubernetes Deployment with environment variables referencing the secret:

```hcl
resource "kubernetes_deployment" "task_manager" {
  metadata {
    name = "task-manager"
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "task-manager"
      }
    }

    template {
      metadata {
        labels = {
          app = "task-manager"
        }
      }

      spec {
        container {
          name  = "task-manager"
          image = "110hideki/task-manager-app:latest"

          # Environment variables - credentials from Kubernetes Secret
          env {
            name  = "MONGODB_HOST"
            value = "mongodb-0.mongodb"  # Or your MongoDB host
          }
          
          env {
            name = "MONGODB_USERNAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mongodb_credentials.metadata[0].name
                key  = "mongodb-username"
              }
            }
          }

          env {
            name = "MONGODB_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mongodb_credentials.metadata[0].name
                key  = "mongodb-password"
              }
            }
          }

          env {
            name = "POD_IP"
            value_from {
              field_ref {
                field_path = "status.podIP"
              }
            }
          }

          env {
            name = "HOSTNAME"
            value_from {
              field_ref {
                field_path = "metadata.name"
              }
            }
          }

          port {
            container_port = 5000
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 30
            period_seconds        = 30
          }

          readiness_probe {
            http_get {
              path = "/ready"
              port = 5000
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}
```

## Environment Variables Reference

### Required for MongoDB Connection

| Variable | Description | Source | Example |
|----------|-------------|--------|---------|
| `MONGODB_HOST` | MongoDB hostname | Terraform (hardcoded or from service) | `mongodb-0.mongodb` |
| `MONGODB_PORT` | MongoDB port | Terraform (hardcoded) | `27017` |
| `MONGODB_USERNAME` | Admin username | **KMS → Kubernetes Secret** | `admin` |
| `MONGODB_PASSWORD` | Admin password | **KMS → Kubernetes Secret** | `securepassword123` |
| `MONGODB_DATABASE` | Database name | Terraform (hardcoded) | `taskdb` |

### Optional for Pod Identification

| Variable | Description | Source | Example |
|----------|-------------|--------|---------|
| `POD_IP` | Pod IP address | Kubernetes Downward API | `10.244.1.5` |
| `HOSTNAME` | Pod hostname | Kubernetes Downward API | `task-manager-5f7d8c9b-x7p2q` |

### Required for Flask

| Variable | Description | Source | Example |
|----------|-------------|--------|---------|
| `SECRET_KEY` | Flask session secret | Kubernetes Secret (generated) | `random-hex-string` |

## Security Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Credentials Stored in Cloud KMS                               │
│    AWS: Secrets Manager                                          │
│    GCP: Secret Manager                                           │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 │ Terraform retrieves at apply time
                 ↓
┌──────────────────────────────────────────────────────────────────┐
│ 2. Terraform Creates Kubernetes Secret                           │
│    (Base64 encoded, stored in etcd)                              │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 │ Referenced in Deployment spec
                 ↓
┌──────────────────────────────────────────────────────────────────┐
│ 3. Kubernetes Injects as Environment Variables                   │
│    (Decrypted and mounted when container starts)                 │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 │ Container runtime
                 ↓
┌──────────────────────────────────────────────────────────────────┐
│ 4. Flask App Reads Environment Variables                         │
│    os.getenv('MONGODB_USERNAME')                                 │
│    os.getenv('MONGODB_PASSWORD')                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Local Development vs Production

### Local Development (docker-compose.yml)

```yaml
services:
  mongodb:
    image: mongo:4.4
    # No authentication for local dev
    
  app:
    build: .
    environment:
      - MONGODB_HOST=mongodb
      - MONGODB_PORT=27017
      # No MONGODB_USERNAME or MONGODB_PASSWORD
      # App will use non-authenticated connection
```

### Production (Kubernetes via Terraform)

```yaml
# Credentials injected from Kubernetes Secret
env:
  - name: MONGODB_USERNAME
    valueFrom:
      secretKeyRef:
        name: mongodb-credentials
        key: mongodb-username
  - name: MONGODB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: mongodb-credentials
        key: mongodb-password
```

## Implementation Checklist for Infrastructure Repos

### AWS (cnap-tech-exercise-aws)

- [ ] Store MongoDB credentials in AWS Secrets Manager
- [ ] Create `mongodb-credentials.tf` to retrieve from Secrets Manager
- [ ] Create Kubernetes Secret via Terraform
- [ ] Update EKS deployment to reference the secret
- [ ] Add variables to `terraform.tfvars` (if using variables)
- [ ] Test deployment with `kubectl exec` to verify env vars

### GCP (cnap-tech-exercise-gcp)

- [ ] Store MongoDB credentials in GCP Secret Manager
- [ ] Create `mongodb-credentials.tf` to retrieve from Secret Manager
- [ ] Create Kubernetes Secret via Terraform
- [ ] Update GKE deployment to reference the secret
- [ ] Add variables to `terraform.tfvars` (if using variables)
- [ ] Test deployment with `kubectl exec` to verify env vars

## Testing Credential Injection

After deployment, verify the credentials are injected correctly:

```bash
# Check if secret exists
kubectl get secret mongodb-credentials

# Verify environment variables in running pod (without exposing values)
kubectl exec -it deployment/task-manager -- env | grep MONGODB

# Expected output:
# MONGODB_HOST=mongodb-0.mongodb
# MONGODB_PORT=27017
# MONGODB_USERNAME=admin
# MONGODB_PASSWORD=<base64-value>
# MONGODB_DATABASE=taskdb

# Test MongoDB connection from pod
kubectl exec -it deployment/task-manager -- curl localhost:5000/ready

# Expected output:
# {"status": "ready", "mongodb": "connected"}
```

## Troubleshooting

### Container can't connect to MongoDB

1. **Check if credentials are injected:**
   ```bash
   kubectl exec -it deployment/task-manager -- printenv | grep MONGODB
   ```

2. **Check if secret exists:**
   ```bash
   kubectl describe secret mongodb-credentials
   ```

3. **Check application logs:**
   ```bash
   kubectl logs -l app=task-manager --tail=50
   ```

4. **Verify MongoDB is accessible:**
   ```bash
   kubectl exec -it deployment/task-manager -- nc -zv mongodb-0.mongodb 27017
   ```

### Wrong credentials

1. **Update the secret in KMS** (AWS Secrets Manager or GCP Secret Manager)

2. **Re-apply Terraform:**
   ```bash
   terraform apply
   ```

3. **Restart pods to pick up new credentials:**
   ```bash
   kubectl rollout restart deployment/task-manager
   ```

## Best Practices

1. **Never hardcode credentials** in the container image
2. **Always use KMS** (AWS Secrets Manager / GCP Secret Manager) for credential storage
3. **Use Kubernetes Secrets** for runtime injection
4. **Rotate credentials regularly** and restart pods
5. **Use RBAC** to limit which pods can access which secrets
6. **Enable encryption at rest** for Kubernetes secrets (KMS integration)
7. **Audit secret access** using cloud provider logging

## Summary

**The task-manager-app container is completely credential-agnostic:**
- ✅ No credentials in code
- ✅ No credentials in Dockerfile
- ✅ No credentials in git repository
- ✅ Credentials are **externally injected** by the infrastructure deployment

**The infrastructure repositories (cnap-tech-exercise-aws/gcp) are responsible for:**
- 🔐 Retrieving credentials from KMS
- 🔐 Creating Kubernetes Secrets
- 🔐 Injecting credentials into containers via environment variables

This separation ensures:
- **Portability**: Same container works on AWS, GCP, Azure
- **Security**: Credentials never in source code
- **Flexibility**: Change credentials without rebuilding container
- **Compliance**: Centralized secret management via cloud KMS
