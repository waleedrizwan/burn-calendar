---
id: BURN-023
title: Repository and environment setup
type: build
priority: must
requirement: 5. Someone else must be able to trust and judge it
timebox: 30m
status: in-progress
depends:
---

## First principle

Work that is not versioned can be lost, and work that cannot be re-run cannot be checked.

## What fails without this task

A mistake or a lost laptop erases progress, and nobody else can run the project.

## Description

Put the project under version control and make the environment reproducible.

## Acceptance criteria

- [ ] A git repository exists with a remote backup
- [ ] The remote repository is public, because the final project link must open without a login
- [x] `.gitignore` covers data files and `.env`
- [x] One documented command sets up the environment
- [x] The README states how to run the project

## Notes (Sat Nov 14)

- Local git repository created on branch `main`. Environment: `uv sync` (Python 3.12, FastAPI, DuckDB, pandas, pyarrow). Run and test commands are in the README.
- **Open, needs the owner:** creating the public GitHub repository and pushing. Command once approved: `gh repo create burn-calendar --public --source . --remote origin --push`. The first two criteria stay unticked until then.
