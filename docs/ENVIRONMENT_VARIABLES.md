# Environment Variables Reference

This document describes all environment variables used by the Task Manager application.

## MongoDB Connection

The application supports **three methods** for MongoDB connection configuration. The methods are checked in priority order:

### Method 1: MONGODB_URI (Priority #1) ⭐ Recommended for Kubernetes

**Use case**: Standard Kubernetes deployment pattern

**Format**: Full MongoDB connection string

**Option A: With database name (explicit)**
```bash
MONGODB_URI="mongodb://admin:password@host:27017/taskdb?authSource=admin"
```

**Option B: Without database name (also supported)**
```bash
MONGODB_URI="mongodb://admin:password@host:27017/?authSource=admin"
```

**Note**: Both formats work correctly. The application will use the `taskdb` database regardless:
- Option A: MongoDB driver uses `taskdb` from the URI
- Option B: Application code explicitly selects `taskdb` using `client[MONGODB_DATABASE]`

**Kubernetes Secret Example:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
type: Opaque
data:
  MONGODB_URI: bW9uZ29kYjovL2FkbWluOnBhc3N3b3JkMTIzQG1vbmdvZGItaG9zdDoyNzAxNy90YXNrZGI/YXV0aFNvdXJjZT1hZG1pbg==
  SECRET_KEY: eW91ci1zZWNyZXQta2V5LWhlcmU=
```

**Generate base64:**
```bash
echo -n "mongodb://admin:password123@10.0.3.40:27017/taskdb?authSource=admin" | base64
```

**Deployment Example:**
```yaml
env:
  - name: MONGODB_URI
    valueFrom:
      secretKeyRef:
        name: mongodb-secret
        key: MONGODB_URI
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: mongodb-secret
        key: SECRET_KEY
```

### Method 2: Individual Variables (Alternative for Kubernetes)

Build the connection string from individual components.

```bash
MONGODB_HOST="mongodb-host"
MONGODB_PORT="27017"
MONGODB_USERNAME="admin"
MONGODB_PASSWORD="password123"
MONGODB_DATABASE="taskdb"
```

### Method 3: Non-Authenticated (Local Development)

For local development with MongoDB running without authentication.

```bash
MONGODB_HOST="localhost"
MONGODB_PORT="27017"
MONGODB_DATABASE="taskdb"
```

**Docker Compose Example:**
```yaml
services:
  app:
    environment:
      - MONGODB_HOST=mongodb
      - MONGODB_PORT=27017
      - MONGODB_DATABASE=taskdb
      # No username/password needed
```

## All Environment Variables

### MongoDB Configuration

| Variable | Description | Default | Example | Required |
|----------|-------------|---------|---------|----------|
| `MONGODB_URI` | Full connection string (Method 1) | - | `mongodb://user:pass@host:27017/db?authSource=admin` | No* |
| `MONGODB_HOST` | MongoDB hostname/IP (Method 2/3) | `localhost` | `mongodb-0.mongodb` | No* |
| `MONGODB_PORT` | MongoDB port (Method 2/3) | `27017` | `27017` | No |
| `MONGODB_USERNAME` | MongoDB username (Method 2) | - | `admin` | No* |
| `MONGODB_PASSWORD` | MongoDB password (Method 2) | - | `securepass123` | No* |
| `MONGODB_DATABASE` | Database name | `taskdb` | `taskdb` | No |

*At least one connection method must be configured

### Flask Configuration

| Variable | Description | Default | Example | Required |
|----------|-------------|---------|---------|----------|
| `SECRET_KEY` | Flask session encryption key | Auto-generated (dev only) | `a1b2c3d4e5f6...` | Yes (production) |

⚠️ **Important**: Always set `SECRET_KEY` in production. The auto-generated key is for development only and will cause issues in multi-pod deployments.

## Configuration Priority

The application checks for MongoDB connection in this order:

1. **MONGODB_URI** - If set, uses this connection string (ignores all other MongoDB variables)
2. **MONGODB_USERNAME + MONGODB_PASSWORD** - If both set, builds authenticated connection string
3. **MONGODB_HOST only** - If no credentials, uses non-authenticated connection


### 3. Local Development (docker-compose)

No authentication needed:

```yaml
# docker-compose.yml
services:
  mongodb:
    image: mongo:4.4
    ports:
      - "27017:27017"
    # No MONGO_INITDB_ROOT_USERNAME/PASSWORD
    
  app:
    build: .
    ports:
      - "5001:5000"
    environment:
      - MONGODB_HOST=mongodb
      - SECRET_KEY=dev-secret-key
    depends_on:
      - mongodb
```

### 4. Local Development (Python venv)

```bash
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export SECRET_KEY=dev-secret-key
python src/app.py
```

## Security Best Practices

### 1. Never Hardcode Secrets

❌ **Bad:**
```yaml
env:
  - name: MONGODB_URI
    value: "mongodb://admin:password123@host:27017/db"  # DON'T DO THIS
```

✅ **Good:**
```yaml
env:
  - name: MONGODB_URI
    valueFrom:
      secretKeyRef:
        name: tasky-db-secret
        key: MONGODB_URI
```

### 2. Generate Strong SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

### 3. Base64 Encode for Kubernetes Secrets

```bash
# Encode
echo -n "mongodb://admin:pass@host:27017/db?authSource=admin" | base64

# Decode (for verification)
echo "bW9uZ29kYjovL2FkbWluOnBhc3NAaG9zdDoyNzAxNy9kYj9hdXRoU291cmNlPWFkbWlu" | base64 -d
```

## Troubleshooting

### Check Current Configuration

```bash
# Check which variables are set in pod
kubectl exec -it deployment/task-manager -- printenv | grep MONGODB

# Expected output (Method 1):
# MONGODB_URI=mongodb://admin:***@host:27017/db?authSource=admin

# Expected output (Method 2):
# MONGODB_HOST=mongodb-0.mongodb
# MONGODB_PORT=27017
# MONGODB_USERNAME=admin
# MONGODB_PASSWORD=***
```

### Test Connection

```bash
# Check health endpoint
kubectl exec -it deployment/task-manager -- curl localhost:5000/health

# Check readiness (includes MongoDB connectivity test)
kubectl exec -it deployment/task-manager -- curl localhost:5000/ready

# Expected output:
# {"status": "ready", "mongodb": "connected"}
```

### View Application Logs

```bash
# Check connection method used
kubectl logs -l app=task-manager --tail=20 | grep "Using"

# Expected output:
# Using MONGODB_URI for connection
# Successfully connected to MongoDB
```
## Summary

The Task Manager application is **flexible** and supports multiple MongoDB connection methods:

1. ✅ **Compatible with standard Kubernetes patterns** (MONGODB_URI)
2. ✅ **Compatible with individual variable deployment patterns**
3. ✅ **Compatible with local development** (no authentication)

Choose the method that best fits your infrastructure setup!
