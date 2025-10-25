# MongoDB Configuration Guide

This guide covers MongoDB connection configuration for the Task Manager application, including URI format explanations, Kubernetes secret creation, and testing examples. For cloud-specific deployment instructions, refer to the respective CNAP project repositories.

## Overview

The Task Manager app supports **MONGODB_URI** as the primary connection method, compatible with standard Kubernetes secret management patterns. The application is flexible and supports multiple URI formats.

## URI Format Support

### Both Formats Work! ✅

The Task Manager application supports **both formats**:
- **Format A (Explicit)**: `mongodb://admin:password@host:27017/taskdb?authSource=admin` (with `/taskdb`)
- **Format B (Implicit)**: `mongodb://admin:password@host:27017/?authSource=admin` (without database name)

### How It Works

```python
# From src/app.py
MONGODB_URI = os.getenv('MONGODB_URI', '')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'taskdb')

def get_db_connection():
    if MONGODB_URI:
        connection_string = MONGODB_URI  # Uses whatever URI you provide
        
    client = MongoClient(connection_string)
    return client[MONGODB_DATABASE]  # ← Always selects 'taskdb'
```

**Key Point**: The last line `client[MONGODB_DATABASE]` ensures the app always uses the `taskdb` database, regardless of whether it's in the URI.

### Format Comparison

| Format | URI | Works? | How |
|--------|-----|--------|-----|
| **A (Explicit)** | `mongodb://admin:pass@host:27017/taskdb?authSource=admin` | ✅ Yes | MongoDB driver connects to `taskdb` from URI |
| **B (Implicit)** | `mongodb://admin:pass@host:27017/?authSource=admin` | ✅ Yes | App code selects `taskdb` via `client[MONGODB_DATABASE]` |

### Recommendation

**For new deployments:**
- Use **Format A** (with `/taskdb`) - More explicit and self-documenting

**For existing deployments:**
- Keep **Format B** (without `/taskdb`) - Already working, no need to change

**Either way, the app will use the `taskdb` database.**

## Configuration Examples

### Basic Connection String Format

The general MongoDB URI format for the Task Manager application:

```
mongodb://[username]:[password]@[host]:[port]/[database]?authSource=admin
```

**Example with explicit database (Format A - Recommended):**
```
mongodb://admin:YourPassword123@10.0.3.40:27017/taskdb?authSource=admin
```

**Example without explicit database (Format B - Also supported):**
```
mongodb://admin:YourPassword123@10.0.3.40:27017/?authSource=admin
```

### Creating Kubernetes Secrets

#### Step 1: Base64 Encode Your Connection String

```bash
# For Format A (with database name)
echo -n "mongodb://admin:YourPassword123@10.0.3.40:27017/taskdb?authSource=admin" | base64

# For Format B (without database name)
echo -n "mongodb://admin:YourPassword123@10.0.3.40:27017/?authSource=admin" | base64
```

#### Step 2: Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Then base64 encode the result:
```bash
echo -n "your-generated-secret-key" | base64
```

#### Step 3: Create Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: task-manager-db-secret
data:
  MONGODB_URI: <your-base64-encoded-mongodb-uri>
  SECRET_KEY: <your-base64-encoded-secret-key>
```

#### Step 4: Apply to Kubernetes

```bash
kubectl apply -f task-manager-secret.yaml
```

## Testing Both Formats

### Test Format A (with /taskdb)

```bash
# Create test docker-compose file
cat > docker-compose.mongodb-uri-explicit.yml << EOF
services:
  app:
    environment:
      - MONGODB_URI=mongodb://admin:password123@mongodb:27017/taskdb?authSource=admin
EOF

# Run test
docker-compose -f docker-compose.mongodb-uri-explicit.yml up -d
docker logs task-manager-app 2>&1 | grep "Successfully connected"
# Expected: Successfully connected to MongoDB
```

### Test Format B (without /taskdb)

```bash
# Use existing docker-compose file
docker-compose -f docker-compose.mongodb-uri.yml up -d
docker logs task-manager-app-uri 2>&1 | grep "Successfully connected"
# Expected: Successfully connected to MongoDB
```

**Both connect successfully!**

## Why Both Formats Work

MongoDB connection URIs follow this format:
```
mongodb://[username:password@]host[:port][/database][?options]
```

The `/database` part is **optional** because:
1. You can specify the database in the URI
2. OR you can select it programmatically with `client[database_name]`

The Task Manager app uses **option 2**, which means:
- If you include `/taskdb` in the URI → MongoDB driver uses it, app also selects it ✅
- If you omit `/taskdb` from the URI → App code selects it ✅

**Result**: Same database used either way.

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Verify MongoDB VM is running
   - Check security group/firewall rules allow port 27017
   - Verify internal IP address is correct

2. **Authentication Failed**
   - Double-check username and password
   - Ensure `authSource=admin` is included in the URI
   - Verify the admin user exists in MongoDB

3. **Database Not Found**
   - Don't worry! The app creates the `taskdb` database automatically
   - Both URI formats will work regardless

### Verification Commands

```bash
# Check secret exists
kubectl get secret task-manager-db-secret

# Check secret contents (be careful in production)
kubectl get secret task-manager-db-secret -o yaml

# Check pod environment variables (without exposing values)
kubectl exec -it deployment/task-manager -- printenv | grep MONGODB
```

## Summary

| Aspect | Format A (Explicit) | Format B (Implicit) |
|--------|----------|----------|
| **URI Pattern** | `...27017/taskdb?auth...` | `...27017/?auth...` |
| **Compatible?** | ✅ Yes | ✅ Yes |
| **Database Used** | `taskdb` | `taskdb` |
| **Change Needed?** | No | No |
| **Recommended For** | New deployments | Existing deployments |

## Key Takeaways

✅ **Both deployment formats are correct**  
✅ **No changes needed to existing deployments**  
✅ **Task Manager app supports both URI formats**  
✅ **Database `taskdb` will be used regardless of format**  
✅ **Choose the format that best fits your deployment strategy**

Whether you're deploying to AWS EKS or GCP GKE, using Format A or Format B, the Task Manager application will connect successfully to your MongoDB instance.