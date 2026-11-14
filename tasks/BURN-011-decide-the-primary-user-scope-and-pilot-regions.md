---
id: BURN-011
title: Decide the primary user, scope and pilot regions
type: brainstorm
priority: must
requirement: 4. A person must be able to read it
timebox: 30m
status: done
depends:
---

## First principle

A tool is useful only in relation to a specific person's decision. Emergency responders, scientists and land managers ask different questions.

## What fails without this task

The work has no priorities, and it is unclear whether the app must cover the globe or a few regions.

## Description

Choose one primary user and write their core stories. Choose pilot regions with contrasting fire regimes, for example boreal forest, savanna and cropland. Decide whether the app covers the whole globe or only the pilot regions. For one person, pilot regions only is the recommended default, with a data layout that does not prevent going global later.

## Acceptance criteria

- [x] One primary persona is described
- [x] Two or three user stories are written as 'As a ... I want ... so that ...'
- [x] Two pilot regions with contrasting fire regimes are chosen
- [x] The scope is stated as pilot regions only
- [x] An explicit out-of-scope list exists

## Outcome (Sat Nov 14)

Written in [`docs/scope.md`](../docs/scope.md): persona = regional fire duty officer; pilot regions = **Canada** (boreal) and **Zambia** (savanna); scope = pilot regions only; out-of-scope list. Region definitions are in `burn/config.py`.
