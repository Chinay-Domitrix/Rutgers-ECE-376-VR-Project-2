# Rover Ready

Rutgers Virtual Reality & Lab  
Project 2 Final Presentation  
Group Members: Chirag Baviskar and Dhrumil Patel

Timing target: about 7 minutes.

---

## Slide 1 - Completed Project Overview

- Rover Ready is a browser-based WebXR rover repair bay
- The player calls a rover into the bay, powers it, repairs it, checks it, and sends it out
- The project stays in one compact garage room instead of trying to become a large level
- Built with Blender, Three.js, WebXR, GLTFLoader, and Cannon-ES

> Chirag: So our project is Rover Ready. It is a small WebXR repair scene where you are standing in one garage bay, getting a rover ready to leave. We kept the goal pretty direct: call the rover in, power it, fix what is broken, check it, and then send it out.

---

## Slide 2 - Demo Flow

- Press CALL ROVER on the bay control panel
- Watch the bay door and rover arrival sequence
- Grab and insert the power cell into the rover dock
- Use the repair tool on highlighted damaged parts
- Place missing parts back onto snap targets when a level requires it
- Press CHECK, then SEND ROVER once the task is complete

> Dhrumil: For the demo, we are going to show the loop in the order the player would actually do it. First we press the call button, the bay opens, and the rover comes into position. Then we insert the power cell. After that, the next repair job shows the repair tool and the missing-part behavior, so you can see that the scene is more than just a static model.

---

## Slide 3 - Scene and Custom Assets

Scene elements:

- Low-poly garage bay with floor markings, tool table, diagnostic screen, bay door, and button panel
- Stylized six-wheel rover with a visible power-cell dock and repairable components
- Rack objects for the power cell and handheld repair tool

Custom Blender assets:

- Power cell module
- Handheld repair tool
- Six-wheel service rover
- Garage repair bay

> Chirag: Visually, we went for a simple low-poly garage style. The shapes are chunky on purpose, because they read well in VR and we did not want the scene to turn into tiny mechanical detail. For the custom asset requirement, the power cell and repair tool are the main props, but we also made the rover and the bay. Each one is exported as its own GLB, which made it easier to load and control them separately in the demo.

---

## Slide 4 - Repair Bay Setup

Image:

- `final-presentation/assets/setup.png`

Caption:

- The rover parked in the work zone, with the mission screen, HUD, tool bench, and bay props visible around it.

> Chirag: This slide shows the main play space from inside the bay. The yellow outline marks where the rover stops, the screen and HUD show the current task, and the repair tools are kept near the work area instead of hidden somewhere else. The layout is meant to make the loop easy to read: check the objective, grab what you need, work on the rover, and then verify it.

---

## Slide 5 - Interaction 1: Power Module Insertion

- The power cell starts as a grabbable object on the rack
- Cannon-ES gives it a physical body while it is loose
- The rover model includes a named snap target for the dock
- When the player aligns the cell near the dock, it snaps into place and locks to the rover
- The HUD, score, and rover-check state update after insertion

> Dhrumil: The power cell interaction was the first big piece of the loop. When it is loose, it has physics and can be grabbed from the rack. Once the player gets it close enough to the receiver, we use the helper points from the model to snap it into the dock. That way the player still has to move it into the right area, but they do not have to line it up perfectly by hand.

---

## Slide 6 - Interaction 2: Repair and Replacement

- The repair tool is a separate grabbable object with its own behavior
- Damaged targets glow red while the tool is being used
- Holding the tool on a target long enough marks it as repaired
- Some levels spawn missing rover parts as loose grabbable objects
- Missing parts show snap markers and reattach when placed near the correct rover target

> Chirag: The second main interaction is the repair step. The tool is not just decoration; when the player holds it, damaged parts can glow red, and holding the tool on the target long enough marks that part as fixed. Some levels also take parts off the rover completely, like a wheel or light, and put them on the rack as loose objects. Then the player has to place that part back on the rover.

---

## Slide 7 - Requirement Fit

Base requirements:

- Original theme: compact rover repair bay, not a lab reskin
- Custom 3D assets: power cell and repair tool, plus custom rover and garage bay
- GLTFLoader: runtime loads the garage bay, rover, power cell, and repair tool as separate models
- Core interactions: power-cell insertion, repair-tool use, and missing-part reattachment

Advanced features:

- Category A: Cannon-ES physics for tools, modules, loose parts, and collision proxies
- Category A: multiple object types and modes, including buttons, rover, power cell, repair tool, repair targets, and missing parts
- Additional support: Blender Python scripts generate meaningful scene and asset content

> Dhrumil: This is the checklist version of how the final build matches the assignment. The original theme is the repair bay, the custom models are loaded with GLTFLoader, and the main interactions are powering and repairing the rover. For the advanced features, we used Cannon-ES physics, and we also have different object types with different behavior: buttons, tools, power cells, repair targets, and missing parts.

---

## Slide 8 - Individual Contributions

Chirag led:

- Blender asset direction for the rover-ready prop set
- Low-poly visual consistency, asset cleanup, and export organization
- Asset documentation and final packaging structure

Dhrumil led:

- WebXR scene setup and Three.js runtime integration
- Controller, desktop, and emulator interaction handling
- Cannon-ES physics setup and collision proxy behavior
- Rover arrival flow, power insertion, repair logic, levels, scoring, and HUD state

> Chirag: On my side, I focused more on the assets and final organization. That included keeping the low-poly style consistent, cleaning up the source and exported assets, and making sure the asset documentation and packaging matched what we actually built.
>
> Dhrumil: On my side, I focused more on the runtime. That meant getting the assets into Three.js, handling the controller and desktop interactions, setting up physics, and building the rover states for calling, powering, repairing, checking, and sending it out.

---

## Slide 9 - Reflection and Future Work

What was challenging:

- Keeping Blender model geometry aligned with runtime snap points
- Making physics objects feel stable enough for VR interaction
- Avoiding scope creep while still meeting the advanced-feature requirements
- Matching visible GLB models with invisible collision and interaction proxies

What VR adds:

- The power-cell insertion works because the player physically aligns an object in 3D space
- The repair tool feels more natural as a hand-held action than as a flat-screen button press
- The rover state changes are easier to understand when the player is standing next to it

Future work:

- Add sound effects and stronger tool feedback
- Add more varied repair jobs and diagnostic screen states
- Polish the rover departure and completion feedback
- Improve headset testing beyond the emulator workflow

> Dhrumil: The hardest part was getting Blender and the browser runtime to agree with each other. A model can look fine in Blender, but then the snap point, collision box, or interaction distance can still feel wrong in WebXR. With more time, we would add stronger feedback, more repair variety, and more headset testing. For this version, though, the main repair loop is in place and stays focused.
