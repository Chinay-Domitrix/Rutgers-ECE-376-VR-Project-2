# Rover Ready Assets

This folder contains the exported runtime models and Blender source files for `Rover Ready`. The Blender Python source scripts live in `./scripts/blender`. The assets are built for a compact low-poly rover repair bay: readable silhouettes, gray and muted sand body colors, orange/yellow safety accents, and small cyan/white light details.

## Generate the Assets

Run the rover/tool generator from the project root (`.`). The command is the same concept on every device: invoke Blender in background mode and point it at `./scripts/blender/create_rover_ready_assets.py`.

If `blender` is on `PATH`:

```bash
blender --background --python ./scripts/blender/create_rover_ready_assets.py
```

On Windows with a default Blender 4.5 install, the command usually looks like:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "./scripts/blender/create_rover_ready_assets.py"
```

On macOS, it may look like:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python ./scripts/blender/create_rover_ready_assets.py
```

On Linux, it may look like:

```bash
/path/to/blender --background --python ./scripts/blender/create_rover_ready_assets.py
```

The rover/tool script writes:

- `./src/assets/blend/rover_ready_assets.blend`
- `./src/assets/models/rover.glb`
- `./src/assets/models/power_cell.glb`
- `./src/assets/models/repair_tool.glb`

The complex rover script is `./scripts/blender/create_complex_rover_only.py`. It writes:

- `./src/assets/blend/rover_complex_only.blend`
- `./src/assets/models/rover_complex.glb`

The garage bay base script is `./scripts/blender/create_rover_bay.py`. The bay can then be enhanced by running `./scripts/blender/create_bay_floor_detail_addon.py` and `./scripts/blender/create_mars_exterior_addon.py` after the base scene is created. The tracked source blend for the enhanced bay is `./src/assets/blend/rover_bay.blend`, and its exported runtime model is `./src/assets/models/Rover_Bay.glb`.

The `.blend` files are the source asset files. The `.glb` files are the runtime assets to load with Three.js `GLTFLoader`.

The distributable package is `./dist/rover_ready_assets.zip`. It contains this README, the Blender source scripts from `./scripts/blender`, the runtime `.glb` files, and the source `.blend` files. Local Python cache folders are intentionally left out of the zip.

## Asset Overview

### `Rover_Bay.glb`

The garage bay is the shared environment model used by the WebXR demo. It contains the room shell, tool table, diagnostic screen, carriage-style bay door, GLB button panel meshes, extra floor props, and the Mars exterior outside the bay.

### `rover.glb`

The rover is a stylized six-wheel service rover with a top-mounted power-cell receiver and three removable repair components.

### `rover_complex.glb`

The complex rover is the larger Level 6+ rover model used by the final demo. It adds the second power-cell slot and additional repair components used by the later level progression.

Important gameplay nodes used by the rover models:

| Node                                           | Purpose                                                                           |
| ---------------------------------------------- | --------------------------------------------------------------------------------- |
| `RR_Rover_Root`                                | Main rover root. Use this as the parent when adding the whole rover to the scene. |
| `RR_Rover_PowerCellDock_Root`                  | Visible receiver assembly on the rover.                                           |
| `RR_Rover_PowerCell_SnapTarget`                | Target transform for snapping the power cell into place.                          |
| `RR_Rover_Component_SideAccessPanel_Root`      | Removable side panel component.                                                   |
| `RR_Rover_Component_FrontRightWheelMount_Root` | Removable front-right wheel-mount component.                                      |
| `RR_Rover_Component_AntennaModule_Root`        | Removable antenna module component.                                               |

Each removable component has three helper nodes:

| Suffix        | Purpose                                                               |
| ------------- | --------------------------------------------------------------------- |
| `_GrabPoint`  | Suggested grab origin for whichever input system is being used.       |
| `_UsePoint`   | Suggested point to aim the repair tool at.                            |
| `_SnapTarget` | Target transform for putting the removed component back on the rover. |

