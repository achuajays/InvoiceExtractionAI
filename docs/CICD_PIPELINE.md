# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and continuous deployment. The CI/CD pipeline helps maintain code quality, security, and automates branch management.

## Workflows

### 1. Code Quality

**File:** `.github/workflows/code-quality.yml`

**Triggers:**
- Push to any branch
- Pull requests to any branch

**Jobs:**
- Checks code formatting with Black
- Verifies import order with isort
- Lints code with Flake8

### 2. Docker Image Build and Scan

**File:** `.github/workflows/docker-image-scan.yml`

**Triggers:**
- Push to main branch
- Pull requests to main branch

**Jobs:**
- Builds Docker image
- Scans Docker image for vulnerabilities using Trivy

### 3. Secret Scan

**File:** `.github/workflows/secret-scan.yml`

**Triggers:**
- Push to any branch
- Pull requests to any branch

**Jobs:**
- Scans codebase for exposed secrets using GitLeaks

### 4. Branch Cleanup After Development Merge

**File:** `.github/workflows/branch-cleanup.yml`

**Triggers:**
- When a pull request is closed and merged into the development branch

**Jobs:**
- Deletes PR branches after they are merged into the development branch

## Branch Strategy

This project follows a simplified Git flow with the following branches:

- **main**: Production-ready code
- **development**: Integration branch for features and fixes
- **feature/***:  Feature branches (created from development, merged back to development)

## Workflow

1. Create a feature branch from development
2. Implement changes and push to the feature branch
3. Create a pull request to merge into development
4. After review and approval, merge the PR
5. The branch cleanup workflow will automatically delete the feature branch
6. When ready for production, create a PR from development to main

## Adding New Workflows

To add a new workflow:

1. Create a new YAML file in the `.github/workflows/` directory
2. Define the workflow triggers, jobs, and steps
3. Commit and push the changes

## Troubleshooting

If a workflow fails:

1. Check the GitHub Actions logs for error details
2. Fix the issues in your local environment
3. Push the changes to trigger the workflow again