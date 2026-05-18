# FieldOps Lab platform delivery plan

This document defines the transition from a local research pipeline to a usable web-based experimental platform.

## Conservative status

The current project has a strong local engineering and diagnostic pipeline, but it is not yet a complete end-user application.

Current estimated product completeness: 33%.

This percentage refers to the complete application, including web interface, API, hosting, Firebase integration, backend execution, experiment management, reporting, deployment, and final user readiness.

## Product goal

FieldOps Lab should become a web-based experimental platform for dynamic TRSP and WSRP operations.

The platform should allow a user to:

- define or import operational instances;
- define perturbation scenarios;
- choose or compare replanning policies;
- execute experimental campaigns;
- inspect diagnostic reports;
- export scientific and operational evidence;
- separate engineering consistency from scientific validity.

## Main platform layers

| Layer | Purpose | Current status |
| --- | --- | --- |
| Core engine | Execute instance validation, perturbations, policies, comparisons, and reports | partially implemented locally |
| Analysis pipeline | Generate diagnostic, ranking, experimental design, and validation reports | partially implemented locally |
| API service | Expose controlled backend operations to the web interface | planned |
| Web interface | Allow users to configure, run, and inspect experiments | planned |
| Storage | Persist inputs, outputs, campaigns, reports, and user files | planned |
| Hosting and deployment | Make the platform accessible outside the local machine | planned |
| Authentication and project isolation | Protect user data and separate experiments by user/project | planned |

## Delivery milestones

### Milestone 1: Platform contract

Define stable contracts between the future web interface, API service, backend engine, and generated artifacts.

Acceptance criteria:

- platform contract JSON exists;
- API responsibilities are explicitly listed;
- web interface responsibilities are explicitly listed;
- tests verify the platform contract.

### Milestone 2: Local API skeleton

Create a minimal API service that can expose project status and available generated reports.

Acceptance criteria:

- API can run locally;
- API can return a health response;
- API can expose a list of available reports;
- tests verify response structure.

### Milestone 3: Web dashboard skeleton

Create the first web dashboard page.

Acceptance criteria:

- page opens locally;
- page shows project status;
- page shows links or cards for generated reports;
- page clearly states that the current evidence is diagnostic, not scientific proof.

### Milestone 4: Execution bridge

Connect the API to safe backend execution commands.

Acceptance criteria:

- API can trigger only approved scripts;
- commands are controlled by allowlist;
- no arbitrary shell command execution is exposed;
- generated outputs are stored in predictable paths.

### Milestone 5: Storage and persistence

Introduce persistent storage for campaigns, inputs, outputs, and reports.

Acceptance criteria:

- storage layout is documented;
- local storage abstraction exists;
- Firebase or cloud storage can be added behind the same interface.

### Milestone 6: Hosted prototype

Deploy a basic version of the web interface and API.

Acceptance criteria:

- web interface is hosted;
- API is reachable by the web interface;
- environment variables and deployment steps are documented;
- no sensitive data is hardcoded.

### Milestone 7: User-ready research platform

Allow a real user to configure, execute, inspect, and export experiments.

Acceptance criteria:

- user can run a complete workflow without using the command line;
- errors are understandable;
- reports are accessible from the UI;
- execution is auditable;
- scientific limitations remain visible.

## Safety and reliability rules

The platform must not expose arbitrary command execution.

The platform must not claim scientific validity from diagnostic-only reports.

The platform must not overwrite user data without explicit control, predictable output paths, and recoverable artifacts.

The platform must keep generated reports traceable to their inputs, scripts, and quality checks.

## Next recommended implementation step

Create the local API skeleton after this contract is committed.

The API should start small:

- health endpoint;
- project status endpoint;
- reports index endpoint;
- no write operations at first;
- no backend execution endpoint until the allowlist model is defined.
This platform contract does not prove scientific validity.
