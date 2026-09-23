# LinkedIn Jobs Executor

This repository is a **public Actions runner project** for the private canonical repository `kobolibra/linkedin-jobs-page`.

## Security boundary

This repository must never contain canonical jobs data, JobSpy history, RSS snapshots, private credentials, or generated frontend payloads. The workflow checks out the private repository into a temporary runner directory, performs the CN-only JobSpy pipeline, and pushes only the intended result files back to the private repository.

The required secret is `PRIVATE_REPO_TOKEN`. It must be limited to the private repository with Contents read/write and Metadata read. Do not use a token with administration, visibility, Actions-write, or repository-deletion permissions.

## Current migration status

The executor repository is bootstrapped before enabling cross-repository writes. The private repository remains the source of truth. The migration preserves the original China-only JobSpy behavior and does not add HK or SG searches.

## First-run procedure

Configure `PRIVATE_REPO_TOKEN` as an Actions secret, then perform a controlled manual run. Confirm that the private repository receives only the intended snapshot files, that no public artifacts are created, and that logs contain no private payloads. Keep the private repository's existing workflow enabled until this executor has been validated; only then disable the private daily path.

## Non-negotiable rules

- Do not commit private data, artifacts, or state here.
- Do not upload private snapshots as public workflow artifacts.
- Do not print private feed URLs, job payloads, or credentials in logs.
- Use the separate `linkedin-private-writer` concurrency group.
