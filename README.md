# Task Manager App

A simple web application for managing tasks, built with Flask and MongoDB. Designed to demonstrate stateless application architecture, Kubernetes deployment, and load balancing across multiple cloud providers (AWS EKS, GCP GKE, Azure AKS).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

## 🎯 Purpose

This application is part of a DevOps portfolio project demonstrating:
- **Stateless application design** with external state management
- **Container orchestration** on Kubernetes
- **Multi-cloud deployment** (AWS, GCP, Azure)
- **CI/CD pipelines** with GitHub Actions
- **Load balancing** and horizontal scaling
- **Infrastructure as Code** integration

## ✨ Features

- ✅ **Simple Task Management**: Create, complete, and delete tasks
- ✅ **Web UI**: Clean, responsive HTML interface
- ✅ **MongoDB Backend**: Persistent storage for tasks
- ✅ **Stateless Design**: Multiple instances share the same database
- ✅ **Health Checks**: Liveness and readiness probes for Kubernetes
- ✅ **Pod Identification**: See which pod handled each request
- ✅ **Production Ready**: Gunicorn WSGI server, non-root container user
- ✅ **Multi-Cloud Compatible**: Works on AWS EKS, GCP GKE, Azure AKS

## 📸 Screenshot

```
┌──────────────────────────────────────┐
│       📝 Task Manager                │
│  Simple task management with MongoDB │
├──────────────────────────────────────┤
│  Total: 5  │  Pending: 2  │  Done: 3 │
├──────────────────────────────────────┤
│  [Enter a new task...]  [Add Task]   │
├──────────────────────────────────────┤
│  ☐ Deploy to production              │
│  ☑ Write documentation               │
│  ☐ Test load balancing               │
└──────────────────────────────────────┘
   Served by: Pod task-manager-abc123
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Kubernetes Service              │
│         (Load Balancer)                 │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌──▼──┐ ┌──▼──┐
│ Pod 1 │ │Pod 2│ │Pod 3│
│ Flask │ │Flask│ │Flask│
└───┬───┘ └──┬──┘ └──┬──┘
    │        │       │
    └────────┼───────┘
             │
      ┌──────▼──────┐
      │   MongoDB   │
      │  (Shared)   │
      └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB running locally or remotely
- Docker (optional, for containerization)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/110hideki/task-manager-app.git
cd task-manager-app
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_DATABASE=taskdb
# Optional: If MongoDB requires authentication
export MONGODB_USERNAME=admin
export MONGODB_PASSWORD=yourpassword
```

5. **Run the application**
```bash
cd src
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 🐳 Docker

### Build Image

```bash
docker build -t task-manager-app:latest .
```

### Run Container

```bash
# Run with local MongoDB
docker run -d \
  --name task-manager \
  -p 5000:5000 \
  -e MONGODB_HOST=host.docker.internal \
  -e MONGODB_PORT=27017 \
  -e MONGODB_DATABASE=taskdb \
  task-manager-app:latest

# Run with MongoDB authentication
docker run -d \
  --name task-manager \
  -p 5000:5000 \
  -e MONGODB_HOST=mongodb-host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_USERNAME=admin \
  -e MONGODB_PASSWORD=yourpassword \
  -e MONGODB_DATABASE=taskdb \
  task-manager-app:latest
```

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag task-manager-app:latest 110hideki/task-manager-app:latest

# Push image
docker push 110hideki/task-manager-app:latest
```

## ☸️ Kubernetes Deployment

This application is designed to be deployed on Kubernetes. See the infrastructure repositories for deployment manifests:

