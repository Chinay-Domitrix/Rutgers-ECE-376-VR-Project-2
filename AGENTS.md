# AGENTS.md

## Role of This File

This file is the working contract for this repository. It should tell future
work where the project actually stands, how the final demo is organized, and
which constraints must not be broken.

- `project2.md` is the assignment source of truth.
- `AGENTS.md` is the repo operations guide.
- If this file conflicts with `project2.md`, follow `project2.md`.
- If this file conflicts with the live implementation, inspect the live files
  first and update this file in the same pass.

## Project Snapshot

- Course: Rutgers Virtual Reality and Lab, Project 2
- Course level: 376 undergraduate
- Team size: 2
- Team members: Chirag Baviskar and Dhrumil Patel
- Project title: `Rover Ready`
- Core stack: Blender, Three.js, WebXR, `GLTFLoader`, Cannon-ES
- Final demo root: `final/`

`Rover Ready` is a browser-based WebXR rover repair experience set in a compact
industrial garage bay. The player calls in a rover, installs one or more power
cells, repairs highlighted components with a handheld tool, places missing
parts back on the rover, checks the rover, and sends it out.

The current implementation is no longer proposal-stage planning. Treat it as a
final demo with supporting report and presentation materials.

## Current Implementation

The implemented experience includes:

- A single garage bay environment with a Mars exterior backdrop.
- A regular rover for early levels.
- A larger complex rover for later levels.
- Power-cell insertion and snapping.
- Handheld repair-tool aiming and dwell-based repair.
- Missing-part placement and snapping.
- Bay buttons for calling, checking, and sending rovers.
- Level progression with increasing repair and part requirements.
- Desktop fallback controls plus WebXR controller support.
- Cannon-ES physics for grabbable parts and tools.

The project is intentionally scoped as one polished room and one repeated repair
loop. Do not expand it into multiple rooms or a broad simulation unless the user
explicitly changes direction.

## Assignment Requirements

Keep the final materials aligned to these non-negotiable requirements:

### Base Requirements

- Original theme beyond the course labs and homework.
- At least two meaningful custom Blender-made 3D assets loaded through
  `GLTFLoader`.
- At least two meaningful VR interactions that directly manipulate objects or
  change the environment through XR input.

### Advanced Feature Minimum

Because this is a 376 two-person group, the project needs:

- At least two advanced features total.
- At least one advanced feature from Category A.

The current feature mapping should stay framed around:

- Category A: Cannon-ES physics.
- Category A: multiple object types, tools, and interaction modes.
- Supporting feature: procedural Blender/Python generation for the environment
  and custom assets.

Do not claim a feature counts unless it clearly matches the assignment language
in `project2.md`.

## Final Demo Layout

The runnable demo is rooted at `final/`. Inside `final/`, documentation and code
paths should be written relative to `final/` as `./...`.

Current important paths:

- `final/index.html`: browser entrypoint.
- `final/src/`: Three.js/WebXR application code.
- `final/src/main.js`: scene setup, game state, input, grabbing, snapping,
  repair logic, HUD, timer, and rover flow.
- `final/src/core/levels.js`: level progression and repair/missing-part
  requirements.
- `final/src/core/types.js`: shared state and object constants.
- `final/src/scene/`: garage, rover, tools, buttons, materials, and in-world
  instruction modules.
- `final/src/assets/models/`: exported runtime `.glb` files.
- `final/src/assets/blend/`: source `.blend` files.
- `final/src/assets/README.md`: asset contract, generation notes, node names,
  and GLTF integration assumptions.
- `final/scripts/blender/`: Blender Python asset-generation scripts.
- `final/docs/demo.md`: concise demo/run notes.
- `final/dist/`: distributable packaged assets.
- `final/run-demo.ps1`, `final/run-demo.bat`, `final/run-demo.sh`: quick-run
  scripts.
- `final/pyproject.toml`, `final/uv.lock`: Python tooling metadata for asset
  scripts.

Do not create parallel demo or asset trees unless the user explicitly asks.
Runtime code belongs under `final/src/`; runtime models and source `.blend` files
belong under `final/src/assets/`; Blender generator scripts belong under
`final/scripts/blender/`.

## Runtime Path Rules

When editing the final demo:

- Treat `final/` as the served root.
- Use `./src/...` for JavaScript modules and runtime assets from
  `final/index.html`.
- Use `./src/assets/models/...` for GLB model URLs.
- Use `./scripts/blender/...` when documenting Blender generation commands.
- Avoid absolute Windows paths in tracked docs and runtime code.
- Do not open `index.html` directly from the file system in instructions; the
  demo needs a local web server.

## Running and Testing

The user is handling live demo testing unless they explicitly ask otherwise.
Do not start a local server, open a browser, or run a live WebXR test by default.

Safe checks that do not launch the demo are acceptable when relevant:

- Static file inspection.
- Syntax checks for edited JavaScript or Python.
- `git diff --check`.
- Targeted searches for stale paths or broken imports.

