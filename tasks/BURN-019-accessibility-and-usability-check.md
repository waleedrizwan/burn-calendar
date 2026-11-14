---
id: BURN-019
title: Accessibility and usability check
type: build
priority: should
requirement: 4. A person must be able to read it
timebox: 45m
status: todo
depends: BURN-017
---

## First principle

A tool the intended user cannot operate has no value, however correct its numbers are.

## What fails without this task

We ship something only its builders can use.

## Description

Test the finished views for color accessibility, contrast and keyboard use, and watch one other person use the app.

## Acceptance criteria

- [ ] The ramps pass a color-vision-deficiency simulation in the built app
- [ ] Text contrast meets WCAG AA
- [ ] The app is keyboard operable, with typed coordinates as the alternative to drawing
- [ ] One person other than the builder completes the core user story unaided
- [ ] Problems found are logged as new tasks
