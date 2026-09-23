# LinkedIn Jobs Executor

This public repository is the execution-only runner for the private canonical repository `kobolibra/linkedin-jobs-page`.

## JobSpy scope

The executor runs each configured company search in China (`CN`), Hong Kong (`HK`), and Singapore (`SG`). Lifecycle snapshots and expiry decisions are region-aware: a failed or blocked search in one region cannot expire jobs in another region.

**JD and city enrichment are strictly CN-only.** HK and SG rows carry listing/lifecycle fields only. The executor does not request their detail pages and does not write their city or description fields.

## Security boundary

The private repository remains the source of truth. This workflow checks it out into a temporary runner directory, runs JobSpy, and pushes only the intended JobSpy snapshot/history files back to the private repository. This public repository must never contain canonical jobs data, JobSpy history, RSS snapshots, private credentials, or generated frontend payloads.

The required Actions secret is `PRIVATE_REPO_TOKEN`. Use a fine-grained token limited to `kobolibra/linkedin-jobs-page` with Contents read/write and Metadata read. It does not need administration, visibility, Actions-write, or repository-deletion permission.

The private repository's `jobspy-incremental.yml` is a lightweight compatibility dispatcher. Its `PUBLIC_EXECUTOR_TOKEN` must be allowed to dispatch workflows in this public executor if the existing external scheduler continues to target the private workflow. The external scheduler may also dispatch this public workflow directly.

No public artifact contains snapshots or job payloads; persistent output is written only to the private canonical repository.