Run scripts from inside `final/`:

- PowerShell: `./run-demo.ps1`
- Windows batch: `run-demo.bat`
- Shell: `./run-demo.sh`

The scripts serve:

```text
http://localhost:5173/
```

If documentation mentions manual serving, use:

```text
python -m http.server 5173
```

from `final/`, then open `http://localhost:5173/`.

## Asset Rules

Preserve both runtime and source assets:

- `.glb` files are runtime assets loaded by the demo.
- `.blend` files are source materials required for final submission.
- Blender Python scripts are source materials and should stay in
  `final/scripts/blender/`.
- The asset README should stay accurate when node names, model paths, or
  generation steps change.

Important runtime models:

- `./src/assets/models/Rover_Bay.glb`
- `./src/assets/models/rover.glb`
- `./src/assets/models/rover_complex.glb`
- `./src/assets/models/power_cell.glb`
- `./src/assets/models/repair_tool.glb`

Important source blends:

- `./src/assets/blend/rover_bay.blend`
- `./src/assets/blend/rover_ready_assets.blend`
- `./src/assets/blend/rover_complex_only.blend`

When editing Blender Python scripts, preserve the import-optimization pattern
used for editor tooling:

```python
from importlib import import_module
from typing import Any

bpy: Any = import_module("bpy")
```

Use `import_module("mathutils")` when `mathutils` symbols are needed. Avoid
reintroducing direct `import bpy` or `from mathutils import ...` unless the user
explicitly asks to reverse that pattern.

## JavaScript Code Rules

Follow the current module boundaries:

- Keep global gameplay orchestration in `final/src/main.js`.
- Keep level data in `final/src/core/levels.js`.
- Keep shared constants and state enums in `final/src/core/types.js`.
- Keep scene construction and model-specific loading in `final/src/scene/`.

Do not scatter GLB node-name lookups across unrelated files. Prefer small local
registries or helper functions near the loading logic.

When changing gameplay, preserve the current loop unless asked otherwise:

1. Call rover.
2. Install required power cells.
3. Repair highlighted targets.
4. Place missing parts.
5. Check rover.
6. Send rover.
7. Advance level.

Keep desktop controls functional as a fallback for VR testing.

## Documentation Roles

Use documents deliberately:

- `project2.md`: assignment brief and grading source.
- `AGENTS.md`: repo operating contract.
- `final/README.md`: final demo run instructions and structure.
- `final/docs/demo.md`: concise demo instructions.
- `final/src/assets/README.md`: asset generation and GLTF node contract.
- `final-presentation/`: final presentation deck, draft, notes, and image
  generation scripts.
- `final-report/`: final report TeX source and IEEE class file.
- `written-proposal/`: accepted written proposal source and generated PDF.
- `proposal-presentation/`: proposal presentation materials.
- `DETAILS.md`: planning and rationale overflow when still useful.

When a behavior, path, feature, or asset changes, update the affected docs in
the same pass. Avoid leaving proposal-era wording in final-stage materials.

## Report and Presentation Rules

Final report and presentation materials must clearly state:

- What the finished experience does.
- Which base requirements are met.
- Which advanced features are implemented.
- Which components each team member led.
- How to run the demo.
- What runtime assets and source materials are included.

Avoid vague contribution wording such as "everyone worked on everything." It is
fine to describe collaboration, but each major component should still have a
clear lead.

For course prose, keep the writing natural and student-written. Avoid stiff,
generic, or overly polished wording.

## Style and Scope Rules

General project direction:

- Prefer the existing one-room rover bay over new areas.
- Prefer a small, complete repair loop over many partial mechanics.
- Keep the low-poly industrial look intentional.
- Favor readable silhouettes, simple materials, and clear interaction targets.
- Use guided snapping for power cells and missing parts.
- Keep difficulty increases as variations of the same repair loop.

Do not add large new systems, new dependencies, or new folder structures unless
they are necessary for the requested change.

## Packaging Rules

Before treating the final project as ready, make sure:

- The demo has clear run instructions.
- Runtime assets are included.
- Source `.blend` files are included.
- Blender generation scripts are included.
- The final report and presentation match the implemented demo.
- Asset credits are present if any third-party assets are introduced.
- The source package does not include local cache folders such as
  `__pycache__`, `.ruff_cache`, or `.venv`.

## Current Status

- The final implementation scaffold exists in `final/`.
- The main runnable entrypoint is `final/index.html`.
- The demo code is in `final/src/`.
- Blender scripts are in `final/scripts/blender/`.
- Runtime models and source blends are in `final/src/assets/`.
- Final presentation materials exist in `final-presentation/`.
- Final report materials exist in `final-report/`.
- The active milestone is final submission packaging and polish for May 4.

## Update Rule

Update this file whenever any of the following changes:

- Demo folder structure.
- Runtime path conventions.
- Implemented interactions or advanced features.
- Asset locations or generation workflow.
- Documentation workflow.
- Final submission status or packaging requirements.
