# IBM DevOps Capstone — Customer Accounts Microservice

[![CI Build](https://github.com/kirshanharivelmwork/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg?branch=main)](https://github.com/kirshanharivelmwork/devops-capstone-project/actions/workflows/ci-build.yaml)

A public project for the **IBM DevOps Capstone Project**, implementing a RESTful Customer Accounts microservice for an e-commerce platform.

## Project overview

The service supports account creation, listing, reading, updating, and deletion. It is being developed through Agile planning, automated testing, continuous integration, containerization, Kubernetes/OpenShift deployment, and Tekton continuous delivery.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/accounts` | Create an account |
| GET | `/accounts` | List accounts |
| GET | `/accounts/{id}` | Read an account |
| PUT | `/accounts/{id}` | Update an account |
| DELETE | `/accounts/{id}` | Delete an account |

## Tech stack

- Python, Flask, Flask-SQLAlchemy, Flask-CORS
- SQLite for local development and tests; configurable database URL for PostgreSQL
- Flake8 and pytest for code quality and automated tests
- GitHub Actions workflow in [`.github/workflows/ci-build.yaml`](.github/workflows/ci-build.yaml)

## Run locally

```bash
python -m pip install -r requirements.txt
flask --app service run --port 5000
```

## Test and continuous integration

```bash
flake8 service tests
python -m pytest -v tests
```

The CI Build workflow runs on pushes and pull requests to `main`. The badge at the top shows **GitHub's real workflow status**; it does not represent a manually assigned grade.

## Capstone progress

The application and initial automated tests are implemented. Agile board evidence, OpenShift deployment, and Tekton pipeline execution will be completed and documented in subsequent tasks.