- **AWS EKS**: [cnap-tech-exercise-aws](https://github.com/110hideki/cnap-tech-exercise-aws)
- **GCP GKE**: [cnap-tech-exercise-gcp](https://github.com/110hideki/cnap-tech-exercise-gcp)

### Basic Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-manager
  template:
    metadata:
      labels:
        app: task-manager
    spec:
      containers:
      - name: task-manager
        image: 110hideki/task-manager-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: MONGODB_HOST
          value: "mongodb-service"
        - name: MONGODB_PORT
          value: "27017"
        - name: MONGODB_DATABASE
          value: "taskdb"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | **Full MongoDB connection string** (takes precedence over individual variables) | - | No* |
| `MONGODB_HOST` | MongoDB server hostname/IP | `localhost` | No* |
| `MONGODB_PORT` | MongoDB server port | `27017` | No |
| `MONGODB_USERNAME` | MongoDB username | - | No* |
| `MONGODB_PASSWORD` | MongoDB password | - | No* |
| `MONGODB_DATABASE` | Database name | `taskdb` | No |
| `SECRET_KEY` | Flask session secret key | - | Yes** |
| `PORT` | Application port | `5000` | No |

**Connection Methods (choose one):**
1. **Method 1 (Recommended for Kubernetes)**: Set `MONGODB_URI` with full connection string
   - Example: `mongodb://admin:password@hostname:27017/taskdb?authSource=admin`
   - Compatible with existing `cnap-tech-exercise-aws` deployment
2. **Method 2 (Alternative)**: Set individual variables (`MONGODB_HOST`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`)
3. **Method 3 (Local dev)**: Just set `MONGODB_HOST` (no authentication)

*At least one connection method must be configured  
**Required for production; auto-generated in development

For detailed examples, see:
- [ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) - Complete variable reference
- [MONGODB_URI_EXAMPLES.md](docs/MONGODB_URI_EXAMPLES.md) - Examples for AWS/GCP deployment

## 📊 MongoDB Schema

### Tasks Collection

```json
{
  "_id": ObjectId("..."),
  "title": "Deploy to production",
  "completed": false,
  "created_at": ISODate("2025-10-21T10:30:00.000Z"),
  "created_by_pod": "task-manager-7d8f9b5c-abc12",
  "updated_at": ISODate("2025-10-21T11:00:00.000Z"),
  "updated_by_pod": "task-manager-7d8f9b5c-def34"
}
```

## 🎨 Features Detail

### 1. Create Tasks
- Enter task title in the input field
- Click "Add Task" button
- Task is saved to MongoDB
- All pods see the new task immediately

### 2. Complete Tasks
- Click checkbox next to task
- Task is marked as completed (visual strikethrough)
- Completion status saved to MongoDB

### 3. Delete Tasks
- Click "Delete" button for individual task
- Confirmation prompt before deletion
- Or use "Delete All Tasks" to clear everything

### 4. Pod Identification
- Footer shows which pod served the request
- Refresh page multiple times to see load balancing
- Different pods will handle different requests

## 🧪 Testing

### Manual Testing

```bash
# Create a task
curl -X POST http://localhost:5000/create \
  -d "title=Test task"

# Delete a task (replace TASK_ID)
curl -X POST http://localhost:5000/delete/TASK_ID

# Delete all tasks
curl -X POST http://localhost:5000/delete-all
```

### Health Checks

```bash
# Liveness probe
curl http://localhost:5000/health

# Readiness probe
curl http://localhost:5000/ready
```

## 📦 Project Structure

```
task-manager-app/
├── src/
│   ├── app.py                 # Main Flask application
│   ├── templates/
│   │   ├── index.html        # Main task list page
│   │   └── error.html        # Error page
│   └── static/
│       └── style.css         # Styling
├── Dockerfile                # Multi-stage container build
├── requirements.txt          # Python dependencies
├── .dockerignore            # Docker build exclusions
├── .gitignore               # Git exclusions
└── README.md                # This file
```

## 🔐 Security Features

- ✅ **Non-root container user** (UID 1000)
- ✅ **Multi-stage Docker build** (smaller image)
- ✅ **No secrets in code** (environment variables)
- ✅ **Minimal base image** (Python 3.11-slim)
- ✅ **Health check endpoint** (container monitoring)
- ✅ **Cloud KMS integration** (AWS Secrets Manager / GCP Secret Manager)
- ✅ **Kubernetes Secret injection** (no hardcoded credentials)

⚠️ **Important**: See [SECURITY_BEST_PRACTICES.md](docs/SECURITY_BEST_PRACTICES.md) for production security guidelines.

**Note**: The test file `docker-compose.mongodb-uri.yml` contains demo credentials (`admin:password123`) for local testing only. These are clearly marked with warnings and must NEVER be used in production.

## 🚦 CI/CD Pipeline

GitHub Actions workflow automatically:
1. Builds Docker image on push to `main`
2. Runs tests (if present)
3. Pushes image to Docker Hub
4. Tags with commit SHA and `latest`

See `.github/workflows/build-and-push.yml` for details.

## 📈 Performance

- **Startup time**: ~5 seconds
- **Memory usage**: ~50MB per pod
- **Response time**: <50ms average
- **Concurrent users**: Scales horizontally

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Hideki**
- Portfolio Project: DevOps Engineer
- GitHub: [@110hideki](https://github.com/110hideki)

## � Deployment

This application is designed to be deployed via infrastructure repositories:

### Infrastructure Repositories
- **AWS**: [cnap-tech-exercise-aws](https://github.com/110hideki/cnap-tech-exercise-aws) - EKS deployment with Terraform
- **GCP**: [cnap-tech-exercise-gcp](https://github.com/110hideki/cnap-tech-exercise-gcp) - GKE deployment with Terraform

### How Deployment Works

The infrastructure repositories manage:
- Kubernetes cluster provisioning
- MongoDB deployment with authentication
- **Credential injection** from cloud KMS (AWS Secrets Manager / GCP Secret Manager)
- Kubernetes manifests with secrets management
- Load balancer configuration

See [DEPLOYMENT_INTEGRATION.md](docs/DEPLOYMENT_INTEGRATION.md) for detailed information on how MongoDB credentials are injected into the container at runtime.

### Container Image

- **Docker Hub**: `110hideki/task-manager-app:latest`
- **Build**: Automatic via GitHub Actions
- **Platforms**: linux/amd64, linux/arm64

## �🔗 Related Projects

- [cnap-tech-exercise-aws](https://github.com/110hideki/cnap-tech-exercise-aws) - AWS EKS infrastructure
- [cnap-tech-exercise-gcp](https://github.com/110hideki/cnap-tech-exercise-gcp) - GCP GKE infrastructure

## 📚 What I Learned

Building this project taught me:
- Stateless application design patterns
- Container orchestration with Kubernetes
- Multi-cloud deployment strategies
- CI/CD pipeline automation
- Infrastructure as Code principles
- Load balancing and horizontal scaling

## 🎯 Future Enhancements (Phase 2)

- [ ] User authentication
- [ ] Task assignments (multi-user)
- [ ] Task priorities (High/Medium/Low)
- [ ] Due dates and reminders
- [ ] Kanban board view (Todo/In Progress/Done)
- [ ] Task categories/tags
- [ ] REST API endpoints (JSON responses)
- [ ] Unit and integration tests

---

**Built with ❤️ for learning DevOps and cloud-native architecture**
