# Task Manager App

A simple web application for managing tasks, built with Flask and MongoDB. Designed to demonstrate stateless application architecture and container deployment.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

## 🎯 Purpose

This application demonstrates:
- **Stateless application design** with external state management
- **Container deployment** patterns
- **MongoDB integration** with proper environment configuration
- **Production-ready** Flask application structure

## ✨ Features

- ✅ **Simple Task Management**: Create, complete, and delete tasks
- ✅ **Web UI**: Clean, responsive HTML interface
- ✅ **MongoDB Backend**: Persistent storage for tasks
- ✅ **Stateless Design**: Multiple instances share the same database
- ✅ **Health Checks**: Liveness and readiness probes
- ✅ **Production Ready**: Gunicorn WSGI server, non-root container user

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
│         Load Balancer                   │
│         (Optional)                      │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌──▼──┐ ┌──▼──┐
│App    │ │App  │ │App  │
│Instance│ │Inst.│ │Inst.│
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
export MONGODB_URI="mongodb://localhost:27017/taskdb"
export SECRET_KEY="your-development-secret-key"
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
# Run with MongoDB connection
docker run -d \
  --name task-manager \
  -p 5000:5000 \
  -e MONGODB_URI="mongodb://admin:password@host:27017/taskdb?authSource=admin" \
  -e SECRET_KEY="your-secure-secret-key" \
  task-manager-app:latest

# For local development with local MongoDB (no auth)
docker run -d \
  --name task-manager \
  -p 5000:5000 \
  -e MONGODB_URI="mongodb://host.docker.internal:27017/taskdb" \
  -e SECRET_KEY="dev-secret-key" \
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

## 🔧 Configuration

### Essential Environment Variables

The application requires two environment variables for MongoDB connection:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | **MongoDB connection string** | `mongodb://user:pass@host:27017/taskdb?authSource=admin` | **Yes** |
| `SECRET_KEY` | **Flask session secret key** | `your-secret-key-here` | **Yes** |

### Optional Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Application port | `5000` | No |

### Example Configuration

```bash
# Required environment variables
export MONGODB_URI="mongodb://admin:password@localhost:27017/taskdb?authSource=admin"
export SECRET_KEY="your-secure-secret-key-here"

# Optional
export PORT=5000
```

### Docker Environment Variables

```bash
docker run -d \
  --name task-manager \
  -p 5000:5000 \
  -e MONGODB_URI="mongodb://admin:password@host:27017/taskdb?authSource=admin" \
  -e SECRET_KEY="your-secure-secret-key" \
  task-manager-app:latest
```

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

⚠️ **Important**: Never hardcode credentials in code. Always use environment variables for sensitive information.

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

## 📚 What I Learned

Building this project taught me:
- Stateless application design patterns
- Container deployment strategies
- MongoDB integration patterns
- Flask web application development
- Production-ready application structure

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

**Built with ❤️ for learning Flask and MongoDB integration**