Full component helper names:

```text
RR_Rover_Component_SideAccessPanel_GrabPoint
RR_Rover_Component_SideAccessPanel_UsePoint
RR_Rover_Component_SideAccessPanel_SnapTarget

RR_Rover_Component_FrontRightWheelMount_GrabPoint
RR_Rover_Component_FrontRightWheelMount_UsePoint
RR_Rover_Component_FrontRightWheelMount_SnapTarget

RR_Rover_Component_AntennaModule_GrabPoint
RR_Rover_Component_AntennaModule_UsePoint
RR_Rover_Component_AntennaModule_SnapTarget
```

### `power_cell.glb`

The power cell is intentionally just a plain beveled rectangular-prism battery. It has flat visual markings only: a top label, a lightning-bolt decoration, an orange label band, and two small front contact pads.

Important gameplay nodes:

| Node                       | Purpose                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| `RR_PowerCell_Root`        | Main battery root. Move, grab, and snap this object.                   |
| `RR_PowerCell_InsertPoint` | Alignment point that should mate with `RR_Rover_PowerCell_SnapTarget`. |
| `RR_PowerCell_GripPoint`   | Suggested grab origin for whichever input system is being used.        |

The front contact pads are visual only:

```text
RR_PowerCell_Front_Contact_Pad_Positive
RR_PowerCell_Front_Contact_Pad_Negative
```

### `repair_tool.glb`

The repair tool is a handheld low-poly tool with a grip, trigger, barrel, nozzle, status ring, and tip light.

Important gameplay nodes:

| Node                        | Purpose                                                         |
| --------------------------- | --------------------------------------------------------------- |
| `RR_RepairTool_Root`        | Main repair tool root. Move and grab this object.               |
| `RR_RepairTool_GripPoint`   | Suggested grab origin for whichever input system is being used. |
| `RR_RepairTool_TipUsePoint` | Point to test against component `_UsePoint` nodes.              |

## Integration Assumptions

The asset contract is device-agnostic. The same node names work whether the project is tested with a WebXR headset, the Immersive Web Emulator, mouse/keyboard debugging controls, or another input wrapper.

The JavaScript side should treat input as higher-level actions:

- `grab`: attach or constrain an object root to the active input pose.
- `release`: detach the object and optionally hand it to physics.
- `use`: check the repair tool tip against a repair target.
- `snap`: align an object/helper point to a target helper point.

How those actions are triggered is up to the runtime: WebXR controller events, emulator controls, pointer events, keyboard shortcuts, or a testing UI can all call the same object-handling functions.

## GLTFLoader Setup

Use `GLTFLoader` to load the runtime `.glb` files separately. This keeps the interactive objects easy to manage and lets Cannon-ES bodies be assigned per object.

```js
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const loader = new GLTFLoader();

async function loadGLB(url) {
  const gltf = await loader.loadAsync(url);
  return gltf.scene;
}

const bay = await loadGLB("./src/assets/models/Rover_Bay.glb");
const rover = await loadGLB("./src/assets/models/rover.glb");
const complexRover = await loadGLB("./src/assets/models/rover_complex.glb");
const powerCell = await loadGLB("./src/assets/models/power_cell.glb");
const repairTool = await loadGLB("./src/assets/models/repair_tool.glb");

scene.add(bay, rover, complexRover, powerCell, repairTool);
```

If your runtime files are served from a different folder, adjust the URLs accordingly.

## Finding Nodes in JavaScript

Use exact node names with `getObjectByName`.

```js
const roverRoot = rover.getObjectByName("RR_Rover_Root");
const powerCellRoot = powerCell.getObjectByName("RR_PowerCell_Root");
const repairToolRoot = repairTool.getObjectByName("RR_RepairTool_Root");

const powerSnapTarget = rover.getObjectByName("RR_Rover_PowerCell_SnapTarget");
const powerInsertPoint = powerCell.getObjectByName("RR_PowerCell_InsertPoint");

const sidePanel = rover.getObjectByName("RR_Rover_Component_SideAccessPanel_Root");
const sidePanelSnap = rover.getObjectByName("RR_Rover_Component_SideAccessPanel_SnapTarget");
const sidePanelUse = rover.getObjectByName("RR_Rover_Component_SideAccessPanel_UsePoint");

const toolTip = repairTool.getObjectByName("RR_RepairTool_TipUsePoint");
```

