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

## Environment Variables Reference

### Required for MongoDB Connection

| Variable | Description | Source | Example |
|----------|-------------|--------|---------|
| `MONGODB_HOST` | MongoDB hostname | Terraform (hardcoded or from service) | `mongodb-0.mongodb` |
| `MONGODB_PORT` | MongoDB port | Terraform (hardcoded) | `27017` |
| `MONGODB_USERNAME` | Admin username | **KMS → Kubernetes Secret** | `admin` |
| `MONGODB_PASSWORD` | Admin password | **KMS → Kubernetes Secret** | `securepassword123` |
| `MONGODB_DATABASE` | Database name | Terraform (hardcoded) | `taskdb` |

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

## Local Development 

### Local Debugging (docker-compose.yml)

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
