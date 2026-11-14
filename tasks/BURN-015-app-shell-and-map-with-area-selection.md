---
id: BURN-015
title: App shell and map with area selection
type: build
priority: must
requirement: 4. A person must be able to read it
timebox: 2h
status: in-progress
depends: BURN-009, BURN-024
---

## First principle

Burning activity is a property of a place. The same month can be extreme in one district and quiet in the next, so no answer exists until an area is given.

## What fails without this task

No query can be asked.

## Description

Extend the skeleton from BURN-024 with a map page where the user defines an area and a date range and triggers a query.

## Acceptance criteria

- [ ] A user can draw a rectangle on the map
- [ ] Stretch: a user can draw a polygon
- [ ] A user can type a latitude and longitude with a radius
- [ ] The area can be cleared and redrawn
- [ ] A date range can be picked
- [ ] Loading and error states are shown

## Outcome (Sat Nov 14)

Leaflet map, rectangle (typed or dragged) and point with radius (typed or clicked), year range. **Not yet tried by hand in a browser**: only a static headless render was checked. The owner should try dragging a rectangle and clicking a point.
