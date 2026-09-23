# LinkedIn Jobs Executor

This repository is a **public Actions runner project** for the private canonical repository `kobolibra/linkedin-jobs-page`.

## Security boundary

This repository must never contain canonical jobs data, JobSpy history, RSS snapshots, private credentials, or generated frontend payloads. The workflow checks out the private repository into a temporary runner directory, performs the CN-only JobSpy pipeline there, and pushes only the intended result files back to the private repository.

The required secret is `PRIVATE_REPO_TOKEN`. It must be limited to the private repository with Contents read/write and Metadata read. Do not use a token with administration or visibility permissions.

## Current migration status

The executor repository is intentionally bootstrapped before enabling cross-repository writes. The private repository remains the source of truth. The migration must preserve the original China-only JobSpy behavior and must not add HK or SG searches.

## Non-negotiable rules

- Do not commit private data, artifacts, or state here.
- Do not upload private snapshots as public workflow artifacts.
- Do not print private feed URLs, job payloads, or credentials in logs.
- Keep the private repository's daily workflows disabled after this executor is validated, so the private repository does not consume Actions minutes.
- Use a separate concurrency group for the private writer.
