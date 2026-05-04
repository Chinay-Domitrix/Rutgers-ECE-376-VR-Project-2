# Rover Ready

Rover Ready is a browser-based WebXR rover repair experience created for
Rutgers Virtual Reality & Lab Project 2. The project places the player inside a
compact low-poly garage bay where they call in service rovers, install power
cells, repair highlighted components with a handheld tool, replace missing
parts, verify the rover, and launch it back out of the bay.

The final experience focuses on one small environment and one complete gameplay
loop rather than a large map. The scene is built around an intentional low-poly
industrial style with custom Blender-made models, readable silhouettes, simple
materials, and clear interaction targets.

## Project Information

- Course: Rutgers Virtual Reality & Lab
- Project: Project 2 Final Deliverable
- Team: Chirag Baviskar and Dhrumil Patel
- Title: Rover Ready
- Stack: Three.js, WebXR, GLTFLoader, Cannon-ES, Blender

## How to Run

Serve the project root through a local web server. Do not open `./index.html`
directly from the file system because the project uses JavaScript modules, GLB
models, and CDN imports.

The easiest option is to run one of the included launch scripts from this
folder:

```powershell
.\run-demo.ps1
```

```bat
.\run-demo.bat
```

```bash
./run-demo.sh
```

Each script starts a Python static server and opens:

```text
http://localhost:5173/
```

A different port can be passed as the first argument for `run-demo.bat` or
`run-demo.sh`, or as `-Port` for `run-demo.ps1`.

The server can also be started manually:

```bash
python -m http.server 5173
```

Then open:

```text
http://localhost:5173/
```

## Browser and VR Notes

Use a Chromium-based browser such as Chrome or Edge. If those browsers have
issues, Opera GX has also worked for testing. An internet connection is required
because Three.js and Cannon-ES are imported from CDN links in `./index.html`.

Desktop testing works directly in the browser. For VR testing without a headset,
use the WebXR Emulator browser extension and enter immersive mode from the VR
button. For headset testing, keep the project served from a local web server and
open the page in a WebXR-compatible browser.

## Controls

- Desktop movement: `W`, `A`, `S`, and `D`.
- Desktop turning: left and right arrow keys.
- VR movement: controller thumbsticks.
- Grab objects: controller trigger/select or desktop mouse drag.
- Bay controls: use the in-scene buttons to call, check, and launch rovers.

## Gameplay Loop

The player begins in a single rover service bay. Pressing the call button brings
in a rover, which starts a short repair task sequence. The core tasks are to
install power cells, repair glowing scan targets with the handheld repair tool,
replace missing rover components, run the check sequence, and launch the rover
when it is ready.

Progression adds more requirements over time. Later levels introduce the larger
complex rover, a second power-cell slot, more repair targets, and more missing
parts. The goal is to keep the challenge within the same readable repair loop
instead of expanding into a separate game mode.

## Assignment Coverage

- Original theme: a compact VR rover repair bay rather than a reskinned class lab.
- Custom Blender assets: rover bay, service rovers, power cell, and repair tool.
- Meaningful interactions: grabbing and installing power cells, aiming the repair tool at targets, moving parts, checking the rover, and launching it.
- Advanced feature: Cannon-ES physics is used for grabbable tools, power cells, and loose parts.
- Advanced feature: multiple object and tool behaviors are implemented across power cells, repair tools, rover components, bay buttons, and level-specific rover variants.

## Submitted Materials

The source tree includes the runnable WebXR demo, original Blender files,
exported GLB models, and Blender generation scripts. The packaged asset/source
bundle is `./dist/rover_ready_assets.zip`.

For implementation layout, asset inventory, rebuild commands, package contents,
and library details, see `./technical-details.md`.
