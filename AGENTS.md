# Repository guidance

## Project files and temporary work

- Keep final requirements, implementation documentation, and supporting evidence in `docs/`; keep intentional manufacturing deliverables in `manufacturing/`.
- Put intermediate working artifacts, temporary exports, routing candidates, logs, disposable fixtures, downloaded inspection copies, and agent-only scripts in the repository-root `.agent-scratch/` directory. Do not scatter them through project directories.
- Use a task-specific subdirectory within `.agent-scratch/`. Keep it clean during work and remove obsolete or reproducible temporary files when the task finishes. Retain only scratch material needed for active work or an explicitly requested local archive, and identify any retained material in the handoff.
- Before deleting or recursively moving scratch content, verify the resolved absolute path is inside this repository's `.agent-scratch/`. Never delete unrelated user files.
- `.agent-scratch/` is ignored by Git. Final documentation and committed tools must not depend on files there. Promote necessary final evidence to an appropriate project directory before referencing it.
- Put intentionally maintained, reusable project scripts in `tools/`, with usage and dependencies documented. Agent-only experiments belong in `.agent-scratch/`, even when written as scripts.
- Ignore Python bytecode and cache directories. Do not commit automatic backups, local preferences, lock files, or editor history.
- Preserve unrelated user changes. Do not stage, commit, or remove files unless requested.

## KiCad design integrity

- Follow the applicable KiCad/Konnect skills. Use Konnect tools for modifications to KiCad design files, libraries, and library tables; do not edit their serialized contents with text manipulation.
- Keep design sources, required project libraries, library tables, and design rules under version control.
- Distinguish final verification evidence from historical results; do not present an earlier revision's checks as validation of the current design.
