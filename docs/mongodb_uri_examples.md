# MONGODB_URI Examples

This document shows how to use the `MONGODB_URI` environment variable with the Task Manager application for AWS and GCP Kubernetes deployments.

## Overview

The Task Manager app supports **MONGODB_URI** as the primary connection method, compatible with standard Kubernetes secret management patterns.

## AWS Deployment (EKS)

### Step 1: Create the Connection String

From your Terraform variables:
```hcl
mongodb_admin_username = "admin"
mongodb_admin_password = "YourSecurePassword123"
```

From your MongoDB deployment (EC2 private IP):
```
MongoDB IP: 10.0.3.40
MongoDB Port: 27017
```

Build the connection string:

**Option A: With database name (recommended)**
```
mongodb://admin:YourSecurePassword123@10.0.3.40:27017/taskdb?authSource=admin
```

**Option B: Without database name (also supported)**
```
mongodb://admin:YourSecurePassword123@10.0.3.40:27017/?authSource=admin
```

Note: Both formats work. The app will use `taskdb` database regardless, but Option A is more explicit.

### Step 2: Base64 Encode

**If using Option A (with database name):**
```bash
echo -n "mongodb://admin:YourSecurePassword123@10.0.3.40:27017/taskdb?authSource=admin" | base64
```

Output:
```
bW9uZ29kYjovL2FkbWluOllvdXJTZWN1cmVQYXNzd29yZDEyM0AxMC4wLjMuNDA6MjcwMTcvdGFza2RiP2F1dGhTb3VyY2U9YWRtaW4=
```

**If using Option B (without database name - common pattern):**
```bash
echo -n "mongodb://admin:YourSecurePassword123@10.0.3.40:27017/?authSource=admin" | base64
```

Output:
```
bW9uZ29kYjovL2FkbWluOllvdXJTZWN1cmVQYXNzd29yZDEyM0AxMC4wLjMuNDA6MjcwMTcvP2F1dGhTb3VyY2U9YWRtaW4=
```

**Note**: Both formats work. The application code explicitly selects the `taskdb` database using `client[MONGODB_DATABASE]`.

### Step 3: Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Output (example):
```
a1b2c3d4e5f6789012345678901234567890abcdefabcdef1234567890abcd
```

Base64 encode:
```bash
echo -n "a1b2c3d4e5f6789012345678901234567890abcdefabcdef1234567890abcd" | base64
```
