# FieldOps Lab API service

This folder will contain the API layer for the FieldOps Lab platform.

## Initial role

The first API version should be read-only.

It should expose existing generated reports to the future web interface without allowing arbitrary execution.

## Planned initial endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Return API status and contract version |
| GET | `/api/v1/project-status` | Return project status summary |
| GET | `/api/v1/reports` | Return available report paths and quality checks |
| GET | `/api/v1/experimental-design-matrix` | Return experimental design matrix summary |

## Safety rule

Do not expose an endpoint that executes arbitrary local commands.

Backend execution may only be added after an explicit allowlist model exists.

## Next implementation step

Create a minimal local API skeleton that reads JSON files from `analysis/reports`.

The first API implementation should not modify files.