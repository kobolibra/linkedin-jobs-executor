# LinkedIn Jobs Executor

A public GitHub Actions execution project for scheduled LinkedIn job collection and lifecycle processing.

## Scope

The executor supports two explicit run modes:

- `cn`: China-only collection and enrichment.
- `expanded`: China, Hong Kong, and Singapore collection for lifecycle and expiry tracking.

JD and city enrichment remain **China-only**. Hong Kong and Singapore records are used for listing and lifecycle fields without requesting their detail pages or populating China-only enrichment fields.

## Workflow

The `run-jobspy.yml` workflow is started through `workflow_dispatch`. It validates the requested scope, runs the configured company searches, preserves the last known good snapshot when a collection window returns no usable results, and publishes only the intended execution output through the configured delivery path.

The workflow is designed to keep credentials, source data, generated payloads, and operational state out of this public repository. Runtime access is provided through protected GitHub Actions secrets, and logs must not contain credentials or sensitive job payloads.

## Operational notes

Use `cn` for the short, frequent collection windows and `expanded` for the longer regional lifecycle pass. Do not commit generated snapshots, credentials, or environment-specific configuration to this repository.

## License and contribution

Public contributions should be limited to generic workflow, tooling, and reliability improvements and must not include operational data or credentials.

## Security

Report suspected credential exposure or sensitive-data leakage privately to the repository owner. Never post tokens, passwords, job data, or generated operational artifacts in issues or pull requests.

<!-- This public README intentionally documents capabilities only and omits deployment topology, source repositories, secret names, and storage details. -->
