# Git Specification

The Git workflow for this project and the `fivecircles` directory follows the central strategy defined in the root documentation.

## Authoritative Reference
- **Document**: `docs/GIT_STRATEGY.md`
- **Agent Rule**: `.agent/rules/git-style-guide.md`

## Summary of Principles
- **Base Branch**: `develop`
- **Branch Naming**: `feat/`, `fix/`, `refactor/`, `docs/`
- **Commits**: Follow Conventional Commits format (`type: description`)
- **Safety**: No direct commits to `main` or `develop`; use PRs.

Any `fivecircles` specific development must be performed in its own task branch branched off from `develop`.
