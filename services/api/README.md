# FieldOps Lab API service

This folder contains the first local API skeleton for the FieldOps Lab platform.

## Current status

The API is intentionally read-only.

It exposes generated reports to the future web interface, but it does not execute backend commands and does not modify project files.

This API does not prove scientific validity. It exposes engineering status, diagnostic reports, experimental design information, and quality-check status.

## Current endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Return API status, read-only mode, and available routes |
| GET | `/api/v1/project-status` | Return project status summary and quality-check status |
| GET | `/api/v1/reports` | Return available generated reports and quality checks |
| GET | `/api/v1/experimental-design-matrix` | Return experimental design matrix summary |

## Safety rule

The API must not expose arbitrary command execution.

Backend execution may only be added after an explicit allowlist model exists.

## Run self-test

```cmd
py -3 services\api\fieldops_api.py --self-test