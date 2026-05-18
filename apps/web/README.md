# FieldOps Lab web interface

This folder contains the web interface for FieldOps Lab.

Current product completeness estimate: 39%.

## Current stage

The current web app is a read-only dashboard skeleton.

It is intentionally conservative:

- it does not execute backend commands;
- it does not expose experiment execution;
- it does not claim scientific validity;
- it shows engineering and diagnostic status only;
- it prepares the structure for future API, Firebase, hosting, and execution workflows.

## Architecture

The current structure follows a simple MVVM-inspired organization:

| Folder | Role |
| --- | --- |
| `src/domain` | Shared domain types and platform models |
| `src/services` | Data access adapters |
| `src/viewModels` | Screen state and view logic |
| `src/components` | Reusable UI components |
| `src/pages` | Application pages |
| `src/__tests__` | Frontend unit tests |

## Current data source

The current dashboard uses a static read-only adapter.

Future versions should replace this adapter with an HTTP client for the Python API without changing the page structure.

## Local commands

Install dependencies:

```cmd
npm install
This dashboard does not prove scientific validity.
