# DETAILS.md

This file stores planning details that are intentionally omitted from the 5-minute proposal presentation but may be useful for the written proposal, implementation planning, and final report.

## Current Concept

**Project title:** `Rover Ready`

- A compact VR repair experience set inside a rover garage bay
- The player prepares a damaged exploration rover for deployment
- The project should stay focused on one small environment and two main interactions

## Expanded Why-VR Rationale

- The experience is built around physical spatial actions rather than menu selection.
- Aligning a power module with a rover socket is more convincing in VR than on a flat screen.
- Using a repair tool on visible rover components benefits from hand presence and depth perception.
- A before-and-after state change in the room and rover gives strong feedback without requiring a large game loop.

## Expanded Environment Notes

- The room should feel like a compact industrial garage, not a large sci-fi level.
- Useful set pieces:
  - rover parked in center or slightly off-center
  - charging rack for power modules
  - tool wall or tool rack
  - small shelf for spare parts
  - floor markings and warning stripes
  - a few cables or panel details for visual density
- Visual progression:
  - start: dim lighting, scattered parts, inactive rover
  - end: brighter lighting, active rover indicators, cleaner scene state

## Visual Style Notes

- Use an intentional low-poly industrial style.
- Prefer chunky silhouettes over fine mechanical detail.
- Use simple materials and a limited palette.
- Candidate palette:
  - gunmetal gray
  - muted sand
  - orange accents
  - warning yellow
  - small cyan or white indicator lights
- Keep shapes readable from a distance in VR.

## Core Interaction Notes

### Interaction 1: Power Module Insertion

- Player grabs a module from the rack
- Player aligns it to a socket
- Snap-to-socket logic should make insertion stable
- State change:
  - rover powers on partially
  - indicator lights change

### Interaction 2: Component Repair

- Player grabs a repair tool
- Player uses it on damaged rover points such as:
  - wheel mount
  - access panel
  - antenna base
- State change:
  - repaired part changes model state, color, or light feedback

### Current Loop Shape

1. Grab a power module from the rack
2. Insert it into the rover to power it on
3. Use the repair tool on damaged rover parts
4. Finish the repair and show the rover as ready to go

### Light Progression Direction

- Later repair tasks can become somewhat more difficult over time
- This should stay within the same garage-bay repair concept
- Do not let the progression idea turn the project into a large multi-level game

### Optional Stretch Interaction

- Load one supply crate or spare part into the rover
- This should only be added if the first two interactions already feel solid

## Feature-Mapping Notes

### Base Requirements

- **Original theme**
  - A rover repair bay is distinct from lab examples

- **Two custom Blender assets**
  - power module
  - repair tool

- **Two meaningful VR interactions**
  - insertion
  - repair

### Planned Advanced Features

1. **Physics (Category A)**
   - tools, power modules, and possibly a crate use physics

2. **Multiple object types / tools (Category A)**
   - modules, sockets, repair targets, and tools each behave differently

### Optional Backup Advanced Feature

- **Procedural generation**
  - only if needed
  - best used for environment kit pieces rather than hero props

## Procedural Blender Modeling Notes

The safest procedural targets are repeated environment assets, not the main interactive props.

### Good procedural candidates

1. `storage crates`
2. `parts shelves`
3. `garage floor panels`
4. `wall modules`
5. `cable bundles`
6. `pipe clusters`

### Keep manual

1. `power module`
2. `repair tool`

These are better as hero props with intentional silhouettes.

## Risk Notes

### Main risks

- overdesigning the rover model
- making module insertion feel unstable
- adding too many repair targets
- spending too much time on environment detail
- letting the progression idea expand the scope too far

### Controls

- keep the rover stylized and low-poly
- use snap targets for insertion
- keep the first playable loop very short
- treat extra interactions as stretch goals, not requirements
- keep any added difficulty to small variations in the existing repair loop

## Written Proposal Material to Reuse

The written proposal can expand on:

- why VR is appropriate for spatial repair work
- the low-poly visual direction and palette
- the room progression from inactive to mission-ready
- detailed feature mapping
- risk mitigation and scope control
- procedural modeling as an optional or backup feature path
