# MONGODB_URI Format Clarification

## Question: Database Name in Connection String

**Issue**: There are two MONGODB_URI formats shown in the documentation:
- Format A: `mongodb://admin:password@host:27017/taskdb?authSource=admin` (with `/taskdb`)
- Format B: `mongodb://admin:password@host:27017/?authSource=admin` (without database name)

**Which one should I use?**

## Answer: Both Work! ✅

The Task Manager application supports **both formats**. Here's how:

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

### Your Deployment

Both formats are supported:
```
mongodb://admin:password123@10.0.3.40:27017/?authSource=admin
```

This is **fully compatible** with the Task Manager app! No changes needed.

### Recommendation

**For new deployments:**
- Use **Format A** (with `/taskdb`) - More explicit and self-documenting

**For existing deployments:**
- Keep **Format B** (without `/taskdb`) - Already working, no need to change

**Either way, the app will use the `taskdb` database.**

## Examples

### Format A (Explicit - Recommended for new deployments)

```bash
# Connection string
MONGODB_URI="mongodb://admin:SecurePass123@10.0.3.40:27017/taskdb?authSource=admin"

# Base64 encode
echo -n "mongodb://admin:SecurePass123@10.0.3.40:27017/taskdb?authSource=admin" | base64
# Output: bW9uZ29kYjovL2FkbWluOlNlY3VyZVBhc3MxMjNAMTAuMC4zLjQwOjI3MDE3L3Rhc2tkYj9hdXRoU291cmNlPWFkbWlu

# Kubernetes Secret
apiVersion: v1
kind: Secret
metadata:
  name: tasky-db-secret
data:
  MONGODB_URI: bW9uZ29kYjovL2FkbWluOlNlY3VyZVBhc3MxMjNAMTAuMC4zLjQwOjI3MDE3L3Rhc2tkYj9hdXRoU291cmNlPWFkbWlu
```

### Format B (Implicit)

```bash
# Connection string
MONGODB_URI="mongodb://admin:password123@10.0.3.40:27017/?authSource=admin"

# Base64 encode
echo -n "mongodb://admin:password123@10.0.3.40:27017/?authSource=admin" | base64
# Output: bW9uZ29kYjovL2FkbWluOnBhc3N3b3JkMTIzQDEwLjAuMy40MDoyNzAxNy8/YXV0aFNvdXJjZT1hZG1pbg==

# Kubernetes Secret
apiVersion: v1
kind: Secret
metadata:
  name: tasky-db-secret
data:
  MONGODB_URI: bW9uZ29kYjovL2FkbWluOnBhc3N3b3JkMTIzQDEwLjAuMy40MDoyNzAxNy8/YXV0aFNvdXJjZT1hZG1pbg==
```

**Both work identically!** The app connects to the same database.

## Testing Both Formats

### Test Format A (with /taskdb)

```bash
# docker-compose.mongodb-uri-explicit.yml
services:
  app:
    environment:
      - MONGODB_URI=mongodb://admin:password123@mongodb:27017/taskdb?authSource=admin

# Run
docker-compose -f docker-compose.mongodb-uri-explicit.yml up -d
docker logs task-manager-app 2>&1 | grep "Successfully connected"
# Output: Successfully connected to MongoDB
```

### Test Format B (without /taskdb)

```bash
# docker-compose.mongodb-uri.yml (already exists)
services:
  app:
    environment:
      - MONGODB_URI=mongodb://admin:password123@mongodb:27017/?authSource=admin

# Run
docker-compose -f docker-compose.mongodb-uri.yml up -d
docker logs task-manager-app-uri 2>&1 | grep "Successfully connected"
# Output: Successfully connected to MongoDB
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

## Summary

| Aspect | Format A | Format B |
|--------|----------|----------|
| **URI** | `...27017/taskdb?auth...` | `...27017/?auth...` |
| **Compatible?** | ✅ Yes | ✅ Yes |
| **Database Used** | `taskdb` | `taskdb` |
| **Change Needed?** | No | No |
| **Recommended For** | New deployments (more explicit) | Also valid |

## Conclusion

✅ **Both deployment formats are correct**  
✅ **No changes needed**  
✅ **Task Manager app supports both formats**  
✅ **Database `taskdb` will be used regardless**

The documentation has been updated to show both formats are supported.
