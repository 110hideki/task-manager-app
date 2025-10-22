# Documentation

This directory contains comprehensive documentation for the Task Manager application.

## 📚 Documentation Index

### Getting Started

- **[../README.md](../README.md)** - Main project documentation, quick start guide

### Deployment Guides

- **[MONGODB_URI_EXAMPLES.md](MONGODB_URI_EXAMPLES.md)** ⭐ **Start here for deployment**
  - Step-by-step guide for AWS and GCP deployment
  - How to create secrets from Terraform variables
  - Scripts and automation examples

- **[DEPLOYMENT_INTEGRATION.md](DEPLOYMENT_INTEGRATION.md)**
  - Architecture overview
  - How infrastructure repos inject credentials
  - Terraform integration patterns

- **[KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)**
  - Complete Kubernetes deployment reference
  - Troubleshooting guide
  - Cloud-specific notes

### Configuration

- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)**
  - Complete environment variable reference
  - All 3 MongoDB connection methods explained
  - Examples for each method
  - Docker Compose and Kubernetes examples

- **[MONGODB_URI_FORMAT.md](MONGODB_URI_FORMAT.md)** ℹ️ **Format clarification**
  - Explains both MONGODB_URI formats (with and without `/taskdb`)
  - How the application handles each format
  - Testing examples for both formats

### Security

- **[SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)** ⚠️ **Read before production deployment**
  - Secret management (AWS/GCP KMS)
  - Password requirements and generation
  - Kubernetes security hardening
  - Secret rotation procedures
  - What to do if credentials leak
  - Compliance checklist

- **[../SECURITY.md](../SECURITY.md)**
  - Security policy
  - Reporting vulnerabilities

### Planning

- **[FUTURE_ENHANCEMENTS.md](FUTURE_ENHANCEMENTS.md)**
  - Roadmap for Phase 2-8
  - Authentication implementation
  - Advanced features
  - Monitoring and observability

- **[SUMMARY.md](SUMMARY.md)**
  - Complete project overview
  - Architecture and design decisions
  - Key features and testing results

## 🔒 Security Notice

⚠️ **Important**: The repository contains a test file `docker-compose.mongodb-uri.yml` with **demo credentials** for local testing only.

**These are clearly marked with warnings and should NEVER be used in production.**

For production deployments:
1. Read [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)
2. Store credentials in cloud KMS (AWS Secrets Manager / GCP Secret Manager)
3. Use strong, randomly generated passwords
4. Follow the deployment guides for proper secret injection

## 🚀 Quick Navigation

### I want to...

**Deploy to AWS EKS:**
1. Read [MONGODB_URI_EXAMPLES.md](MONGODB_URI_EXAMPLES.md) - AWS section
2. Follow the step-by-step guide
3. Review [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)

**Deploy to GCP GKE:**
1. Read [MONGODB_URI_EXAMPLES.md](MONGODB_URI_EXAMPLES.md) - GCP section
2. Choose Option 1 (MONGODB_URI) or Option 2 (individual variables)
3. Review [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)

**Understand environment variables:**
→ [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)

**Configure MongoDB connection:**
→ [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) - See the 3 connection methods

**Troubleshoot deployment:**
→ [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) - Troubleshooting section

**Secure the application:**
→ [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)

**Plan future enhancements:**
→ [FUTURE_ENHANCEMENTS.md](FUTURE_ENHANCEMENTS.md)

**See project overview:**
→ [SUMMARY.md](SUMMARY.md)

## 📖 Reading Order

For first-time users:

1. **[../README.md](../README.md)** - Understand what the app does
2. **[SUMMARY.md](SUMMARY.md)** - See the big picture
3. **[MONGODB_URI_EXAMPLES.md](MONGODB_URI_EXAMPLES.md)** - Deploy to your cloud
4. **[SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)** - Secure your deployment
5. **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Reference when needed

## 🔄 Updates

Documentation last updated: 2025-10-22

All documentation is kept in sync with the application code in `src/app.py`.
