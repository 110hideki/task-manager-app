# Documentation

This directory contains comprehensive documentation for the Task Manager application.

## 📚 Documentation Index

### Getting Started

- **[../README.md](../README.md)** - Main project documentation, quick start guide

### Deployment Guides

- **[mongodb_uri_examples.md](mongodb_uri_examples.md)** ⭐ **Start here for deployment**
  - Step-by-step guide for AWS and GCP deployment
  - How to create secrets from Terraform variables
  - Scripts and automation examples

- **[deployment_integration.md](deployment_integration.md)**
  - Architecture overview
  - How infrastructure repos inject credentials
  - Terraform integration patterns

### Configuration

- **[environment_variables.md](environment_variables.md)**
  - Complete environment variable reference
  - All 3 MongoDB connection methods explained
  - Examples for each method
  - Docker Compose and Kubernetes examples

- **[mongodb_uri_format.md](mongodb_uri_format.md)** ℹ️ **Format clarification**
  - Explains both MONGODB_URI formats (with and without `/taskdb`)
  - How the application handles each format
  - Testing examples for both formats

### Security

- **[security_best_practices.md](security_best_practices.md)** ⚠️ **Read before production deployment**
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

- **[future_enhancements.md](future_enhancements.md)**
  - Roadmap for Phase 2-8
  - Authentication implementation
  - Advanced features
  - Monitoring and observability

- **[summary.md](summary.md)**
  - Complete project overview
  - Architecture and design decisions
  - Key features and testing results

## 🔒 Security Notice

⚠️ **Important**: The repository contains a test file `docker-compose.mongodb-uri.yml` with **demo credentials** for local testing only.

**These are clearly marked with warnings and should NEVER be used in production.**

For production deployments:
1. Read [security_best_practices.md](security_best_practices.md)
2. Store credentials in cloud KMS (AWS Secrets Manager / GCP Secret Manager)
3. Use strong, randomly generated passwords
4. Follow the deployment guides for proper secret injection

## 🚀 Quick Navigation

### I want to...

**Deploy to AWS EKS:**
1. Read [mongodb_uri_examples.md](mongodb_uri_examples.md) - AWS section
2. Follow the step-by-step guide
3. Review [security_best_practices.md](security_best_practices.md)

**Deploy to GCP GKE:**
1. Read [mongodb_uri_examples.md](mongodb_uri_examples.md) - GCP section
2. Choose Option 1 (MONGODB_URI) or Option 2 (individual variables)
3. Review [security_best_practices.md](security_best_practices.md)

**Understand environment variables:**
→ [environment_variables.md](environment_variables.md)

**Configure MongoDB connection:**
→ [environment_variables.md](environment_variables.md) - See the 3 connection methods

**Troubleshoot deployment:**
→ [deployment_integration.md](deployment_integration.md) - Architecture and integration patterns

**Secure the application:**
→ [security_best_practices.md](security_best_practices.md)

**Plan future enhancements:**
→ [future_enhancements.md](future_enhancements.md)

**See project overview:**
→ [summary.md](summary.md)

## 📖 Reading Order

For first-time users:

1. **[../README.md](../README.md)** - Understand what the app does
2. **[summary.md](summary.md)** - See the big picture
3. **[mongodb_uri_examples.md](mongodb_uri_examples.md)** - Deploy to your cloud
4. **[security_best_practices.md](security_best_practices.md)** - Secure your deployment
5. **[environment_variables.md](environment_variables.md)** - Reference when needed

## 🔄 Updates

Documentation last updated: 2025-10-22

All documentation is kept in sync with the application code in `src/app.py`.
