# FieldOps Lab read-only API container

This folder contains the initial Cloud Run container scaffold for the FieldOps Lab read-only API.

The container is intentionally limited to inspection endpoints. It exposes contracts, reports, samples, and readiness information, but it does not run solvers, does not start experiments, does not mutate schedules, does not write files, does not deploy resources, and does not trigger backend jobs.

This scaffold is useful for preparing the future API hosting layer, but it does not make the full FieldOps Lab system production-ready.

The real execution layer is still future work. That future layer must include controlled backend jobs, explicit execution boundaries, solver integration, experiment orchestration, persistent storage, monitoring, authentication decisions, and rollback procedures.

Remaining work includes the production web hosting configuration, Cloud Run deployment validation, API URL wiring for the frontend, post-deploy smoke tests, future authenticated execution endpoints, future solver-backed jobs, OR-Tools-backed solver integration, statistical analysis pipeline, storage integration, monitoring, and rollback procedures.

## Current target

The current target is a Cloud Run service serving the read-only HTTP API.

Current read-only endpoints include:

- `/api/v1/health`
- `/api/v1/project-status`
- `/api/v1/reports`
- `/api/v1/experimental-design-matrix`
- `/api/v1/research-method`
- `/api/v1/simulation-state-contract`
- `/api/v1/simulation-state-sample`
- `/api/v1/delay-injection-request-contract`
- `/api/v1/replanning-decision-response-contract`
- `/api/v1/replanning-decision-response-sample`
- `/api/v1/simulation-playback-control-contract`
- `/api/v1/simulation-playback-state-sample`
- `/api/v1/solver-integration-contract`
- `/api/v1/comparative-analysis-contract`
- `/api/v1/comparative-analysis-sample`
- `/api/v1/deployment-readiness-contract`

## Local build command

Run from the repository root:

```cmd
docker build -f deploy\cloud-run\read_only_api.Dockerfile -t fieldops-read-only-api .
```

## Local run command

Run only after the image has been built:

```cmd
docker run --rm -p 8080:8080 -e PORT=8080 fieldops-read-only-api
```

This command starts the read-only API locally on port 8080. It does not run solvers, does not start experiments, does not mutate schedules, does not write files, does not deploy resources, and does not trigger backend jobs.

## Local smoke test command

Use another terminal while the container is running:

```cmd
curl http://127.0.0.1:8080/api/v1/health
```

The expected result is an HTTP JSON response with status `ok`, `read_only` set to `true`, and execution disabled.

## Future Cloud Run deploy command

The future deploy command will use `gcloud run deploy`, but this README does not force deployment now.

## Future deployment command template

Do not run it until the Google Cloud project, billing, region, container registry, service visibility, and post-deploy smoke tests are explicitly confirmed and the image has been smoke-tested successfully.

```cmd
gcloud run deploy fieldops-read-only-api --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/fieldops-read-only-api:TAG --platform managed --region REGION --allow-unauthenticated
```

Before using a real command, replace `REGION`, `PROJECT_ID`, `REPOSITORY`, and `TAG`, confirm the Google Cloud project, confirm billing, confirm the deployment region, and confirm whether unauthenticated public access is acceptable.

## Required smoke tests after deploy

Required smoke tests after deploy must verify at least:

- `/api/v1/health` returns HTTP 200.
- `/api/v1/project-status` returns HTTP 200.
- `/api/v1/reports` returns HTTP 200.
- `/api/v1/deployment-readiness-contract` returns HTTP 200.
- Unknown report requests still return HTTP 404.
- POST requests still return HTTP 405.
- The deployed API still reports `read_only` as `true`.
- The deployed API still reports execution as disabled.
- The deployed API still does not run solvers, does not start experiments, does not mutate schedules, does not write files, and does not trigger backend jobs.

## Production caution

This container scaffold only prepares the read-only API for container-based hosting. It is not the full FieldOps Lab system.

The full production system still needs the real execution layer, solver-backed jobs, OR-Tools-backed solver integration, experiment orchestration, statistical analysis pipeline, storage, frontend API wiring, deployment automation, monitoring, authentication decisions, cost controls, and rollback procedures.