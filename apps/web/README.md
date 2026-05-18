# FieldOps Lab web interface

This folder will contain the web interface for FieldOps Lab.

## Initial role

The first web interface should be a dashboard for inspecting the current state of the platform.

It should not pretend that the project is already a complete scientific or commercial platform.

## Planned first pages

| Page | Purpose |
| --- | --- |
| Dashboard | Show engineering status, scientific status, and report availability |
| Reports | List generated reports and quality checks |
| Experimental design | Show the planned experimental design matrix |
| Scientific validation | Show open scientific risks and validation actions |

## Required message to users

The interface must clearly separate:

- structural engineering consistency;
- diagnostic evidence;
- scientific validation still pending.

## Next implementation step

After the API skeleton exists, create a first dashboard page that consumes the API locally.