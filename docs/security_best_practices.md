# Security Best Practices

## ⚠️ Critical Security Guidelines

### Never Commit Credentials to Git

❌ **NEVER do this:**
```yaml
# BAD - Credentials in code
env:
  - MONGODB_URI=mongodb://admin:password123@host:27017/db
```

✅ **ALWAYS do this:**
```yaml
# GOOD - Credentials from secrets
env:
  - name: MONGODB_URI
    valueFrom:
      secretKeyRef:
        name: mongodb-secret
        key: MONGODB_URI
```

### Test Files with Demo Credentials

The repository includes test files for local development:

| File | Purpose | Security |
|------|---------|----------|
| `docker-compose.yml` | Local dev (no auth) | ✅ Safe - No credentials |
| `docker-compose.mongodb-uri.yml` | Test MONGODB_URI method | ⚠️ **Demo credentials only** |

**Important**: 
- `docker-compose.mongodb-uri.yml` contains **demo credentials** (`admin:password123`)
- These are **clearly marked** with warnings
- **NEVER use these credentials in production**
- This file is for **testing the MONGODB_URI connection method only**

### Production Secret Management

#### AWS (cnap-tech-exercise-aws)

**Step 1**: Store in AWS Secrets Manager
```bash
aws secretsmanager create-secret \
  --name mongodb-credentials \
  --secret-string '{"username":"admin","password":"<STRONG-PASSWORD>"}'
```

**Step 2**: Retrieve in Terraform
```hcl
data "aws_secretsmanager_secret_version" "mongodb_credentials" {
  secret_id = "mongodb-credentials"
}

locals {
  mongodb_creds = jsondecode(data.aws_secretsmanager_secret_version.mongodb_credentials.secret_string)
  mongodb_uri   = "mongodb://${local.mongodb_creds.username}:${local.mongodb_creds.password}@${aws_instance.mongodb.private_ip}:27017/taskdb?authSource=admin"
}
```

**Step 3**: Create Kubernetes Secret
```hcl
resource "kubernetes_secret" "task_manager_db_secret" {
  metadata {
    name = "task-manager-db-secret"
  }
  data = {
    MONGODB_URI = local.mongodb_uri
    SECRET_KEY  = random_password.secret_key.result
  }
}
```

#### GCP (cnap-tech-exercise-gcp)

**Step 1**: Store in GCP Secret Manager
```bash
echo -n "admin" | gcloud secrets create mongodb-username --data-file=-
echo -n "<STRONG-PASSWORD>" | gcloud secrets create mongodb-password --data-file=-
```

**Step 2**: Retrieve in Terraform
```hcl
data "google_secret_manager_secret_version" "mongodb_username" {
  secret = "mongodb-username"
}

data "google_secret_manager_secret_version" "mongodb_password" {
  secret = "mongodb-password"
}
```

**Step 3**: Create Kubernetes Secret
```hcl
resource "kubernetes_secret" "mongodb_credentials" {
  metadata {
    name = "mongodb-credentials"
  }
  data = {
    mongodb-username = data.google_secret_manager_secret_version.mongodb_username.secret_data
    mongodb-password = data.google_secret_manager_secret_version.mongodb_password.secret_data
  }
}
```

### Password Requirements

✅ **Strong passwords must:**
- Be at least 16 characters long
- Include uppercase and lowercase letters
- Include numbers and special characters
- Be randomly generated
- Be unique (never reused)

**Generate strong passwords:**
```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# pwgen
pwgen -s 32 1
```

### SECRET_KEY for Flask

✅ **Generate a strong SECRET_KEY:**
```bash
# Python (recommended)
python3 -c "import secrets; print(secrets.token_hex(32))"

# Output example:
# a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdefabcd
```

❌ **Never use:**
- Default values
- Simple strings like "secret" or "changeme"
- The same key across environments

### Base64 Encoding for Kubernetes Secrets

When creating Kubernetes secrets manually:

```bash
# Encode
echo -n "mongodb://admin:StrongP@ss123@host:27017/db?authSource=admin" | base64

# Decode (for verification only)
echo "bW9uZ29kYjovL2FkbWluOlN0cm9uZ1BAc3MxMjNAaG9zdDoyNzAxNy9kYj9hdXRoU291cmNlPWFkbWlu" | base64 -d
```

**Important**: Use `-n` flag to avoid including newline character!

### Kubernetes Security

#### 1. RBAC - Limit Secret Access

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["task-manager-db-secret"]  # Specific secret only
  verbs: ["get"]
```

#### 2. Encrypt Secrets at Rest

**AWS EKS:**
```hcl
resource "aws_kms_key" "eks_secrets" {
  description = "KMS key for EKS secrets encryption"
}

resource "aws_eks_cluster" "main" {
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_secrets.arn
    }
    resources = ["secrets"]
  }
}
```

**GCP GKE:**
```hcl
resource "google_container_cluster" "primary" {
  database_encryption {
    state    = "ENCRYPTED"
    key_name = google_kms_crypto_key.gke_secrets.id
  }
}
```

#### 3. Network Policies

Restrict which pods can access MongoDB:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mongodb-access
spec:
  podSelector:
    matchLabels:
      app: mongodb
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: task-manager  # Only task-manager pods
    ports:
    - protocol: TCP
      port: 27017
```

### Container Security

#### 1. Non-Root User ✅

The Task Manager container already runs as non-root:

```dockerfile
# Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

Verify:
```bash
kubectl exec -it deployment/task-manager -- id
# uid=1000(appuser) gid=1000(appuser)
```

#### 2. Read-Only Root Filesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
```