The generator exports Blender custom properties as GLTF extras, so `GLTFLoader` should put them on `object.userData`. For example:

```js
console.log(sidePanel.userData);
// Expected keys include:
// interaction_role: "removable_component"
// component_id: "side_access_panel"
```

## Recommended Runtime Registries

Build small registries after loading instead of scattering string lookups across the code.

```js
const roverParts = {
  side_access_panel: {
    root: rover.getObjectByName("RR_Rover_Component_SideAccessPanel_Root"),
    grabPoint: rover.getObjectByName("RR_Rover_Component_SideAccessPanel_GrabPoint"),
    usePoint: rover.getObjectByName("RR_Rover_Component_SideAccessPanel_UsePoint"),
    snapTarget: rover.getObjectByName("RR_Rover_Component_SideAccessPanel_SnapTarget"),
    repaired: false,
    attached: true,
  },
  front_right_wheel_mount: {
    root: rover.getObjectByName("RR_Rover_Component_FrontRightWheelMount_Root"),
    grabPoint: rover.getObjectByName("RR_Rover_Component_FrontRightWheelMount_GrabPoint"),
    usePoint: rover.getObjectByName("RR_Rover_Component_FrontRightWheelMount_UsePoint"),
    snapTarget: rover.getObjectByName("RR_Rover_Component_FrontRightWheelMount_SnapTarget"),
    repaired: false,
    attached: true,
  },
  antenna_module: {
    root: rover.getObjectByName("RR_Rover_Component_AntennaModule_Root"),
    grabPoint: rover.getObjectByName("RR_Rover_Component_AntennaModule_GrabPoint"),
    usePoint: rover.getObjectByName("RR_Rover_Component_AntennaModule_UsePoint"),
    snapTarget: rover.getObjectByName("RR_Rover_Component_AntennaModule_SnapTarget"),
    repaired: false,
    attached: true,
  },
};
```

## Power Cell Interaction

The intended flow:

1. The input system grabs `RR_PowerCell_Root`.
2. While held, compare `RR_PowerCell_InsertPoint` to `RR_Rover_PowerCell_SnapTarget`.
3. If the points are close enough, snap `RR_PowerCell_Root` into the receiver.
4. Mark the rover as powered.
5. Optionally change rover indicator lights or enable the repair stage.

Distance check helper:

```js
const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();

function worldDistance(a, b) {
  a.getWorldPosition(tmpA);
  b.getWorldPosition(tmpB);
  return tmpA.distanceTo(tmpB);
}

const closeEnough = worldDistance(powerInsertPoint, powerSnapTarget) < 0.18;
```

Simple snap helper:

```js
function snapObjectByPoints(objectRoot, objectPoint, targetPoint) {
  const objectPointWorld = new THREE.Vector3();
  const targetPointWorld = new THREE.Vector3();

  objectPoint.getWorldPosition(objectPointWorld);
  targetPoint.getWorldPosition(targetPointWorld);

  const delta = targetPointWorld.sub(objectPointWorld);
  objectRoot.position.add(delta);

  targetPoint.getWorldQuaternion(objectRoot.quaternion);
}
```

Use it like this:

```js
if (closeEnough) {
  snapObjectByPoints(powerCellRoot, powerInsertPoint, powerSnapTarget);
  powerCellRoot.userData.inserted = true;
}
```

Depending on the grab implementation, detach the object from the active input pose before snapping it.

## Repair Component Interaction

The intended flow for each removable rover component:

