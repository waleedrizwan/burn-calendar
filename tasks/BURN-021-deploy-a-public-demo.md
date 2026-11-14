---
id: BURN-021
title: Deploy a public demo
type: build
priority: must
requirement: 5. Someone else must be able to trust and judge it
timebox: 1h30
status: todo
depends: BURN-024
---

## First principle

The challenge asks for a web application. Software that runs on one machine reaches one person, and a fire manager cannot use what they cannot open in a browser.

## What fails without this task

The app exists on one laptop.

## Description

Host the app and the pilot-region data at a public URL. Deploy in two steps: the skeleton from BURN-024 on Saturday, so hosting problems show up early, and the finished app on Sunday. Each step has half of the time budget.

## Acceptance criteria

- [ ] The skeleton from BURN-024 is at a public URL on Saturday, November 14
- [ ] The finished app is redeployed to the same URL on Sunday, November 15
- [ ] A public URL serves the app with pilot-region data
- [ ] The URL opens in a private browser window without a password, permission or registration
- [ ] No secrets are in the repo or the client bundle
- [ ] Deploy steps are documented
- [ ] The deploy can be repeated from a clean checkout by following the documented steps
- [ ] A FortiGuard Web Filter Classification is requested for the URL (optional, see `docs/rules.md`)
