# Rover Ready Technical Details

This file records the implementation layout, asset inventory, rebuild workflow,
and packaging notes for the Rover Ready final deliverable.

## Project Layout

- `./index.html`: browser entrypoint for the WebXR demo.
- `./src/main.js`: main scene setup, game state, interaction handling, scoring, timer, and rover flow.
- `./src/core/`: level configuration and shared game constants.
- `./src/scene/`: Three.js scene modules for the garage, rover, tools, buttons, materials, and instruction text.
- `./src/assets/models/`: exported runtime GLB models loaded by the demo.
- `./src/assets/blend/`: original Blender source files preserved for submission.
- `./scripts/blender/`: Blender Python scripts used to generate and update the models.

Generated local folders such as `./.venv`, `./.ruff_cache`, and `./__pycache__`
are intentionally not part of the submitted tree.

## Runtime Asset Paths

The WebXR demo loads runtime models from `./src/assets/models/`:

- `Rover_Bay.glb`: garage bay environment.
- `rover.glb`: regular rover model.
- `rover_complex.glb`: larger Level 6+ rover model.
- `power_cell.glb`: grabbable power cell.
- `repair_tool.glb`: handheld repair tool.

The scene-loading code that references these models lives in `./src/scene/`.
The URLs are root-relative to the local static server path, so the project must
be served from the project root.

## Blender Source Files

The original Blender files are stored in `./src/assets/blend/`:

- `rover_bay.blend`
- `rover_complex_only.blend`
- `rover_ready_assets.blend`

The Blender generation scripts are stored in `./scripts/blender/` and write
outputs back into `./src/assets/models/` and `./src/assets/blend/`.

## Rebuilding Assets

Blender must be installed to regenerate the models. From the project root, run
the relevant script with Blender in background mode. For example:

```bash
blender --background --python ./scripts/blender/create_rover_ready_assets.py
```

The other Blender scripts are:

```text
./scripts/blender/create_complex_rover_only.py
./scripts/blender/create_rover_bay.py
./scripts/blender/create_bay_floor_detail_addon.py
./scripts/blender/create_mars_exterior_addon.py
```

## Demo Video

The recorded final demo video is hosted separately from the source submission.

## External Libraries

The demo imports Three.js and Cannon-ES from public CDNs through `./index.html`.
All visible rover, tool, power-cell, and garage-bay models included in the final
demo are generated from the project Blender files and scripts in this repository.
