# FieldOps Lab API service

This folder contains the API layer for the FieldOps Lab platform.

Current product completeness estimate: 44%.

## Current stage

The current API is read-only.

It exposes existing generated reports to the future web interface without allowing arbitrary execution.

This API does not prove scientific validity. It only exposes the current engineering, diagnostic, and validation-report state.

## Current local endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Return API status and contract version |
| GET | `/api/v1/project-status` | Return project status summary |
| GET | `/api/v1/reports` | Return available report paths and quality checks |
| GET | `/api/v1/experimental-design-matrix` | Return experimental design matrix summary |

## Safety rule

The current API must remain read-only.

It must not expose arbitrary command execution.

It must not expose experiment execution endpoints yet.

Backend execution may only be added after an explicit allowlist model exists.

## Local commands from the project root

Run the API self-test:

```cmd
py -3 services\api\fieldops_http_server.py --self-test