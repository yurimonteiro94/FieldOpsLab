# FieldOps Lab research framing

## Project question

How can a field service operation choose an appropriate replanning policy when operational disruptions occur during the execution of a dynamic TRSP or WSRP schedule?

The question is not only which policy obtains the best objective value in one instance.

The central question is how to decide which policy is more appropriate for each class of operational scenario, considering performance, stability, computational cost, severity of disruption, and practical equivalence between policies.

## Research gap

Dynamic technician routing, workforce scheduling and routing, and replanning have already been studied in the literature.

The gap addressed by this project is narrower.

The project focuses on the lack of a replicable experimental and decision framework that compares replanning policies under controlled dynamic disruptions, especially delay propagation, and converts the results into an explainable recommendation method for operational use.

The intended contribution is not just another solver.

The intended contribution is a method that links scenario characteristics to replanning policy choice.

## What the master's work does

The master's work develops and validates an experimental decision method for dynamic field operations.

The work has five main parts.

1. Define relevant dynamic scenarios and disruption classes.
2. Execute controlled computational experiments with alternative replanning policies.
3. Compare policies using performance, stability, and computational indicators.
4. Identify cases where policies are practically equivalent.
5. Produce an explainable recommendation for which policy should be used in each scenario class.

The final method should be usable with real or realistic company data.

## What the system does

FieldOps Lab is the experimental platform used to support the research.

The system is not the scientific contribution by itself.

The system exists to generate, execute, inspect, and validate experiments in a reproducible way.

It supports or will support the following functions.

- Define field service instances.
- Define dynamic perturbation plans.
- Generate controlled experiment campaigns.
- Execute policies against the same scenarios.
- Produce reports, rankings, diagnostics, and quality checks.
- Expose results through a read-only local API.
- Present engineering and scientific status through a web dashboard.
- Support later validation with real company data.

## What has already been done

The current implementation already contains a working engineering foundation.

Completed items include:

- C and C++ core structure.
- CMake and Ninja build flow.
- Unit tests for the C and C++ core.
- Dynamic perturbation concepts.
- Travel delay and service delay perturbation handling.
- Replanning request and result structures.
- Greedy replanning solver structure.
- Policy abstractions.
- No-replanning policy.
- Threshold delay replanning policy.
- Batch experiment and ranking artifacts.
- Generated campaign reports.
- Generated quality reports.
- Python report generators and verifiers.
- Project quality gate script.
- Full campaign pipeline execution.
- Read-only local HTTP API.
- Web dashboard connected to the read-only API.
- Local platform smoke check.
- Conservative scientific warnings in the platform interface.

## What still needs to be done

The current system is not a finished scientific or production platform.

Important missing items include:

- More realistic field service data model.
- Import flow for real company data.
- Stronger scenario classification.
- More replanning policies.
- Stronger statistical comparison.
- Practical equivalence criteria between policies.
- Decision method for recommending policies by scenario class.
- Better visualization of experiments and results.
- More complete web interface.
- Cloud deployment.
- Firebase Hosting.
- Cloud Run or equivalent API deployment.
- Authentication or access control if real company data is used.
- Data privacy controls.
- External validation with real or realistic company data.
- Final academic analysis and dissertation writing.

## Policy comparison principle

A policy should not be declared better only because it has a slightly better average value.

When two policies produce very similar results, the system should treat the difference conservatively.

The comparison should consider practical equivalence, statistical evidence, operational robustness, and implementation cost.

A simpler policy can be preferred when it performs almost the same as a more complex policy.

## Role of fuzzy logic

Fuzzy logic is not mandatory for this project.

It should only be used if it helps express scenario classification or decision rules in a clearer and more defensible way.

If standard statistical comparison, thresholds, dominance rules, or multi-criteria scoring are enough, fuzzy logic should not be forced into the work.

## Conservative interpretation

Passing engineering tests does not prove the scientific contribution.

Generated reports and dashboards are evidence of reproducibility and implementation quality.

Scientific validity still depends on the research design, the experimental campaign, the statistical analysis, and the quality of the real or realistic validation data.