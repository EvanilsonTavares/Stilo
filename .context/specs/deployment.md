# Spec: Mission 4 - Cloud Run Ready Deployment

## Goal
Prepare the Stilo monorepo for production deployment on Google Cloud Platform (GCP) using Cloud Run, ensuring scalability, security, and automated delivery.

## Requirements
- **Containerization**: Create optimized `Dockerfile`s for both `frontend` and `backend`.
- **Infrastructure as Code**: Define a `docker-compose.yml` for local multi-container orchestration.
- **Continuous Deployment**: Create a `cloudbuild.yaml` for automated builds and deploys to Cloud Run.
- **Security**: Refactor the backend to support Google Secret Manager for sensitive API keys.
- **Networking**: Configure the frontend to point to the Cloud Run service URL in production.

## Technical Details
- **Architecture**:
  - Frontend: Served via Nginx or as a static site.
  - Backend: FastAPI (Uvicorn) running in a managed container.
- **Environment Variables**:
  - `ENV`: `development` or `production`.
  - `GCP_PROJECT_ID`: Target project for Secret Manager.

## Definition of Done (DoD)
- [ ] Both frontend and backend can be started via a single `docker-compose up` command.
- [ ] `Dockerfile`s are optimized (multi-stage builds).
- [ ] Backend logic successfully falls back to Secret Manager when `.env` is missing (production mode).
- [ ] `cloudbuild.yaml` is valid and ready for GCP integration.
