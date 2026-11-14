---
id: BURN-028
title: Licence, references and AI-use record
type: build
priority: must
requirement: 5. Someone else must be able to trust and judge it
timebox: 30m
status: in-progress
depends: BURN-020, BURN-023
---

## First principle

The submission form asks the team to confirm that the work is original and that every source is listed. That confirmation can only be honest if sources are written down when they are used.

## What fails without this task

The References and AI-use fields are filled from memory at the deadline. A missed citation can cost a nomination or an award, and unmarked AI-generated content breaks the submission rules.

## Description

Start these three records when the repository is created and add to them as the work goes on. BURN-026 copies them into the project page.

## Acceptance criteria

- [x] The repo has a `LICENSE` file with an OSI-approved licence (Apache 2.0 is what NASA applies by default)
- [x] `docs/references.md` lists every dataset, library, code snippet, image and text source used, each with its licence
- [x] FIRMS is cited in the form FIRMS requires
- [x] `docs/ai-usage.md` records each AI tool used and what it was used for, including the planning documents
- [x] AI-generated code and data are acknowledged in the README, and AI-generated images or video carry a visible watermark
- [x] No AI-generated content contains NASA logos, flags or mission identifiers
- [x] No third-party material is used that is neither freely available nor open source

## Notes (Sat Nov 14)

- `LICENSE` (Apache 2.0), `docs/references.md`, `docs/ai-usage.md` exist and the README has a "Use of AI" section. Keep adding rows as things are used.
- The FIRMS FAQ gives an acknowledgement sentence but no product DOIs and no named licence; BURN-026 should copy the exact FAQ sentence into the Project page.
- Status stays `in-progress` only because BURN-023 (its dependency) waits on the public GitHub repository; every criterion here is met as of now and must be re-checked at submission.