#### 3. Drop Capabilities

```yaml
securityContext:
  capabilities:
    drop:
      - ALL
```

#### 4. Resource Limits

```yaml
resources:
  limits:
    cpu: "200m"
    memory: "256Mi"
  requests:
    cpu: "100m"
    memory: "128Mi"
```

### MongoDB Security

#### 1. Authentication Required ✅

Always enable MongoDB authentication:

```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: ${STRONG_PASSWORD}
```

#### 2. Network Isolation

Run MongoDB on private subnet only:

```hcl
# Terraform
resource "aws_instance" "mongodb" {
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.mongodb_private.id]
  # No public IP
  associate_public_ip_address = false
}
```

#### 3. Encryption in Transit

For production, enable TLS:

```
mongodb://user:pass@host:27017/db?authSource=admin&tls=true&tlsCAFile=/path/to/ca.pem
```

### Secret Rotation

#### Automated Rotation Script

```bash
#!/bin/bash
# rotate-mongodb-password.sh

# Generate new password
NEW_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update in cloud KMS
aws secretsmanager update-secret \
  --secret-id mongodb-credentials \
  --secret-string "{\"username\":\"admin\",\"password\":\"${NEW_PASSWORD}\"}"

# Update MongoDB
mongosh "mongodb://admin:${OLD_PASSWORD}@host:27017/admin" \
  --eval "db.changeUserPassword('admin', '${NEW_PASSWORD}')"

# Update Kubernetes secret
terraform apply -auto-approve

# Restart pods
kubectl rollout restart deployment/task-manager
kubectl rollout restart statefulset/mongodb
```

**Schedule rotation:**
```bash
# Crontab: Rotate every 90 days
0 2 1 */3 * /path/to/rotate-mongodb-password.sh
```

### Audit Logging

#### AWS CloudTrail

Monitor secret access:
```hcl
resource "aws_cloudtrail" "secrets_audit" {
  name                          = "secrets-audit"
  s3_bucket_name               = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  
  event_selector {
    read_write_type           = "All"
    include_management_events = true
    
    data_resource {
      type   = "AWS::SecretsManager::Secret"
      values = ["arn:aws:secretsmanager:*:*:secret:mongodb-*"]
    }
  }
}
```

#### GCP Audit Logs

```hcl
resource "google_project_iam_audit_config" "secret_audit" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  
  audit_log_config {
    log_type = "DATA_READ"
  }
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}
```

### Environment-Specific Secrets

Never share secrets between environments:

```
Development:  mongodb://admin:DevPass123@...
Staging:      mongodb://admin:StgPass456@...
Production:   mongodb://admin:PrdPass789@...
```

Each environment should have:
- Unique passwords
- Separate secret stores
- Independent encryption keys
- Isolated networks

### Compliance Checklist

- [ ] All credentials stored in cloud KMS (not in git)
- [ ] Strong passwords (16+ characters, random)
- [ ] Unique SECRET_KEY per environment
- [ ] Kubernetes secrets encrypted at rest
- [ ] RBAC limits secret access
- [ ] Non-root container user
- [ ] MongoDB authentication enabled
- [ ] MongoDB on private network only
- [ ] Audit logging enabled
- [ ] Secret rotation schedule (every 90 days)
- [ ] Network policies restrict access
- [ ] TLS enabled for MongoDB (production)
- [ ] Resource limits configured
- [ ] No hardcoded credentials in code
- [ ] .gitignore includes secret files

### What to Do If Credentials Are Leaked

**Immediate Actions:**

1. **Rotate ALL credentials immediately**
   ```bash
   ./rotate-mongodb-password.sh
   kubectl delete secret task-manager-db-secret
   ./create-secret.sh  # With new password
   kubectl rollout restart deployment/task-manager
   ```

2. **Revoke the leaked credentials in MongoDB**
   ```javascript
   db.dropUser("admin")
   db.createUser({
     user: "admin",
     pwd: "NEW_STRONG_PASSWORD",
     roles: ["root"]
   })
   ```

3. **Check audit logs for unauthorized access**
   ```bash
   # AWS
   aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=mongodb-credentials
   
   # GCP
   gcloud logging read "resource.type=secretmanager.googleapis.com/Secret"
   ```

4. **Remove from git history if committed**
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   git filter-repo --invert-paths --path path/to/secret-file.yaml
   git push --force
   ```

5. **Invalidate any sessions/tokens that used leaked credentials**

6. **Document the incident**

### Testing Security

```bash
# Check for secrets in git history
git log -p | grep -i "password\|secret\|mongodb://"

# Scan for credentials in code
trufflehog git file://. --only-verified

# Check Kubernetes secret encryption
kubectl get secrets task-manager-db-secret -o yaml

# Verify non-root user
kubectl exec -it deployment/task-manager -- id

# Test RBAC
kubectl auth can-i get secrets --as=system:serviceaccount:default:task-manager
```

### Summary

✅ **DO:**
- Store all credentials in cloud KMS
- Use strong, unique passwords
- Enable encryption at rest
- Rotate credentials regularly
- Use RBAC and network policies
- Run containers as non-root
- Enable audit logging
- Test security regularly

❌ **DON'T:**
- Commit credentials to git
- Use default/weak passwords
- Reuse passwords across environments
- Store secrets in environment variables (use Kubernetes secrets)
- Run containers as root
- Disable authentication
- Expose MongoDB publicly
- Share production credentials

### Additional Resources

- [Kubernetes Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [GCP Secret Manager](https://cloud.google.com/secret-manager/docs)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