1. The input system targets or grabs a component root, such as `RR_Rover_Component_SideAccessPanel_Root`.
2. Component is detached from the rover and treated as a movable object.
3. The repair action checks `RR_RepairTool_TipUsePoint` near the component's `_UsePoint`.
4. After enough repair time or one confirmed action, mark the component repaired.
5. The component is moved back near its `_SnapTarget`.
6. Snap the component root back onto the rover and mark it attached.

Example repair test:

```js
function tryRepairComponent(component, repairToolTip) {
  if (component.repaired) return false;
  if (worldDistance(repairToolTip, component.usePoint) > 0.15) return false;

  component.repaired = true;
  component.root.userData.repaired = true;
  return true;
}
```

Example reattachment test:

```js
function tryReattachComponent(component) {
  if (!component.repaired || component.attached) return false;
  if (worldDistance(component.root, component.snapTarget) > 0.18) return false;

  snapObjectByPoints(component.root, component.root, component.snapTarget);
  component.attached = true;
  component.root.userData.attached = true;
  return true;
}
```

If you use Cannon-ES, disable or sleep the physics body before snapping, then copy the snapped Three.js transform back into the body.

## Traversing by Metadata

Because the export enables `export_extras`, you can also discover nodes by metadata instead of hardcoded names.

```js
const removableComponents = [];

rover.traverse((object) => {
  if (object.userData?.interaction_role === "removable_component") {
    removableComponents.push(object);
  }
});
```

Current exported `interaction_role` values:

| Role                    | Meaning                                              |
| ----------------------- | ---------------------------------------------------- |
| `power_cell_receiver`   | Rover dock that accepts the power cell.              |
| `socket_snap_target`    | Rover snap target for the battery.                   |
| `battery_insert_point`  | Battery-side alignment point.                        |
| `battery_grab_point`    | Suggested battery grab point for any input system.   |
| `removable_component`   | Root of a removable repair component.                |
| `component_grab_point`  | Suggested grab point for a repair component.         |
| `repair_use_point`      | Point to check against the repair tool tip.          |
| `component_snap_target` | Target transform for reattaching a repair component. |

Current exported `component_id` values:

```text
power_cell
side_access_panel
front_right_wheel_mount
antenna_module
```

## Collision and Physics Notes

These GLB files are visual/gameplay marker assets, not optimized physics collision meshes. For Cannon-ES, use simple proxy bodies:

- Rover: static box or compound boxes around the chassis and floor contact area.
- Power cell: one dynamic box matching `RR_PowerCell_Root`.
- Repair tool: one dynamic box or capsule-like compound around the grip/body.
- Removable components: small dynamic boxes around each component root while detached.

Keep the visible GLB nodes and Cannon-ES bodies synchronized after grabs, drops, repairs, and snap actions.

## Naming Contract

Runtime code should treat these names as stable:

```text
RR_Rover_Root
RR_Rover_PowerCellDock_Root
RR_Rover_PowerCell_SnapTarget

RR_PowerCell_Root
RR_PowerCell_InsertPoint
RR_PowerCell_GripPoint

RR_RepairTool_Root
RR_RepairTool_GripPoint
RR_RepairTool_TipUsePoint

RR_Rover_Component_SideAccessPanel_Root
RR_Rover_Component_SideAccessPanel_GrabPoint
RR_Rover_Component_SideAccessPanel_UsePoint
RR_Rover_Component_SideAccessPanel_SnapTarget

RR_Rover_Component_FrontRightWheelMount_Root
RR_Rover_Component_FrontRightWheelMount_GrabPoint
RR_Rover_Component_FrontRightWheelMount_UsePoint
RR_Rover_Component_FrontRightWheelMount_SnapTarget

RR_Rover_Component_AntennaModule_Root
RR_Rover_Component_AntennaModule_GrabPoint
RR_Rover_Component_AntennaModule_UsePoint
RR_Rover_Component_AntennaModule_SnapTarget
```

If these names change in the Blender generator, update this README and the JavaScript lookup registry at the same time.
