import * as THREE from "three";
import { VRButton } from "three/addons/webxr/VRButton.js";
import { XRControllerModelFactory } from "three/addons/webxr/XRControllerModelFactory.js";
import * as CANNON from "cannon-es";
import { createMaterials } from "./scene/materials.js";
import { createLighting as createLightingAsset, createGarage as createGarageAsset } from "./scene/garage.js";
import { createRover as createRoverAsset } from "./scene/rover.js";
import {
  createPowerModule as createPowerModuleAsset,
  createRepairTool as createRepairToolAsset,
} from "./scene/tools.js";
import { bindBayButtonMeshes, createControlButtons as createControlButtonsAsset } from "./scene/buttons.js";
import { createInstructionText as createInstructionTextAsset } from "./scene/instructions.js";
import { getLevelConfig, missingPartDefinitions, repairPartDefinitions } from "./core/levels.js";
import { GameState, ObjectType } from "./core/types.js";

const state = {
  game: GameState.AWAITING_ROVER,
  held: new Map(),
  grabbables: [],
  staticPhysicsMeshes: [],
  buttonTargets: [],
  roverArriving: false,
  roverTurning: false,
  roverLeavingTurning: false,
  roverLeaving: false,
  doorMoving: false,
  doorOpen: false,
  doorProgress: 0,
  doorMode: null,
  bayDoor: null,
  roverChecked: false,
  roverGoodForLevel: false,
  level: 1,
  completedRovers: 0,
  currentLevelConfig: getLevelConfig(1),
  score: 0,
  timerDuration: 180,
  timeRemaining: 180,
  timerActive: false,
  powerModuleInstalled: false,
  installedPowerCellSlots: new Set(),
  preinstalledPowerCellSlotsVisualized: new Set(),
  powerSnapCheckTimer: 0,
  powerSnapCheckInterval: 0.1,
  powerSnapDistance: 0.55,
  powerSnapLocalPosition: new THREE.Vector3(-0.72, 1.35, 0),
  powerSnapLocalRotation: new THREE.Euler(0, 0, 0),
  powerInstallLocalPosition: new THREE.Vector3(-0.72, 1.05, 0),
  powerCellBodyLocalPosition: new THREE.Vector3(0, 0.38, 0),
  powerCellBodyHalfHeight: 0.17,
  powerDockSeatLocalPosition: new THREE.Vector3(-0.72, 1.23, 0),
  powerDockSeatTopClearance: 0.015,
  powerInsertLocalPosition: new THREE.Vector3(-0.51, 0.415, 0),
  repairTargets: [],
  missingParts: [],
  roverInteractionsReady: false,
  repairAimTargetId: null,
  repairAimTimer: 0,
  repairDwellTime: 3.0,
  repairTipReachDistance: 0.125,
  repairGlowTime: 0,
  partSnapCheckTimer: 0,
  partSnapCheckInterval: 0.08,
  partSnapDistance: 0.6,
  currentObjective: "",
  miniScreen: null,
  statusScreen: null,
  vrHud: null,
};
const raycaster = new THREE.Raycaster();
const raycastMatrix = new THREE.Matrix4();

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x171b20);

const playerRig = new THREE.Group();
playerRig.name = "playerRig";
playerRig.position.set(0, 0, 2.15);
scene.add(playerRig);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 1.6, 0);
playerRig.add(camera);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.xr.enabled = true;
document.body.appendChild(renderer.domElement);
document.body.appendChild(VRButton.createButton(renderer));

const controllerModelFactory = new XRControllerModelFactory();
const controllers = [0, 1].map(createController);

const physics = createPhysicsWorld();
const clock = new THREE.Clock();
const objective = document.querySelector("#objective");
const levelValue = document.querySelector("#levelValue");
const scoreValue = document.querySelector("#scoreValue");
const keyboard = {
  forward: false,
  backward: false,
  left: false,
  right: false,
  turnLeft: false,
  turnRight: false,
};
const playerCollider = {
  radius: 0.28,
  room: { minX: -6.55, maxX: 6.55, minZ: -4.95, maxZ: 4.95 },
  obstacles: [
    // Player walking collision volumes.
    { id: "workTable", minX: -6.65, maxX: -4.95, minZ: -3.95, maxZ: 3.95 },
    { id: "buttonPanel", minX: 6.35, maxX: 6.95, minZ: -2.85, maxZ: 0.25 },
    { id: "screenConsole", minX: -2.3, maxX: 2.3, minZ: 3.62, maxZ: 5.02 },

    // Crate walking collision volumes.
    { id: "crateBackLeftStack", minX: -6.3, maxX: -4.9, minZ: 3.25, maxZ: 4.25 },
    { id: "crateBackRightStack", minX: 4.85, maxX: 6.3, minZ: 3.25, maxZ: 4.25 },
    { id: "crateFrontLeftStack", minX: -6.3, maxX: -5.05, minZ: -4.3, maxZ: -3.3 },
    { id: "crateFrontRightStack", minX: 5.05, maxX: 6.3, minZ: -4.3, maxZ: -3.3 },
    { id: "crateLeftWall", minX: -6.3, maxX: -5.75, minZ: 0.05, maxZ: 0.65 },
    { id: "crateRightWall", minX: 5.75, maxX: 6.3, minZ: -0.9, maxZ: -0.2 },
  ],
};
const rackSurfaces = [
  // Work table resting surfaces.
  { id: "tableTop", y: 1.17, minX: -6.58, maxX: -5.02, minZ: -3.62, maxZ: 3.62 },
  { id: "tableShelf", y: 0.51, minX: -6.52, maxX: -5.08, minZ: -3.52, maxZ: 3.52 },

  // Diagnostic console resting surfaces.
  { id: "screenBaseTop", y: 1.31, minX: -2.1, maxX: 2.1, minZ: 3.8, maxZ: 4.85 },
  { id: "screenKeyboardTop", y: 1.41, minX: -1.45, maxX: 1.45, minZ: 3.88, maxZ: 4.62 },
];

const lastAllowedHeadPosition = new THREE.Vector3(playerRig.position.x, 0, playerRig.position.z);
const pointer = new THREE.Vector2();
const dragPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const dragHit = new THREE.Vector3();
// Rover arrival staging positions.
const ROVER_ENTRY_Z = -10.25;
const ROVER_PARKED_Z = -0.1;
const REPAIR_TOOL_GRIP_OFFSET = new THREE.Vector3(0, -0.04, -0.3);
const REPAIR_TOOL_FORWARD = new THREE.Vector3(0, 0, -1);
const REPAIR_TOOL_DOWN = new THREE.Vector3(0, -1, 0);
const VR_HUD_POSITION = new THREE.Vector3(-0.62, 0.34, -1.25);
const TOOL_TABLE_SPAWN_X = [-5.24, -5.84, -6.34];
const TOOL_TABLE_SPAWN_Z = [-3.25, -2.15, -1.05, 0.05, 1.15, 2.25, 3.25];
let mouseHeld = null;
let launchButton;
let callButton;
let checkButton;
let pendingBayRoot = null;
let repairTool = null;
let lastDrawnSecond = -1;
let powerModules = [];

const materials = createMaterials();
state.vrHud = createVrHudPanel();

const lighting = createLightingAsset(scene);
createGarageAsset({
  scene,
  addBox,
  materials,
  onBayLoaded: bindLoadedBayFunctions,
});
let rover = null;
let powerModule = null;
repairTool = createRepairToolAsset({
  scene,
  materials,
  meshBox,
  addPhysicsBox,
  grabbables: state.grabbables,
});
const buttonControls = createControlButtonsAsset({
  scene,
  materials,
  meshBox,
  addStaticBodyForMesh,
  buttonTargets: state.buttonTargets,
});
({ launchButton, callButton, checkButton } = buttonControls);
if (!checkButton) checkButton = createLogicalButton("check");
if (launchButton?.userData) launchButton.userData.action = launchButton.userData.action ?? "launch";
if (callButton?.userData) callButton.userData.action = callButton.userData.action ?? "call";
if (checkButton?.userData) checkButton.userData.action = checkButton.userData.action ?? "check";
state.inWorldText = createInstructionTextAsset({ scene });
if (pendingBayRoot) bindLoadedBayFunctions(pendingBayRoot);
setButtonEnabled(callButton, true, materials.lightOn, materials.socketIdle);
setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
setCheckButtonEnabled(false);
updateObjective("Press the call button to bring in the first rover.");
updateHud();

renderer.setAnimationLoop(render);
window.addEventListener("resize", onResize);
window.addEventListener("keydown", (event) => setKey(event.code, true));
window.addEventListener("keyup", (event) => setKey(event.code, false));
renderer.domElement.addEventListener("pointerdown", onPointerDown);
renderer.domElement.addEventListener("pointermove", onPointerMove);
renderer.domElement.addEventListener("pointerup", onPointerUp);

function createLogicalButton(actionName) {
  return {
    userData: {
      action: actionName,
      enabled: false,
      button: null,
    },
  };
}

function createVrHudPanel() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.generateMipmaps = false;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;

  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(0.78, 0.39),
    new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
      depthWrite: false,
    }),
  );
  panel.name = "VrCameraHud";
  panel.position.copy(VR_HUD_POSITION);
  panel.renderOrder = 10000;
  panel.visible = false;
  camera.add(panel);

  return { canvas, texture, panel };
}

function markShadowsDirty() {
  if (lighting?.main?.shadow) lighting.main.shadow.needsUpdate = true;
}

function getButtonForAction(actionName) {
  if (actionName === "call") return callButton;
  if (actionName === "check") return checkButton;
  if (actionName === "launch" || actionName === "send") return launchButton;
  return null;
}

function setButtonEnabled(
  buttonGroup,
  enabled,
  enabledMaterial = materials.lightOn,
  disabledMaterial = materials.lightOff,
) {
  if (!buttonGroup?.userData) return;

  buttonGroup.userData.enabled = enabled;
  if (buttonGroup.userData.button) {
    buttonGroup.userData.button.material = enabled ? enabledMaterial : disabledMaterial;
  }
}

function getPressedButtonAction(buttonMesh) {
  return buttonMesh.userData.action ?? buttonMesh.userData.parentButton?.userData?.action ?? "";
}

function setButtonActionEnabled(
  actionName,
  enabled,
  enabledMaterial = materials.lightOn,
  disabledMaterial = materials.lightOff,
) {
  for (const buttonMesh of state.buttonTargets) {
    if (getPressedButtonAction(buttonMesh) !== actionName) continue;
    setButtonEnabled(buttonMesh.userData.parentButton, enabled, enabledMaterial, disabledMaterial);
  }
}

function setCheckButtonEnabled(enabled) {
  setButtonEnabled(checkButton, enabled, materials.lightOn, materials.socketIdle);
  setButtonActionEnabled("check", enabled, materials.lightOn, materials.socketIdle);
}

function createController(index) {
  const controller = renderer.xr.getController(index);
  controller.userData.index = index;
  controller.userData.selecting = false;
  controller.userData.gripDown = false;
  controller.addEventListener("selectstart", () => {
    if (tryPressLaunchButton(controller)) return;
    tryRayGrab(controller);
  });
  controller.addEventListener("selectend", () => releaseHeld(controller));
  controller.addEventListener("squeezestart", () => grabNearest(controller));
  controller.addEventListener("squeezeend", () => releaseHeld(controller));
  playerRig.add(controller);

  const line = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, -1)]),
    new THREE.LineBasicMaterial({ color: 0xf6c453 }),
  );
  line.name = "controller-ray";
  line.scale.z = 2;
  controller.add(line);

  const grip = renderer.xr.getControllerGrip(index);
  grip.add(controllerModelFactory.createControllerModel(grip));
  playerRig.add(grip);

  return controller;
}

function createPhysicsWorld() {
  const world = new CANNON.World({ gravity: new CANNON.Vec3(0, -9.82, 0) });
  world.broadphase = new CANNON.SAPBroadphase(world);
  world.allowSleep = true;

  const floorBody = new CANNON.Body({ mass: 0, shape: new CANNON.Plane() });
  floorBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
  world.addBody(floorBody);

  return { world, bodies: new Map() };
}

function buttonTargetAlreadyRegistered(mesh) {
  return state.buttonTargets.includes(mesh);
}

function registerBayButtonActionTargets(bayRoot) {
  const actionMatchers = [
    { action: "call", terms: ["call"] },
    { action: "launch", terms: ["send", "launch"] },
    { action: "check", terms: ["check"] },
  ];

  bayRoot.traverse?.((child) => {
    if (!child.isMesh) return;
    const lowerName = child.name.toLowerCase();
    const match = actionMatchers.find(({ terms }) => terms.some((term) => lowerName.includes(term)));
    if (!match) return;

    child.userData.action = child.userData.action ?? match.action;
    child.userData.parentButton = child.userData.parentButton ?? getButtonForAction(match.action);

    if (!buttonTargetAlreadyRegistered(child)) {
      state.buttonTargets.push(child);
    }
  });
}

function bindLoadedBayFunctions(bayRoot) {
  if (!launchButton || !callButton) {
    pendingBayRoot = bayRoot;
    return;
  }

  setupBayDoor(bayRoot);
  bindBayButtonMeshes({
    bayRoot,
    controls: { launchButton, callButton, checkButton },
    buttonTargets: state.buttonTargets,
  });
  applyBayScreenText(bayRoot);
  registerBayButtonActionTargets(bayRoot);
  setButtonEnabled(callButton, Boolean(callButton.userData.enabled), materials.lightOn, materials.socketIdle);
  setButtonEnabled(launchButton, Boolean(launchButton.userData.enabled), materials.lightOn, materials.lightOff);
  setButtonEnabled(checkButton, Boolean(checkButton?.userData?.enabled), materials.lightOn, materials.socketIdle);
  pendingBayRoot = null;
}

function setupBayDoor(bayRoot) {
  const left = createDoorLeafGroup(bayRoot, "Left");
  const right = createDoorLeafGroup(bayRoot, "Right");
  if (!left || !right) {
    console.warn("Bay door animation disabled: unable to find left/right door leaf meshes in Rover_Bay.glb.");
    return;
  }

  state.bayDoor = {
    left,
    right,
    // Carriage-door swing angles.
    leftClosedY: left.rotation.y,
    rightClosedY: right.rotation.y,
    leftOpenY: left.rotation.y + THREE.MathUtils.degToRad(72),
    rightOpenY: right.rotation.y - THREE.MathUtils.degToRad(72),
  };
  applyDoorProgress(0);
}

function createDoorLeafGroup(bayRoot, side) {
  const existingGroup = bayRoot.getObjectByName(`AnimatedBayDoor_${side}`);
  if (existingGroup) return existingGroup;

  const leafObjects = collectDoorLeafObjects(bayRoot, side);
  if (leafObjects.length === 0) return null;

  bayRoot.updateMatrixWorld(true);
  const hingeWorld = getDoorHingeWorldPosition(leafObjects, side);
  const hingeLocal = bayRoot.worldToLocal(hingeWorld.clone());

  const pivot = new THREE.Group();
  pivot.name = `AnimatedBayDoor_${side}`;
  pivot.position.copy(hingeLocal);
  bayRoot.add(pivot);
  pivot.updateMatrixWorld(true);

  // Door leaf mesh grouping.
  for (const object of leafObjects) {
    pivot.attach(object);
  }

  pivot.userData.doorSide = side;
  return pivot;
}

function collectDoorLeafObjects(bayRoot, side) {
  const sideLower = side.toLowerCase();
  const primaryPrefix = `Wall_Front_Sill_${side}Door`;
  const objects = [];
  const excludedTerms = ["jamb", "track", "post", "ramp", "header", "return", "sill"];

  bayRoot.traverse((child) => {
    if (!child.isMesh && child.type !== "Group") return;
    if (child.name === `AnimatedBayDoor_${side}` || child.name.startsWith(`AnimatedBayDoor_${side}_`)) return;

    const lowerName = child.name.toLowerCase();
    const isPrimaryDoorPart = child.name === primaryPrefix || child.name.startsWith(`${primaryPrefix}_`);
    const looksLikeDoorLeaf =
      lowerName.includes("door") &&
      lowerName.includes(sideLower) &&
      !excludedTerms.some((term) => lowerName.includes(term));

    if (isPrimaryDoorPart || looksLikeDoorLeaf) {
      objects.push(child);
    }
  });

  // Door leaf match de-duplication.
  return objects.filter((object) => !objects.some((other) => other !== object && isDescendantOf(object, other)));
}

function getDoorHingeWorldPosition(leafObjects, side) {
  const box = new THREE.Box3();
  for (const object of leafObjects) {
    object.updateMatrixWorld(true);
    box.expandByObject(object);
  }

  const center = box.getCenter(new THREE.Vector3());
  const hingeX = side === "Left" ? box.min.x : box.max.x;
  return new THREE.Vector3(hingeX, center.y, center.z);
}

function isDescendantOf(object, possibleParent) {
  let parent = object.parent;
  while (parent) {
    if (parent === possibleParent) return true;
    parent = parent.parent;
  }
  return false;
}

function easeDoorProgress(progress) {
  const t = THREE.MathUtils.clamp(progress, 0, 1);
  return t * t * t * (t * (t * 6 - 15) + 10);
}

function startDoorMotion(mode) {
  state.doorMode = mode;
  state.doorMoving = true;
  if (!state.bayDoor) {
    finishDoorMotion();
  }
}

function updateDoorMotion(delta) {
  if (!state.doorMoving) return;

  const opening = state.doorMode === "openingForCall" || state.doorMode === "openingForSend";
  const direction = opening ? 1 : -1;
  state.doorProgress = THREE.MathUtils.clamp(state.doorProgress + direction * delta * 0.62, 0, 1);
  applyDoorProgress(state.doorProgress);
  markShadowsDirty();

  if ((opening && state.doorProgress < 1) || (!opening && state.doorProgress > 0)) return;
  finishDoorMotion();
}

function applyDoorProgress(progress) {
  if (!state.bayDoor) return;

  const eased = easeDoorProgress(progress);
  state.bayDoor.left.rotation.y = THREE.MathUtils.lerp(state.bayDoor.leftClosedY, state.bayDoor.leftOpenY, eased);
  state.bayDoor.right.rotation.y = THREE.MathUtils.lerp(state.bayDoor.rightClosedY, state.bayDoor.rightOpenY, eased);
  state.doorOpen = progress >= 0.98;
}

function finishDoorMotion() {
  const mode = state.doorMode;
  state.doorMoving = false;
  state.doorMode = null;
  state.doorOpen = state.doorProgress >= 0.98;

  if (mode === "openingForCall") {
    startRoverCallAfterDoorOpens();
  } else if (mode === "closingAfterCall") {
    activateRepairPhase();
  } else if (mode === "openingForSend") {
    startRoverDepartureAfterDoorOpens();
  } else if (mode === "closingAfterSend") {
    completeRoverDeparture();
  }
}

function removeOldPanelLabelTargets(bayRoot) {
  const oldTargets = [];
  bayRoot.traverse?.((child) => {
    if (child.userData?.clickableLabel) oldTargets.push(child);
  });

  for (const target of oldTargets) {
    state.buttonTargets = state.buttonTargets.filter((object) => object !== target);
    target.parent?.remove(target);
    target.geometry?.dispose?.();
    const material = target.material;
    material?.map?.dispose?.();
    material?.dispose?.();
  }
}

function applyBayScreenText(bayRoot) {
  removeOldPanelLabelTargets(bayRoot);
  applyPanelLabel(bayRoot, bayRoot.getObjectByName("Btn_CallLabel"), "CALL ROVER", {
    accent: "#56d88a",
    action: "call",
  });
  applyPanelLabel(bayRoot, bayRoot.getObjectByName("Btn_SendLabel"), "SEND ROVER", {
    accent: "#f6c453",
    action: "launch",
  });
  applyPanelLabel(bayRoot, bayRoot.getObjectByName("Btn_CheckLabel"), "CHECK", { accent: "#8bd3ff", action: "check" });
  applyStatusScreen(bayRoot);

  const miniScreen = bayRoot.getObjectByName("MiniScreenUI") ?? bayRoot.getObjectByName("MiniScreen");
  if (!miniScreen) return;

  miniScreen.visible = false;
  const box = new THREE.Box3().setFromObject(miniScreen);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const canvas = document.createElement("canvas");
  canvas.width = 2048;
  canvas.height = Math.round(canvas.width * (size.y / size.z));
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.generateMipmaps = false;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(size.z, size.y),
    new THREE.MeshBasicMaterial({ map: texture, side: THREE.FrontSide }),
  );
  screen.name = "MiniScreenTextOverlay";
  screen.position.set(center.x - 0.045, center.y, center.z);
  screen.rotation.y = -Math.PI / 2;
  bayRoot.add(screen);
  state.miniScreen = { canvas, texture };
  drawMiniScreen();
}

function applyStatusScreen(bayRoot) {
  const screenFace = bayRoot.getObjectByName("Screen_Face");
  if (!screenFace) return;

  const box = new THREE.Box3().setFromObject(screenFace);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const canvas = document.createElement("canvas");
  canvas.width = 2048;
  canvas.height = Math.round(canvas.width * (size.y / size.x));
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.generateMipmaps = false;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(size.x, size.y),
    new THREE.MeshBasicMaterial({ map: texture, side: THREE.FrontSide }),
  );
  screen.name = "ScreenFaceStatusOverlay";
  screen.position.set(center.x, center.y, box.min.z - 0.012);
  screen.rotation.y = Math.PI;
  bayRoot.add(screen);
  state.statusScreen = { canvas, texture };
  drawStatusScreen();
}

function applyPanelLabel(bayRoot, mesh, text, { accent, action = "" }) {
  if (!mesh) return;

  mesh.visible = false;
  const box = new THREE.Box3().setFromObject(mesh);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  context.fillStyle = "#15181d";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = accent;
  context.lineWidth = 18;
  context.strokeRect(18, 18, canvas.width - 36, canvas.height - 36);
  context.fillStyle = accent;
  context.fillRect(36, 36, 28, canvas.height - 72);
  context.fillStyle = "#f4f0e6";
  context.font = "900 104px system-ui, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(text, canvas.width / 2 + 20, canvas.height / 2, canvas.width - 110);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const label = new THREE.Mesh(
    new THREE.PlaneGeometry(Math.max(size.z, 0.8) * 0.96, Math.max(size.y, 0.24) * 0.78),
    new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide }),
  );
  label.name = `${mesh.name}TextOverlay`;
  label.position.set(center.x - 0.045, center.y, center.z);
  label.rotation.y = -Math.PI / 2;

  if (action) {
    const parentButton = getButtonForAction(action);
    label.userData.action = action;
    label.userData.parentButton = parentButton;
    label.userData.clickableLabel = true;
    if (!buttonTargetAlreadyRegistered(label)) state.buttonTargets.push(label);

    const hitTarget = new THREE.Mesh(
      label.geometry.clone(),
      new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.01, side: THREE.DoubleSide, depthWrite: false }),
    );
    hitTarget.name = `${mesh.name}_${action}_ClickableHitTarget`;
    hitTarget.position.copy(label.position);
    hitTarget.rotation.copy(label.rotation);
    hitTarget.scale.setScalar(1.08);
    hitTarget.renderOrder = 999;
    hitTarget.userData.action = action;
    hitTarget.userData.parentButton = parentButton;
    hitTarget.userData.clickableLabel = true;
    bayRoot.add(hitTarget);
    if (!buttonTargetAlreadyRegistered(hitTarget)) state.buttonTargets.push(hitTarget);
  }

  bayRoot.add(label);
}

function addBox(name, size, position, material, receiveShadow = false, visible = true) {
  const mesh = meshBox(size, material);
  mesh.name = name;
  mesh.position.fromArray(position);
  mesh.receiveShadow = receiveShadow;
  mesh.castShadow = !receiveShadow;
  mesh.visible = visible;
  mesh.userData.type = ObjectType.STATIC;
  scene.add(mesh);
  addStaticBodyForMesh(mesh, size);
  return mesh;
}

function meshBox(size, material) {
  return new THREE.Mesh(new THREE.BoxGeometry(size[0], size[1], size[2]), material);
}

function addPhysicsBox(object, size, mass) {
  const shape = new CANNON.Box(new CANNON.Vec3(size[0] / 2, size[1] / 2, size[2] / 2));
  const body = new CANNON.Body({ mass, shape, position: toCannonVec(object.position) });
  body.quaternion.copy(toCannonQuat(object.quaternion));
  body.type = CANNON.Body.KINEMATIC;
  body.linearDamping = 0.2;
  body.angularDamping = 0.45;
  physics.world.addBody(body);
  physics.bodies.set(object, body);
  return body;
}

function addStaticBodyForMesh(mesh, size) {
  mesh.updateMatrixWorld(true);
  const worldPosition = mesh.getWorldPosition(new THREE.Vector3());
  const worldQuaternion = mesh.getWorldQuaternion(new THREE.Quaternion());
  const worldScale = mesh.getWorldScale(new THREE.Vector3());
  const halfExtents = new CANNON.Vec3(
    (size[0] * worldScale.x) / 2,
    (size[1] * worldScale.y) / 2,
    (size[2] * worldScale.z) / 2,
  );
  const body = new CANNON.Body({
    mass: 0,
    shape: new CANNON.Box(halfExtents),
  });
  body.position.copy(toCannonVec(worldPosition));
  body.quaternion.copy(toCannonQuat(worldQuaternion));

  physics.world.addBody(body);
  state.staticPhysicsMeshes.push({ mesh, body });
  return body;
}

function tryRayGrab(controller) {
  updateControllerRaycaster(controller);
  const intersections = raycaster.intersectObjects(state.grabbables, true);
  const hit = intersections.find((intersection) => getGrabbableRoot(intersection.object));
  if (!hit) return false;

  const object = getGrabbableRoot(hit.object);
  if (!object || !object.userData.grabbable || object.userData.locked) return false;

  const body = physics.bodies.get(object);
  if (body) {
    body.type = CANNON.Body.KINEMATIC;
    body.velocity.setZero();
    body.angularVelocity.setZero();
  }

  setObjectHighlight(object, true);
  controller.attach(object);
  applyHeldGripPose(object);
  state.held.set(controller, object);
  return true;
}

function tryPressLaunchButton(controller) {
  updateControllerRaycaster(controller);
  const intersections = raycaster.intersectObjects(state.buttonTargets, false);
  const hit = intersections.find(
    (intersection) => intersection.distance <= 3 && getPressedButtonAction(intersection.object),
  );
  if (!hit) return false;

  return pressButton(hit.object);
}

function grabNearest(controller) {
  let nearest = null;
  let nearestDistance = 0.45;
  const controllerPosition = new THREE.Vector3();
  controller.getWorldPosition(controllerPosition);

  for (const object of state.grabbables) {
    if (!object.userData.grabbable || object.userData.locked) continue;
    const distance = controllerPosition.distanceTo(object.getWorldPosition(new THREE.Vector3()));
    if (distance < nearestDistance) {
      nearest = object;
      nearestDistance = distance;
    }
  }

  if (!nearest) return;

  const body = physics.bodies.get(nearest);
  if (body) {
    body.type = CANNON.Body.KINEMATIC;
    body.velocity.setZero();
    body.angularVelocity.setZero();
  }

  controller.attach(nearest);
  applyHeldGripPose(nearest);
  state.held.set(controller, nearest);
}

function applyHeldGripPose(object) {
  if (object.userData.type !== ObjectType.REPAIR_TOOL) return;

  const gripPoint = object.getObjectByName("RR_RepairTool_GripPoint");
  const tipPoint = object.getObjectByName("RR_RepairTool_TipUsePoint");
  if (!gripPoint || !tipPoint) {
    object.position.copy(REPAIR_TOOL_GRIP_OFFSET);
    object.rotation.set(0, Math.PI, 0);
    return;
  }

  object.updateMatrixWorld(true);
  const gripLocal = object.worldToLocal(gripPoint.getWorldPosition(new THREE.Vector3()));
  const tipLocal = object.worldToLocal(tipPoint.getWorldPosition(new THREE.Vector3()));
  const barrelDirection = tipLocal.clone().sub(gripLocal);
  if (barrelDirection.lengthSq() < 0.0001) return;

  barrelDirection.normalize();
  const gripQuaternion = new THREE.Quaternion().setFromUnitVectors(barrelDirection, REPAIR_TOOL_FORWARD);
  const downReference = getRepairToolDownReference(object, gripLocal);

  if (downReference) {
    const currentDown = downReference.clone().applyQuaternion(gripQuaternion);
    currentDown.addScaledVector(REPAIR_TOOL_FORWARD, -currentDown.dot(REPAIR_TOOL_FORWARD));
    if (currentDown.lengthSq() > 0.0001) {
      currentDown.normalize();
      const cross = currentDown.clone().cross(REPAIR_TOOL_DOWN);
      const rollAngle = Math.atan2(REPAIR_TOOL_FORWARD.dot(cross), currentDown.dot(REPAIR_TOOL_DOWN));
      const rollQuaternion = new THREE.Quaternion().setFromAxisAngle(REPAIR_TOOL_FORWARD, rollAngle);
      gripQuaternion.premultiply(rollQuaternion);
    }
  }

  object.quaternion.copy(gripQuaternion);
  object.position.copy(REPAIR_TOOL_GRIP_OFFSET).sub(gripLocal.applyQuaternion(object.quaternion));
}

function getRepairToolDownReference(object, gripLocal) {
  const reference =
    object.getObjectByName("RR_RepairTool_Angled_Grip") ??
    object.getObjectByName("RR_RepairTool_Orange_Grip_Base") ??
    object.getObjectByName("RR_RepairTool_Trigger");

  if (!reference) return null;

  object.updateMatrixWorld(true);
  const referenceLocal = object.worldToLocal(reference.getWorldPosition(new THREE.Vector3()));
  const downReference = referenceLocal.sub(gripLocal);
  return downReference.lengthSq() > 0.0001 ? downReference.normalize() : null;
}

function releaseHeld(controller) {
  const object = state.held.get(controller);
  if (!object) return;

  scene.attach(object);
  state.held.delete(controller);
  setObjectHighlight(object, false);

  if (object.userData.locked) return;

  const body = physics.bodies.get(object);
  if (body) {
    body.type = CANNON.Body.DYNAMIC;
    body.position.copy(toCannonVec(object.position));
    body.quaternion.copy(toCannonQuat(object.quaternion));
    body.wakeUp();
  }
}

function updateControllerRaycaster(controller) {
  controller.updateMatrixWorld(true);
  raycastMatrix.identity().extractRotation(controller.matrixWorld);
  raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
  raycaster.ray.direction.set(0, 0, -1).applyMatrix4(raycastMatrix);
}

function getGrabbableRoot(object) {
  let current = object;
  while (current) {
    if (state.grabbables.includes(current)) return current;
    current = current.parent;
  }
  return null;
}

function setObjectHighlight(object, highlighted) {
  object.traverse?.((child) => {
    if (child.material?.emissive) {
      child.material.emissive.setHex(highlighted ? 0x112244 : 0x000000);
    }
  });

  if (object.material?.emissive) {
    object.material.emissive.setHex(highlighted ? 0x112244 : 0x000000);
  }
}

function onPointerDown(event) {
  if (renderer.xr.isPresenting || event.button !== 0) return;
  updatePointerRaycaster(event);

  if (tryPressLaunchButtonFromPointer()) return;

  const hit = raycaster
    .intersectObjects(state.grabbables, true)
    .find((intersection) => getGrabbableRoot(intersection.object));
  if (!hit) return;

  mouseHeld = getGrabbableRoot(hit.object);
  if (!mouseHeld || !mouseHeld.userData.grabbable || mouseHeld.userData.locked) {
    mouseHeld = null;
    return;
  }

  const body = physics.bodies.get(mouseHeld);
  if (body) {
    body.type = CANNON.Body.KINEMATIC;
    body.velocity.setZero();
    body.angularVelocity.setZero();
  }

  setObjectHighlight(mouseHeld, true);
  dragPlane.constant = -mouseHeld.position.y;
  renderer.domElement.setPointerCapture(event.pointerId);
}

function tryPressLaunchButtonFromPointer() {
  const intersections = raycaster.intersectObjects(state.buttonTargets, false);
  if (intersections.length === 0) return false;

  return pressButton(intersections[0].object);
}

function pressButton(buttonMesh) {
  const action = getPressedButtonAction(buttonMesh);
  const buttonGroup = buttonMesh.userData.parentButton ?? getButtonForAction(action);
  if (!buttonGroup?.userData.enabled) return false;

  if (buttonMesh.userData.clickableLabel && buttonGroup.userData.button?.material) {
    buttonGroup.userData.button.material = materials.lightOn;
  }

  if (action === "launch" || action === "send") {
    sendRoverOut();
    return true;
  }

  if (action === "call") {
    callInRover();
    return true;
  }

  if (action === "check") {
    checkRoverForLevel();
    return true;
  }

  return false;
}

function onPointerMove(event) {
  updatePointerRaycaster(event);
  if (!mouseHeld) return;
  if (!raycaster.ray.intersectPlane(dragPlane, dragHit)) return;

  mouseHeld.position.copy(dragHit);
  const body = physics.bodies.get(mouseHeld);
  if (body) {
    body.position.copy(toCannonVec(mouseHeld.position));
    body.quaternion.copy(toCannonQuat(mouseHeld.quaternion));
  }
}

function onPointerUp(event) {
  if (!mouseHeld) return;

  setObjectHighlight(mouseHeld, false);
  const body = physics.bodies.get(mouseHeld);
  if (body) {
    body.type = CANNON.Body.DYNAMIC;
    body.position.copy(toCannonVec(mouseHeld.position));
    body.quaternion.copy(toCannonQuat(mouseHeld.quaternion));
    body.wakeUp();
  }

  mouseHeld = null;
  renderer.domElement.releasePointerCapture(event.pointerId);
}

function updatePointerRaycaster(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
}

function removeRoverStaticBodies() {
  if (!rover) return;
  for (const body of rover.group.userData.staticBodies ?? []) {
    physics.world.removeBody(body);
  }
  rover.group.userData.staticBodies = [];
}

function addRoverStaticBodies(group = rover.group) {
  if (!group) return;
  group.updateMatrixWorld(true);
  group.userData.staticBodies = [];

  for (const mesh of group.userData.staticMeshes ?? []) {
    const staticBody = addStaticBodyForMesh(mesh, mesh.userData.physicsSize);
    group.userData.staticBodies.push(staticBody);
  }
}

function removePlayerObstacle(id) {
  playerCollider.obstacles = playerCollider.obstacles.filter((obstacle) => obstacle.id !== id);
}

function spawnPowerModuleForLevel() {
  removePowerModule({ resetInstallState: false });
  if (!state.currentLevelConfig.requiresPowerCell) return;

  const spawnCount = Math.max(0, getRequiredPowerCellCount() - state.installedPowerCellSlots.size);

  powerModules = [];
  for (let index = 0; index < spawnCount; index += 1) {
    const createdPowerModule = createPowerModuleAsset({
      scene,
      materials,
      meshBox,
      addPhysicsBox,
      grabbables: state.grabbables,
      name: index === 0 ? "powerModule" : `powerModule${index + 1}`,
      position: getToolTableSpawnPosition(index).toArray(),
    });
    const module = getPowerModuleFromCreateResult(createdPowerModule);
    if (module) powerModules.push(module);
  }
  powerModule = powerModules[0] ?? null;
}

function removePowerModule({ resetInstallState = true } = {}) {
  const modules = getPowerModules();
  if (modules.length === 0) return;

  for (const module of modules) {
    for (const [controller, heldObject] of state.held) {
      if (heldObject === module) state.held.delete(controller);
    }
    if (mouseHeld === module) mouseHeld = null;

    const body = physics.bodies.get(module);
    if (body) {
      physics.world.removeBody(body);
      physics.bodies.delete(module);
    }

    state.grabbables = state.grabbables.filter((object) => object !== module);
    module.parent?.remove(module);
  }

  powerModules = [];
  powerModule = null;
  if (resetInstallState) {
    state.installedPowerCellSlots.clear();
    state.preinstalledPowerCellSlotsVisualized.clear();
    state.powerModuleInstalled = false;
  }
  state.powerSnapCheckTimer = 0;
}

function resetPowerCellInstallStateForLevel() {
  state.installedPowerCellSlots.clear();
  state.preinstalledPowerCellSlotsVisualized.clear();

  for (const slotId of state.currentLevelConfig.initialPowerCellSlots ?? []) {
    state.installedPowerCellSlots.add(slotId);
  }

  state.powerModuleInstalled = hasRequiredPowerCellsInstalled();
}

function createPreinstalledPowerCellsForLevel() {
  if (!rover?.group || !state.currentLevelConfig.requiresPowerCell) return;

  for (const slotId of state.currentLevelConfig.initialPowerCellSlots ?? []) {
    if (state.preinstalledPowerCellSlotsVisualized.has(slotId)) continue;

    const slot = getPowerCellSlotDefinition(slotId);
    const module = getPowerModuleFromCreateResult(
      createPowerModuleAsset({
        scene,
        materials,
        meshBox,
        addPhysicsBox,
        grabbables: state.grabbables,
        name: `preinstalledPowerModule${slotId}`,
        position: getToolTableSpawnPosition(powerModules.length).toArray(),
      }),
    );
    if (!module) continue;

    powerModules.push(module);
    snapPowerModuleToRover(module, slot, {
      awardScore: false,
      updateObjectiveText: false,
      enableCheckButton: false,
    });
    state.preinstalledPowerCellSlotsVisualized.add(slotId);
  }
}

function clearLevelInteractionObjects() {
  state.repairAimTargetId = null;
  state.repairAimTimer = 0;
  state.partSnapCheckTimer = 0;
  state.roverInteractionsReady = false;

  for (const part of state.missingParts) {
    removeLooseMissingPart(part);
    part.snapMarker?.parent?.remove(part.snapMarker);

    if (part.sourceMeshes && part.sourceMeshes.length > 0) {
      for (const mesh of part.sourceMeshes) setObjectVisible(mesh, true);
    } else if (part.sourceRoot) {
      setObjectVisible(part.sourceRoot, true);
    }

    if (part.sourceRoot && part.sourceRoot.name.includes("_VirtualRoot")) {
      part.sourceRoot.parent?.remove(part.sourceRoot);
    }
    if (part.snapTarget && part.snapTarget.name.includes("_VirtualSnapTarget")) {
      part.snapTarget.parent?.remove(part.snapTarget);
    }
    if (part.wheelId) {
      const wheelPivot = rover?.wheels?.find((wheel) => wheel.userData.wheelId === part.wheelId);
      if (wheelPivot) wheelPivot.userData.spinEnabled = true;
    }

    part.sourceRoot = null;
    part.sourceMeshes = null;
    part.snapTarget = null;
  }

  for (const target of state.repairTargets) {
    setRepairTargetGlow(target, "off");
  }

  state.missingParts = [];
  state.repairTargets = [];
}

function removeLooseMissingPart(part) {
  const looseObject = part?.looseObject;
  if (!looseObject) return;

  for (const [controller, heldObject] of state.held) {
    if (heldObject === looseObject) state.held.delete(controller);
  }
  if (mouseHeld === looseObject) mouseHeld = null;

  const body = physics.bodies.get(looseObject);
  if (body) {
    physics.world.removeBody(body);
    physics.bodies.delete(looseObject);
  }

  state.grabbables = state.grabbables.filter((object) => object !== looseObject);
  looseObject.parent?.remove(looseObject);
  part.looseObject = null;
}

function collectMissingPartMeshes(definition, root) {
  const meshes = [];
  if (definition.meshNames) {
    for (const name of definition.meshNames) {
      const mesh = root.getObjectByName(name);
      if (mesh) meshes.push(mesh);
    }
  }
  if (definition.meshNamePattern) {
    root.traverse((child) => {
      if (child.isMesh && definition.meshNamePattern.test(child.name)) {
        meshes.push(child);
      }
    });
  }
  return meshes;
}

function createVirtualPartRoot(definition, meshes) {
  if (meshes.length === 0) return null;
  const group = new THREE.Group();
  group.name = `${definition.id}_VirtualRoot`;

  rover.group.updateMatrixWorld(true);
  const box = new THREE.Box3();
  for (const mesh of meshes) {
    mesh.updateMatrixWorld(true);
    box.expandByObject(mesh);
  }

  const center = box.getCenter(new THREE.Vector3());
  group.position.copy(rover.group.worldToLocal(center));
  rover.group.add(group);
  return group;
}

function createVirtualSnapTarget(definition, sourceRoot = null) {
  if (!definition.snapLocalPosition && !sourceRoot) return null;
  const target = new THREE.Object3D();
  target.name = `${definition.id}_VirtualSnapTarget`;

  if (definition.snapLocalPosition) {
    target.position.copy(definition.snapLocalPosition);
    rover.group.add(target);
  } else {
    target.position.copy(sourceRoot.getWorldPosition(new THREE.Vector3()));
    scene.add(target);
    rover.group.attach(target);
  }

  return target;
}

function setupLevelRoverInteractions(model) {
  if (!rover?.group || model.parent !== rover.group) return;

  clearLevelInteractionObjects();
  rover.group.updateMatrixWorld(true);
  createPreinstalledPowerCellsForLevel();

  const activeMissingPartIds = new Set(state.currentLevelConfig.missingPartIds);
  const activeRepairTargetIds = new Set(state.currentLevelConfig.repairTargetIds);
  const missingPartSpawnOffset = getPowerModules().filter((module) => !module.userData.locked).length;

  state.missingParts = missingPartDefinitions
    .filter((definition) => activeMissingPartIds.has(definition.id))
    .map((definition, index) => {
      const sourceMeshes = collectMissingPartMeshes(definition, rover.group);
      const sourceRoot = definition.rootName
        ? rover.group.getObjectByName(definition.rootName)
        : createVirtualPartRoot(definition, sourceMeshes);

      const namedSnapTarget = definition.snapTargetName ? rover.group.getObjectByName(definition.snapTargetName) : null;
      const snapTarget = namedSnapTarget ?? createVirtualSnapTarget(definition, sourceRoot);

      const part = {
        ...definition,
        spawnPosition: getToolTableSpawnPosition(missingPartSpawnOffset + index),
        sourceRoot,
        sourceMeshes,
        snapTarget,
        snapMarker: null,
        looseObject: null,
        installed: false,
      };

      if (!sourceRoot || !snapTarget) {
        console.warn(`Missing part setup skipped for ${definition.id}: source or snap target not found.`);
        return part;
      }

      if (sourceMeshes && sourceMeshes.length > 0) {
        for (const mesh of sourceMeshes) setObjectVisible(mesh, false);
      } else {
        setObjectVisible(sourceRoot, false);
      }

      if (definition.wheelId) {
        const wheelPivot = rover.wheels?.find((w) => w.userData.wheelId === definition.wheelId);
        if (wheelPivot) {
          wheelPivot.userData.spinEnabled = false;
        }
      }

      spawnLooseMissingPart(part);
      part.snapMarker = createMissingPartSnapMarker(part);
      return part;
    });

  state.repairTargets = repairPartDefinitions
    .filter((definition) => activeRepairTargetIds.has(definition.id))
    .map((definition) => {
      const root = definition.rootName ? rover.group.getObjectByName(definition.rootName) : null;
      const meshes = collectRepairTargetMeshes(definition, root);
      const usePoint =
        (definition.usePointName ? rover.group.getObjectByName(definition.usePointName) : null) ??
        createVirtualRepairUsePoint(definition, meshes) ??
        root;
      const target = {
        ...definition,
        root,
        usePoint,
        repaired: false,
        meshes,
        pulseObjects: getRepairPulseObjects(root, meshes),
        glowState: "off",
      };

      if (!root && meshes.length === 0) {
        console.warn(`Repair target setup skipped for ${definition.id}: no matching rover meshes found.`);
        return target;
      }

      for (const child of meshes) {
        prepareRepairTargetMaterial(child);
      }
      setRepairTargetGlow(target, "off");
      return target;
    });

  state.roverInteractionsReady = true;
  setCheckButtonEnabled(!state.roverArriving && !state.roverTurning && !state.doorMoving && !state.doorOpen);
  markShadowsDirty();
  updateObjective(getNextRepairObjective());
}

function spawnLooseMissingPart(part) {
  if (!part.sourceRoot && (!part.sourceMeshes || part.sourceMeshes.length === 0)) return;

  const group = new THREE.Group();
  group.name = `missingPart_${part.id}`;
  group.position.copy(part.spawnPosition);
  group.userData = {
    type: ObjectType.MISSING_PART,
    missingPartId: part.id,
    grabbable: true,
    locked: false,
    physicsSize: part.physicsSize ?? [0.45, 0.35, 0.45],
  };
  scene.add(group);

  const clone = new THREE.Group();
  clone.name = `${part.id}_looseVisual`;

  if (part.sourceMeshes && part.sourceMeshes.length > 0) {
    for (const mesh of part.sourceMeshes) {
      const meshClone = mesh.clone(true);
      part.sourceRoot.updateMatrixWorld(true);
      mesh.updateMatrixWorld(true);
      const localMat = mesh.matrixWorld.clone().premultiply(part.sourceRoot.matrixWorld.clone().invert());
      meshClone.applyMatrix4(localMat);
      clone.add(meshClone);
    }
  } else if (part.sourceRoot) {
    const rootClone = part.sourceRoot.clone(true);
    const sourceWorldScale = part.sourceRoot.getWorldScale(new THREE.Vector3());
    rootClone.position.set(0, 0, 0);
    rootClone.quaternion.identity();
    rootClone.scale.copy(sourceWorldScale);
    clone.add(rootClone);
  }

  setObjectVisible(clone, true);
  clone.traverse?.((child) => {
    if (!child.isMesh) return;
    child.material = cloneMaterial(child.material);
    child.castShadow = true;
    child.receiveShadow = true;
  });
  group.add(clone);

  group.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const localCenter = group.worldToLocal(center.clone());
  clone.position.sub(localCenter);
  group.updateMatrixWorld(true);

  const normalizedBox = new THREE.Box3().setFromObject(group);
  const normalizedSize = normalizedBox.getSize(new THREE.Vector3());
  const physicsSize = part.physicsSize ?? [
    Math.max(normalizedSize.x, 0.28),
    Math.max(normalizedSize.y, 0.22),
    Math.max(normalizedSize.z, 0.28),
  ];
  group.userData.physicsSize = physicsSize;
  group.position.y = rackSurfaces[0].y + physicsSize[1] / 2 + 0.04;

  const hitBox = meshBox(physicsSize, materials.roverDark);
  hitBox.name = `${group.name}GrabBox`;
  hitBox.visible = false;
  group.add(hitBox);

  addPhysicsBox(group, physicsSize, 1.25);
  state.grabbables.push(group);
  part.looseObject = group;
}

function createMissingPartSnapMarker(part) {
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 16, 8),
    new THREE.MeshBasicMaterial({
      color: 0xf6c453,
      transparent: true,
      opacity: 0.72,
      depthWrite: false,
    }),
  );
  marker.name = `${part.id}_SnapGlow`;
  marker.visible = false;
  marker.position.copy(part.snapTarget.getWorldPosition(new THREE.Vector3()));
  scene.add(marker);
  rover.group.attach(marker);
  return marker;
}

function collectRepairTargetMeshes(definition, root) {
  const meshes = [];
  const addMesh = (object) => {
    if (object?.isMesh && !meshes.includes(object)) meshes.push(object);
  };

  root?.traverse?.((child) => addMesh(child));

  for (const name of definition.meshNames ?? []) {
    addMesh(rover.group.getObjectByName(name));
  }

  if (definition.meshNamePattern) {
    rover.group.traverse?.((child) => {
      if (child.isMesh && definition.meshNamePattern.test(child.name)) addMesh(child);
    });
  }

  return meshes;
}

function createVirtualRepairUsePoint(definition, meshes) {
  if (meshes.length === 0) return null;

  rover.group.updateMatrixWorld(true);
  const box = new THREE.Box3();
  for (const mesh of meshes) box.expandByObject(mesh);
  const center = box.getCenter(new THREE.Vector3());
  const marker = new THREE.Object3D();
  marker.name = `${definition.id}_VirtualUsePoint`;
  marker.position.copy(center);
  scene.add(marker);
  rover.group.attach(marker);
  return marker;
}

function cloneMaterial(material) {
  if (Array.isArray(material)) return material.map((item) => cloneMaterial(item));
  return material?.clone?.() ?? material;
}

function setObjectVisible(object, visible) {
  if (!object) return;
  object.visible = visible;
  object.traverse?.((child) => {
    child.visible = visible;
  });
}

function prepareRepairTargetMaterial(mesh) {
  mesh.material = cloneMaterial(mesh.material);
  const materialsToPrepare = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  for (const material of materialsToPrepare) {
    if (!material) continue;
    material.userData.baseEmissive = material.emissive?.clone?.() ?? new THREE.Color(0x000000);
    material.userData.baseEmissiveIntensity = material.emissiveIntensity ?? 1;
  }

  prepareRepairPulseObject(mesh);
}

function getRepairPulseObjects(root, meshes) {
  const objects = [];

  if (root && root !== rover?.group) {
    objects.push(root);
  } else {
    for (const mesh of meshes ?? []) {
      if (!mesh || objects.some((object) => object === mesh || isDescendantOf(mesh, object))) continue;
      objects.push(mesh);
    }
  }

  for (const object of objects) prepareRepairPulseObject(object);
  return objects;
}

function prepareRepairPulseObject(object) {
  if (!object?.userData) return;
  object.userData.repairBaseScale = object.userData.repairBaseScale ?? object.scale.clone();
}

function setRepairPulseScale(target, scaleMultiplier = 1) {
  for (const object of target?.pulseObjects ?? []) {
    prepareRepairPulseObject(object);
    const baseScale = object.userData.repairBaseScale ?? new THREE.Vector3(1, 1, 1);
    object.scale.copy(baseScale).multiplyScalar(scaleMultiplier);
  }
}

function getRepairProgressColor(progress) {
  const clampedProgress = THREE.MathUtils.clamp(progress, 0, 1);
  const red = new THREE.Color(0xff2b1f);
  const orange = new THREE.Color(0xff8a1f);
  const yellow = new THREE.Color(0xffeb3b);
  const green = new THREE.Color(0x28ff7a);

  if (clampedProgress < 1 / 3) {
    return new THREE.Color().lerpColors(red, orange, clampedProgress * 3);
  }

  if (clampedProgress < 2 / 3) {
    return new THREE.Color().lerpColors(orange, yellow, (clampedProgress - 1 / 3) * 3);
  }

  return new THREE.Color().lerpColors(yellow, green, (clampedProgress - 2 / 3) * 3);
}

function setRepairTargetGlow(target, stateName, pulse = 1, progress = 0) {
  if (!target || (target.glowState === stateName && stateName !== "damaged" && stateName !== "repairing")) return;

  const colorByState = {
    damaged: new THREE.Color(0xff2b1f),
    fixed: new THREE.Color(0x28ff7a),
    repairing: getRepairProgressColor(progress),
  };
  const intensityByState = {
    off: 0,
    damaged: 0.65 + pulse * 0.65,
    fixed: 0.95,
    repairing: 0.85 + pulse * 0.85,
  };

  const scaleMultiplier =
    stateName === "repairing"
      ? 1 + Math.sin(state.repairGlowTime * 8) * (0.012 + THREE.MathUtils.clamp(progress, 0, 1) * 0.018)
      : 1;
  setRepairPulseScale(target, scaleMultiplier);

  for (const child of target.meshes ?? []) {
    const targetMaterials = Array.isArray(child.material) ? child.material : [child.material];
    for (const material of targetMaterials) {
      if (!material?.emissive) continue;
      if (stateName === "off") {
        material.emissive.copy(material.userData.baseEmissive ?? new THREE.Color(0x000000));
        material.emissiveIntensity = material.userData.baseEmissiveIntensity ?? 1;
      } else {
        material.emissive.copy(colorByState[stateName] ?? new THREE.Color(0x000000));
        material.emissiveIntensity = intensityByState[stateName] ?? 0;
      }
    }
  }

  target.glowState = stateName;
}

function isMissingPartInstalled(partId) {
  const part = state.missingParts.find((item) => item.id === partId);
  return !part || part.installed;
}

function isRepairTargetActive(target) {
  if (!target || target.meshes.length === 0) return false;
  if (target.missingPartId && !isMissingPartInstalled(target.missingPartId)) return false;
  return target.meshes.some((mesh) => mesh.visible !== false);
}

function getHeldRepairToolController() {
  const tool = getRepairTool();
  if (!tool || tool.userData.locked) return null;

  for (const [controller, heldObject] of state.held) {
    if (heldObject === tool) return controller;
  }
  return null;
}

function getRepairTool() {
  if (repairTool?.parent) return repairTool;

  repairTool =
    state.grabbables.find((object) => {
      const name = object.name.toLowerCase();
      return name.includes("repair") || name.includes("scan") || object.userData.type === ObjectType.REPAIR_TOOL;
    }) ?? null;
  return repairTool;
}

function isRepairToolCurrentlyHeld() {
  const tool = getRepairTool();
  if (!tool) return false;
  if (mouseHeld === tool) return true;
  return Boolean(getHeldRepairToolController());
}

function getHeldMissingPart() {
  const heldObjects = [mouseHeld, ...state.held.values()].filter(Boolean);
  return heldObjects.find((object) => object.userData.type === ObjectType.MISSING_PART) ?? null;
}

function updateRepairInteractions(delta) {
  state.repairGlowTime += delta;

  const scanToolHeld = isRepairToolCurrentlyHeld();
  const hitTarget = scanToolHeld ? getRepairTipTouchTarget() : null;

  if (hitTarget && hitTarget.id === state.repairAimTargetId) {
    state.repairAimTimer += delta;
  } else {
    state.repairAimTargetId = hitTarget?.id ?? null;
    state.repairAimTimer = hitTarget ? delta : 0;
  }

  const activeRepairProgress = hitTarget
    ? THREE.MathUtils.clamp(state.repairAimTimer / state.repairDwellTime, 0, 1)
    : 0;

  if (hitTarget && activeRepairProgress >= 1) {
    repairTarget(hitTarget);
    state.repairAimTargetId = null;
    state.repairAimTimer = 0;
  }

  const pulse = (Math.sin(state.repairGlowTime * 5.5) + 1) / 2;
  for (const target of state.repairTargets) {
    if (!isRepairTargetActive(target)) {
      setRepairTargetGlow(target, "off");
    } else if (target.repaired) {
      // Repaired target display state.
      setRepairTargetGlow(target, state.roverGoodForLevel ? "off" : "fixed");
    } else if (target === hitTarget) {
      setRepairTargetGlow(target, "repairing", pulse, activeRepairProgress);
    } else if (scanToolHeld) {
      setRepairTargetGlow(target, "damaged", pulse);
    } else {
      setRepairTargetGlow(target, "off");
    }
  }
}

function getRepairTipTouchTarget() {
  const activeTargets = state.repairTargets.filter((target) => isRepairTargetActive(target) && !target.repaired);
  if (activeTargets.length === 0) return null;

  const tipPosition = getRepairToolTipWorldPosition();
  if (!tipPosition) return null;

  let bestTarget = null;
  let bestDistance = state.repairTipReachDistance;

  for (const target of activeTargets) {
    const distance = getDistanceFromTipToRepairTarget(tipPosition, target);
    if (distance > bestDistance) continue;

    bestDistance = distance;
    bestTarget = target;
  }

  return bestTarget;
}

function getRepairToolTipWorldPosition() {
  const tool = getRepairTool();
  if (!tool || !isRepairToolCurrentlyHeld()) return null;

  tool.updateMatrixWorld(true);
  const namedTip = tool.getObjectByName("RR_RepairTool_TipUsePoint") ?? findRepairToolTipObject(tool);

  if (namedTip) return namedTip.getWorldPosition(new THREE.Vector3());

  // Repair tool tip marker.
  const fallbackTip = new THREE.Vector3(0.54, 0, 0);
  return tool.localToWorld(fallbackTip);
}

function findRepairToolTipObject(tool) {
  let tipObject = null;
  tool.traverse?.((child) => {
    if (tipObject) return;
    const lowerName = child.name?.toLowerCase?.() ?? "";
    if (lowerName.includes("tip") || lowerName.includes("nozzle")) tipObject = child;
  });
  return tipObject;
}

function getDistanceFromTipToRepairTarget(tipPosition, target) {
  let bestDistance = Infinity;

  const usePoint = target.usePoint?.getWorldPosition(new THREE.Vector3());
  if (usePoint) bestDistance = Math.min(bestDistance, tipPosition.distanceTo(usePoint));

  const targetBox = new THREE.Box3();
  for (const mesh of target.meshes ?? []) {
    if (mesh.visible === false) continue;
    targetBox.expandByObject(mesh);
  }

  if (!targetBox.isEmpty()) {
    bestDistance = Math.min(bestDistance, targetBox.distanceToPoint(tipPosition));
  }

  return bestDistance;
}

function repairTarget(target) {
  if (!target || target.repaired) return;

  target.repaired = true;
  setRepairTargetGlow(target, "fixed");
  state.score += 50;
  state.roverChecked = false;
  state.roverGoodForLevel = false;
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  updateHud();
  updateObjective(`${capitalize(target.label)} fixed. ${getNextRepairObjective()}`);
}

function updateMissingPartSnapThrottled(delta) {
  const heldPart = getHeldMissingPart();
  updateMissingPartSnapMarkers(heldPart);

  if (!heldPart) {
    state.partSnapCheckTimer = 0;
    return;
  }

  state.partSnapCheckTimer -= delta;
  if (state.partSnapCheckTimer > 0) return;

  state.partSnapCheckTimer = state.partSnapCheckInterval;
  updateMissingPartSnap();
}

function updateMissingPartSnapMarkers(heldPartObject) {
  for (const part of state.missingParts) {
    if (!part.snapMarker) continue;
    const isHeldMatch = heldPartObject && part.looseObject === heldPartObject && !part.installed;
    const distance = isHeldMatch
      ? heldPartObject
          .getWorldPosition(new THREE.Vector3())
          .distanceTo(part.snapTarget.getWorldPosition(new THREE.Vector3()))
      : Infinity;
    const visible = distance <= state.partSnapDistance * 1.85;
    part.snapMarker.visible = visible;
    if (visible) {
      const pulse = 1 + Math.sin(state.repairGlowTime * 8) * 0.18;
      part.snapMarker.scale.setScalar(pulse);
    }
  }
}

function updateMissingPartSnap() {
  if (!rover || state.roverArriving || state.roverTurning || state.roverLeaving || state.roverLeavingTurning) return;

  const heldPartObject = getHeldMissingPart();
  if (!heldPartObject) return;

  const part = state.missingParts.find((item) => item.looseObject === heldPartObject && !item.installed);
  if (!part?.snapTarget) return;

  const partPosition = heldPartObject.getWorldPosition(new THREE.Vector3());
  const snapPosition = part.snapTarget.getWorldPosition(new THREE.Vector3());
  if (partPosition.distanceTo(snapPosition) > state.partSnapDistance) return;

  snapMissingPartToRover(part);
}

function snapMissingPartToRover(part) {
  const looseObject = part.looseObject;
  if (!looseObject || part.installed) return;

  for (const [controller, heldObject] of state.held) {
    if (heldObject === looseObject) state.held.delete(controller);
  }
  if (mouseHeld === looseObject) mouseHeld = null;

  removeLooseMissingPart(part);
  part.snapMarker?.parent?.remove(part.snapMarker);
  part.snapMarker = null;

  if (part.sourceMeshes && part.sourceMeshes.length > 0) {
    for (const mesh of part.sourceMeshes) setObjectVisible(mesh, true);
  } else if (part.sourceRoot) {
    setObjectVisible(part.sourceRoot, true);
  }

  if (part.wheelId) {
    const wheelPivot = rover.wheels?.find((w) => w.userData.wheelId === part.wheelId);
    if (wheelPivot) {
      wheelPivot.userData.spinEnabled = true;
    }
  }

  markShadowsDirty();
  part.installed = true;
  state.partSnapCheckTimer = 0;
  state.score += 75;
  state.roverChecked = false;
  state.roverGoodForLevel = false;
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  updateHud();
  updateObjective(`${capitalize(part.label)} installed. ${getNextRepairObjective()}`);
}

function getNextRepairObjective() {
  if (!rover) return "Press CALL ROVER.";
  if (state.doorMoving) return state.doorMode?.includes("opening") ? "OPENING BAY DOOR" : "CLOSING BAY DOOR";
  if (state.roverArriving || state.roverTurning) return "Rover arriving.";
  if (!state.roverInteractionsReady) return "Loading rover repair targets.";
  return getIncompleteLevelRequirement();
}

function allMissingPartsInstalled() {
  return state.missingParts.every((part) => part.installed);
}

function allRepairTargetsFixed() {
  return state.repairTargets.every((target) => !isRepairTargetActive(target) || target.repaired);
}

function clearFixedRepairHighlights() {
  for (const target of state.repairTargets) {
    if (target.repaired) {
      setRepairTargetGlow(target, "off");
    }
  }
}

function getIncompleteLevelRequirement() {
  if (state.currentLevelConfig.requiresPowerCell && !hasRequiredPowerCellsInstalled()) {
    const openSlots = getOpenPowerCellSlots()
      .map((slot) => slot.label)
      .filter(Boolean);
    const remainingCount = getRequiredPowerCellCount() - state.installedPowerCellSlots.size;
    if (remainingCount > 1 && openSlots.length > 1) return `Install power cells in slots ${openSlots.join(" and ")}.`;
    if (openSlots.length === 1) return `Install a power cell in slot ${openSlots[0]}.`;
    return "Install the power cell.";
  }

  const missingPart = state.missingParts.find((part) => !part.installed);
  if (missingPart) return `Place missing ${missingPart.label}.`;

  const repairTarget = state.repairTargets.find((target) => isRepairTargetActive(target) && !target.repaired);
  if (repairTarget) return `Hold repair tool tip on ${repairTarget.label} for 3 seconds.`;

  return "Press CHECK to verify the rover.";
}

function capitalize(text) {
  return text ? `${text.charAt(0).toUpperCase()}${text.slice(1)}` : "";
}

function callInRover() {
  if (!callButton.userData.enabled || state.doorMoving || state.roverArriving || state.roverTurning) return;

  setButtonEnabled(callButton, false, materials.lightOn, materials.socketIdle);
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  setCheckButtonEnabled(false);

  // Rover staging sequence.
  stageRoverForArrival();

  updateObjective("OPENING BAY DOOR");
  startDoorMotion("openingForCall");
}

function stageRoverForArrival() {
  state.currentLevelConfig = getLevelConfig(state.level);
  removePowerModule();
  clearLevelInteractionObjects();
  if (rover) {
    removeRoverStaticBodies();
    scene.remove(rover.group);
    rover = null;
  }
  addPlayerObstacle({ id: "rover", minX: -1.15, maxX: 1.15, minZ: -1.1, maxZ: 0.85 });

  rover = createRoverAsset({
    scene,
    materials,
    meshBox,
    addRoverStaticBodies,
    options: {
      roverType: state.currentLevelConfig.roverType ?? "regular",
      position: new THREE.Vector3(0, 0.55, ROVER_ENTRY_Z),
      onModelLoaded: setupLevelRoverInteractions,
    },
  });
  removeRoverStaticBodies();
  rover.group.rotation.y = -Math.PI / 2;
  rover.group.userData.arrivalTargetZ = ROVER_PARKED_Z;
  rover.group.userData.parkedRotationY = 0;
  rover.group.userData.exitRotationY = -Math.PI / 2;
  rover.group.userData.exitTargetZ = ROVER_ENTRY_Z;
  resetPowerCellInstallStateForLevel();
  state.powerSnapCheckTimer = 0;
  state.roverChecked = false;
  state.roverGoodForLevel = false;
  state.timerDuration = state.currentLevelConfig.timerDuration;
  state.timeRemaining = state.timerDuration;
  lastDrawnSecond = -1;
  spawnPowerModuleForLevel();
  state.timerActive = false;
  state.roverArriving = false;
  state.roverTurning = false;
  state.roverLeavingTurning = false;
  state.roverLeaving = false;
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  setCheckButtonEnabled(false);
  state.game = GameState.AWAITING_ROVER;
}

function startRoverCallAfterDoorOpens() {
  if (!rover) {
    stageRoverForArrival();
  }

  state.timerActive = true;
  state.roverArriving = true;
  state.roverTurning = false;
  state.roverLeavingTurning = false;
  state.roverLeaving = false;
  updateObjective(`Level ${state.level} rover arriving.`);
}

function sendRoverOut() {
  if (
    !launchButton.userData.enabled ||
    !rover ||
    state.doorMoving ||
    state.roverArriving ||
    state.roverTurning ||
    state.roverLeavingTurning ||
    state.roverLeaving
  ) {
    return;
  }

  if (!state.roverGoodForLevel) {
    updateObjective("Press CHECK first. Rover is not cleared for rollout yet.");
    return;
  }

  state.timerActive = false;
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  setCheckButtonEnabled(false);
  setButtonEnabled(callButton, false, materials.lightOn, materials.socketIdle);

  updateObjective("OPENING BAY DOOR");
  startDoorMotion("openingForSend");
}

function startRoverDepartureAfterDoorOpens() {
  if (!rover) return;

  removeRoverStaticBodies();
  state.roverLeavingTurning = true;
  state.roverLeaving = false;
  updateObjective("Rover cleared. Turning toward the exit.");
}

function spinRoverWheels(amount) {
  if (!rover?.wheels) return;

  for (const wheel of rover.wheels) {
    if (wheel.userData.spinEnabled === false || wheel.visible === false) continue;

    const axis = wheel.userData.spinAxis ?? "x";
    const direction = wheel.userData.spinDirection ?? -1;
    wheel.rotation[axis] += amount * direction;
  }
}

function updateRoverArrival(delta) {
  if (!state.roverArriving) return;

  rover.group.position.z += delta * 2.5;
  spinRoverWheels(delta * 8.5);
  markShadowsDirty();

  if (rover.group.position.z >= rover.group.userData.arrivalTargetZ) {
    rover.group.position.z = rover.group.userData.arrivalTargetZ;
    state.roverArriving = false;
    state.roverTurning = true;
    state.game = GameState.AWAITING_ROVER;
    updateObjective("Rover aligning in the repair zone.");
  }
}

function updateRoverTurn(delta) {
  if (!state.roverTurning || !rover) return;

  rover.group.rotation.y = THREE.MathUtils.damp(
    rover.group.rotation.y,
    rover.group.userData.parkedRotationY,
    4.5,
    delta,
  );
  markShadowsDirty();

  if (Math.abs(rover.group.rotation.y - rover.group.userData.parkedRotationY) > 0.015) return;

  rover.group.rotation.y = rover.group.userData.parkedRotationY;
  state.roverTurning = false;

  addRoverStaticBodies();
  state.roverChecked = false;
  state.roverGoodForLevel = false;
  updateObjective("CLOSING BAY DOOR");
  startDoorMotion("closingAfterCall");
}

function activateRepairPhase() {
  setCheckButtonEnabled(true);
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  updateObjective(getNextRepairObjective());
}

function checkRoverForLevel() {
  if (!rover) {
    updateObjective("CHECK FAILED: No rover is currently in the bay.");
    return;
  }

  if (
    state.doorMoving ||
    state.doorOpen ||
    state.roverArriving ||
    state.roverTurning ||
    state.roverLeavingTurning ||
    state.roverLeaving
  ) {
    updateObjective("CHECK WAIT: Rover is still moving.");
    return;
  }

  if (!state.roverInteractionsReady) {
    updateObjective("CHECK WAIT: Rover repair targets are still loading.");
    return;
  }

  state.roverChecked = true;
  state.roverGoodForLevel = Boolean(
    (!state.currentLevelConfig.requiresPowerCell || hasRequiredPowerCellsInstalled()) &&
    allMissingPartsInstalled() &&
    allRepairTargetsFixed(),
  );

  if (state.roverGoodForLevel) {
    clearFixedRepairHighlights();
    setButtonEnabled(launchButton, true, materials.lightOn, materials.lightOff);
    updateObjective("CHECK PASSED: Rover is fixed. Press SEND ROVER.");
    return;
  }

  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  updateObjective(`CHECK FAILED: ${getNextRepairObjective()}`);
}

function updateRoverLeavingTurn(delta) {
  if (!state.roverLeavingTurning || !rover) return;

  const targetRotation = rover.group.userData.exitRotationY ?? -Math.PI / 2;
  rover.group.rotation.y = THREE.MathUtils.damp(rover.group.rotation.y, targetRotation, 4.5, delta);
  spinRoverWheels(-delta * 2.5);
  markShadowsDirty();

  if (Math.abs(rover.group.rotation.y - targetRotation) > 0.015) return;

  rover.group.rotation.y = targetRotation;
  state.roverLeavingTurning = false;
  state.roverLeaving = true;
  updateObjective("Rover leaving the repair bay.");
}

function updateRoverLeaving(delta) {
  if (!state.roverLeaving || !rover) return;

  const exitTargetZ = rover.group.userData.exitTargetZ ?? ROVER_ENTRY_Z;
  rover.group.position.z -= delta * 1.2;
  spinRoverWheels(-delta * 8.5);
  markShadowsDirty();

  if (rover.group.position.z > exitTargetZ) return;

  rover.group.position.z = exitTargetZ;
  state.roverLeaving = false;
  updateObjective("CLOSING BAY DOOR");
  startDoorMotion("closingAfterSend");
}

function completeRoverDeparture() {
  removePlayerObstacle("rover");

  const completedLevel = state.level;
  const completionBonus = state.currentLevelConfig.completionBonus ?? 0;
  state.score += completionBonus;
  state.completedRovers += 1;
  state.level += 1;
  state.currentLevelConfig = getLevelConfig(state.level);
  clearLevelInteractionObjects();
  scene.remove(rover.group);
  rover = null;
  powerModule = null;
  powerModules = [];
  state.powerModuleInstalled = false;
  state.installedPowerCellSlots.clear();
  state.powerSnapCheckTimer = 0;
  state.roverChecked = false;
  state.roverGoodForLevel = false;

  setButtonEnabled(callButton, true, materials.lightOn, materials.socketIdle);
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);
  setCheckButtonEnabled(false);
  updateHud();
  updateObjective(
    `Level ${completedLevel} complete. +${completionBonus} bonus. Press CALL ROVER for level ${state.level}.`,
  );
}

function addPlayerObstacle(obstacle) {
  removePlayerObstacle(obstacle.id);
  playerCollider.obstacles.push(obstacle);
}

function getToolTableSpawnPosition(index) {
  const x = TOOL_TABLE_SPAWN_X[Math.floor(index / TOOL_TABLE_SPAWN_Z.length) % TOOL_TABLE_SPAWN_X.length];
  const z = TOOL_TABLE_SPAWN_Z[index % TOOL_TABLE_SPAWN_Z.length];
  return new THREE.Vector3(x, 1.45, z);
}

function updateObjective(text) {
  state.currentObjective = text;
  objective.textContent = text;
  drawInWorldHud();
  drawVrHud();
  drawMiniScreen();
  drawStatusScreen();
}

function drawInWorldHud() {
  if (!state.inWorldText) return;

  const { canvas, texture } = state.inWorldText.userData;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "rgba(17, 19, 24, 0.82)";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#f6c453";
  context.lineWidth = 6;
  context.strokeRect(6, 6, canvas.width - 12, canvas.height - 12);
  context.fillStyle = "#f6c453";
  context.font = "700 42px system-ui, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(`LEVEL ${state.level}     SCORE ${state.score}`, canvas.width / 2, 78);
  context.fillStyle = "#f4f0e6";
  context.font = "700 58px system-ui, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(state.currentObjective, canvas.width / 2, 230, canvas.width - 90);
  texture.needsUpdate = true;
}

function drawVrHud() {
  if (!state.vrHud) return;

  const { canvas, texture } = state.vrHud;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);

  const cornerRadius = 34;
  context.fillStyle = "rgba(12, 17, 22, 0.86)";
  drawRoundedRect(context, 0, 0, canvas.width, canvas.height, cornerRadius);
  context.fill();

  context.strokeStyle = "rgba(246, 196, 83, 0.82)";
  context.lineWidth = 12;
  drawRoundedRect(context, 14, 14, canvas.width - 28, canvas.height - 28, cornerRadius - 6);
  context.stroke();

  context.fillStyle = "#f6c453";
  context.font = "900 54px system-ui, sans-serif";
  context.textAlign = "left";
  context.textBaseline = "middle";
  context.fillText("ROVER READY", 58, 66);

  context.fillStyle = "#f4f0e6";
  context.font = "800 52px system-ui, sans-serif";
  context.fillText(`LEVEL ${state.level}`, 58, 156);
  context.fillText(`SCORE ${state.score}`, 360, 156);
  context.fillText(`TIME ${formatElapsedTime(state.timeRemaining)}`, 690, 156);

  context.fillStyle = "rgba(244, 240, 230, 0.16)";
  context.fillRect(58, 214, canvas.width - 116, 3);

  context.fillStyle = "#f4f0e6";
  context.font = "800 62px system-ui, sans-serif";
  context.textAlign = "left";
  wrapCanvasText(context, state.currentObjective || "Press CALL ROVER.", 58, 342, canvas.width - 116, 72);

  texture.needsUpdate = true;
}

function drawRoundedRect(context, x, y, width, height, radius) {
  context.beginPath();
  context.moveTo(x + radius, y);
  context.lineTo(x + width - radius, y);
  context.quadraticCurveTo(x + width, y, x + width, y + radius);
  context.lineTo(x + width, y + height - radius);
  context.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  context.lineTo(x + radius, y + height);
  context.quadraticCurveTo(x, y + height, x, y + height - radius);
  context.lineTo(x, y + radius);
  context.quadraticCurveTo(x, y, x + radius, y);
  context.closePath();
}

function drawMiniScreen() {
  if (!state.miniScreen) return;

  const { canvas, texture } = state.miniScreen;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#0d141a";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#56d88a";
  context.lineWidth = Math.max(8, canvas.height * 0.03);
  context.strokeRect(
    context.lineWidth,
    context.lineWidth,
    canvas.width - context.lineWidth * 2,
    canvas.height - context.lineWidth * 2,
  );
  context.fillStyle = "#f4f0e6";
  context.font = `900 ${Math.round(canvas.height * 0.2)}px system-ui, sans-serif`;
  context.textAlign = "center";
  context.textBaseline = "middle";
  wrapCanvasText(
    context,
    state.currentObjective || "Press the call button.",
    canvas.width / 2,
    canvas.height / 2,
    canvas.width - canvas.height * 0.7,
    canvas.height * 0.23,
  );
  texture.needsUpdate = true;
}

function drawStatusScreen() {
  if (!state.statusScreen) return;

  const { canvas, texture } = state.statusScreen;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#111821";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#f6c453";
  context.lineWidth = Math.max(14, canvas.height * 0.018);
  context.strokeRect(
    context.lineWidth,
    context.lineWidth,
    canvas.width - context.lineWidth * 2,
    canvas.height - context.lineWidth * 2,
  );
  context.fillStyle = "#f6c453";
  context.font = `900 ${Math.round(canvas.height * 0.075)}px system-ui, sans-serif`;
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText("MISSION STATUS", canvas.width / 2, canvas.height * 0.12);
  drawStatusRow(context, "LEVEL", String(state.level), canvas.height * 0.33, canvas);
  drawStatusRow(context, "SCORE", String(state.score), canvas.height * 0.54, canvas);
  drawStatusRow(context, "TIME", formatElapsedTime(state.timeRemaining), canvas.height * 0.75, canvas);
  texture.needsUpdate = true;
}

function drawStatusRow(context, label, value, y, canvas) {
  context.fillStyle = "#f4f0e6";
  context.font = `800 ${Math.round(canvas.height * 0.07)}px system-ui, sans-serif`;
  context.textAlign = "left";
  context.fillText(label, canvas.width * 0.13, y);
  context.fillStyle = "#56d88a";
  context.font = `900 ${Math.round(canvas.height * 0.095)}px system-ui, sans-serif`;
  context.textAlign = "right";
  context.fillText(value, canvas.width * 0.87, y);
}

function wrapCanvasText(context, text, x, centerY, maxWidth, lineHeight) {
  const words = text.split(" ");
  const lines = [];
  let line = "";

  for (const word of words) {
    const testLine = line ? `${line} ${word}` : word;
    if (context.measureText(testLine).width > maxWidth && line) {
      lines.push(line);
      line = word;
    } else {
      line = testLine;
    }
  }
  if (line) lines.push(line);

  const startY = centerY - ((lines.length - 1) * lineHeight) / 2;
  lines.forEach((lineText, index) => {
    context.fillText(lineText, x, startY + index * lineHeight);
  });
}

function updateHud() {
  if (levelValue) levelValue.textContent = String(state.level);
  if (scoreValue) scoreValue.textContent = String(state.score);
  drawInWorldHud();
  drawVrHud();
  drawMiniScreen();
  drawStatusScreen();
}

function formatElapsedTime(seconds) {
  const totalSeconds = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(totalSeconds / 60);
  const remainder = totalSeconds % 60;
  return `${minutes}:${String(remainder).padStart(2, "0")}`;
}

function setKey(code, pressed) {
  if (code === "KeyW" || code === "ArrowUp") keyboard.forward = pressed;
  if (code === "KeyS" || code === "ArrowDown") keyboard.backward = pressed;
  if (code === "KeyA") keyboard.left = pressed;
  if (code === "KeyD") keyboard.right = pressed;
  if (code === "ArrowLeft") keyboard.turnLeft = pressed;
  if (code === "ArrowRight") keyboard.turnRight = pressed;
}

function updateLocomotion(delta) {
  const move = getDesktopMoveVector();
  const xrMove = getXrMoveVector();
  move.add(xrMove);

  if (move.lengthSq() > 1) move.normalize();

  const turnInput = Number(keyboard.turnLeft) - Number(keyboard.turnRight) + getXrTurnInput();
  if (Math.abs(turnInput) > 0.12) {
    playerRig.rotation.y += turnInput * delta * 1.8;
  }

  if (move.lengthSq() === 0) return;

  const speed = renderer.xr.isPresenting ? 4 : 3.0;
  const yaw = getCameraYaw();
  const forward = new THREE.Vector3(Math.sin(yaw), 0, Math.cos(yaw));
  const right = new THREE.Vector3(-forward.z, 0, forward.x);
  const offset = new THREE.Vector3()
    .addScaledVector(forward, move.y)
    .addScaledVector(right, move.x)
    .multiplyScalar(speed * delta);

  movePlayerWithCollision(offset);
}

function movePlayerWithCollision(offset) {
  const currentHead = getHeadFloorPosition();
  const nextHeadX = currentHead.clone();
  nextHeadX.x += offset.x;
  if (isPlayerPositionAllowed(nextHeadX)) {
    playerRig.position.x += offset.x;
  }

  const headAfterX = getHeadFloorPosition();
  const nextHeadZ = headAfterX.clone();
  nextHeadZ.z += offset.z;
  if (isPlayerPositionAllowed(nextHeadZ)) {
    playerRig.position.z += offset.z;
  }

  enforceHeadCollision();
}

function enforceHeadCollision() {
  const headPosition = getHeadFloorPosition();
  if (isPlayerPositionAllowed(headPosition)) {
    lastAllowedHeadPosition.copy(headPosition);
    return;
  }

  const corrected = resolveNearestAllowedHeadPosition(headPosition);
  playerRig.position.x += corrected.x - headPosition.x;
  playerRig.position.z += corrected.z - headPosition.z;
  lastAllowedHeadPosition.copy(corrected);
}

function resolveNearestAllowedHeadPosition(position) {
  const radius = playerCollider.radius;
  const room = playerCollider.room;
  const corrected = position.clone();
  corrected.x = THREE.MathUtils.clamp(corrected.x, room.minX + radius, room.maxX - radius);
  corrected.z = THREE.MathUtils.clamp(corrected.z, room.minZ + radius, room.maxZ - radius);

  if (isPlayerPositionAllowed(corrected)) return corrected;
  if (isPlayerPositionAllowed(lastAllowedHeadPosition)) return lastAllowedHeadPosition.clone();
  return new THREE.Vector3(0, 0, 2.15);
}

function getHeadFloorPosition() {
  const headPosition = new THREE.Vector3();
  camera.getWorldPosition(headPosition);
  headPosition.y = 0;
  return headPosition;
}

function isPlayerPositionAllowed(position) {
  const radius = playerCollider.radius;
  const room = playerCollider.room;
  if (
    position.x - radius < room.minX ||
    position.x + radius > room.maxX ||
    position.z - radius < room.minZ ||
    position.z + radius > room.maxZ
  ) {
    return false;
  }

  return !playerCollider.obstacles.some((box) => circleOverlapsBox(position.x, position.z, radius, box));
}

function circleOverlapsBox(x, z, radius, box) {
  const nearestX = THREE.MathUtils.clamp(x, box.minX, box.maxX);
  const nearestZ = THREE.MathUtils.clamp(z, box.minZ, box.maxZ);
  const dx = x - nearestX;
  const dz = z - nearestZ;
  return dx * dx + dz * dz < radius * radius;
}

function getDesktopMoveVector() {
  const x = Number(keyboard.right) - Number(keyboard.left);
  const y = Number(keyboard.forward) - Number(keyboard.backward);
  return new THREE.Vector2(x, y);
}

function getXrMoveVector() {
  for (const source of renderer.xr.getSession()?.inputSources ?? []) {
    const axes = source.gamepad?.axes;
    if (!axes || axes.length < 4) continue;

    const x = applyDeadZone(axes[2] ?? axes[0]);
    const y = -applyDeadZone(axes[3] ?? axes[1]);
    if (Math.abs(x) > 0 || Math.abs(y) > 0) {
      return new THREE.Vector2(x, y);
    }
  }
  return new THREE.Vector2();
}

function getXrTurnInput() {
  for (const source of renderer.xr.getSession()?.inputSources ?? []) {
    const axes = source.gamepad?.axes;
    if (!axes || axes.length < 2) continue;
    const x = applyDeadZone(axes[0]);
    if (Math.abs(x) > 0) return -x;
  }
  return 0;
}

function getCameraYaw() {
  const direction = new THREE.Vector3();
  camera.getWorldDirection(direction);
  return Math.atan2(direction.x, direction.z);
}

function applyDeadZone(value) {
  if (Math.abs(value) < 0.18) return 0;
  return value;
}

function keepGrabbablesOnRackSurfaces() {
  const heldObjects = new Set(state.held.values());

  for (const object of state.grabbables) {
    if (object.userData.locked || heldObjects.has(object) || mouseHeld === object) continue;

    const body = physics.bodies.get(object);
    if (!body || body.type !== CANNON.Body.DYNAMIC) continue;

    const halfHeight = (object.userData.physicsSize?.[1] ?? 0.4) / 2;
    const surface = findRackSurfaceUnderBody(body.position.x, body.position.z, body.position.y, halfHeight);
    if (!surface) continue;

    settleBodyOnRackSurface(object, body, surface, halfHeight);
  }
}

function settleBodyOnRackSurface(object, body, surface, halfHeight) {
  const restingY = surface.y + halfHeight + 0.012;
  body.position.y = restingY;

  if (body.velocity.y < 0) body.velocity.y = 0;
  body.velocity.x *= 0.35;
  body.velocity.z *= 0.35;
  body.angularVelocity.scale(0.3, body.angularVelocity);

  object.position.copy(body.position);
  object.quaternion.copy(body.quaternion);

  if (body.velocity.lengthSquared() < 0.025 && body.angularVelocity.lengthSquared() < 0.025) {
    body.velocity.setZero();
    body.angularVelocity.setZero();
    body.sleep();
  }
}

function findRackSurfaceUnderBody(x, z, bodyY, halfHeight) {
  for (const surface of rackSurfaces) {
    if (x < surface.minX || x > surface.maxX || z < surface.minZ || z > surface.maxZ) continue;

    const bottomY = bodyY - halfHeight;
    const closeToSurface = bottomY <= surface.y + 0.18 && bodyY > surface.y - 0.45;
    if (closeToSurface) return surface;
  }
  return null;
}

function getPowerModuleFromCreateResult(result) {
  if (!result) return null;
  if (result.isObject3D) return result;
  if (result.group?.isObject3D) return result.group;
  if (result.mesh?.isObject3D) return result.mesh;
  if (result.object?.isObject3D) return result.object;
  return null;
}

function getPowerModule() {
  const modules = getPowerModules();
  powerModule = modules[0] ?? null;
  return powerModule ?? null;
}

function getPowerModules() {
  const modules = [];
  const addModule = (object) => {
    if (!object?.parent || modules.includes(object)) return;
    if (object.userData.type === ObjectType.POWER_MODULE) modules.push(object);
  };

  for (const module of powerModules) addModule(module);
  addModule(powerModule);
  for (const object of state.grabbables) addModule(object);

  powerModules = modules;
  return modules;
}

function findFirstObjectByName(root, names) {
  if (!root) return null;
  for (const name of names) {
    const found = root.getObjectByName(name);
    if (found) return found;
  }
  return null;
}

function getPowerCellSlotIds() {
  if (!state.currentLevelConfig.requiresPowerCell) return [];
  const slotIds = state.currentLevelConfig.powerCellSlots;
  return slotIds?.length ? slotIds : ["main"];
}

function getRequiredPowerCellCount() {
  if (!state.currentLevelConfig.requiresPowerCell) return 0;
  return Math.max(1, state.currentLevelConfig.requiredPowerCellCount ?? 1);
}

function hasRequiredPowerCellsInstalled() {
  return state.installedPowerCellSlots.size >= getRequiredPowerCellCount();
}

function getPowerCellSlotDefinition(slotId) {
  if (slotId === "A") {
    return {
      id: "A",
      label: "A",
      snapTargetName: "RR_Rover_PowerCellA_SnapTarget",
      seatNames: ["RR_Rover_PowerCellDock_A_Battery_Seat", "RR_Rover_PowerCellDock_A_Rectangular_Recess"],
    };
  }

  if (slotId === "B") {
    return {
      id: "B",
      label: "B",
      snapTargetName: "RR_Rover_PowerCellB_SnapTarget",
      seatNames: ["RR_Rover_PowerCellDock_B_Battery_Seat", "RR_Rover_PowerCellDock_B_Rectangular_Recess"],
    };
  }

  return {
    id: "main",
    label: "",
    snapTargetName: "RR_Rover_PowerCell_SnapTarget",
    seatNames: [
      "RR_Rover_PowerCellDock_Battery_Seat",
      "RR_Rover_PowerCellDock_Rectangular_Recess",
      "PowerCellDock_Battery_Seat",
      "PowerDockSeat",
    ],
  };
}

function getPowerCellSlots() {
  return getPowerCellSlotIds().map((slotId) => getPowerCellSlotDefinition(slotId));
}

function getOpenPowerCellSlots() {
  return getPowerCellSlots().filter((slot) => !state.installedPowerCellSlots.has(slot.id));
}

function getPowerSnapWorldPosition(slot = getPowerCellSlotDefinition("main")) {
  if (!rover?.group) return null;
  const snapTarget = rover.group.getObjectByName(slot.snapTargetName);
  if (snapTarget) return snapTarget.getWorldPosition(new THREE.Vector3());

  return rover.group.localToWorld(state.powerSnapLocalPosition.clone());
}

function getPowerInstalledWorldQuaternion() {
  if (!rover?.group) return null;

  const roverWorldQuaternion = rover.group.getWorldQuaternion(new THREE.Quaternion());
  const localInstallQuaternion = new THREE.Quaternion().setFromEuler(state.powerSnapLocalRotation);
  return roverWorldQuaternion.multiply(localInstallQuaternion);
}

function getPowerInsertWorldPosition(module) {
  const insertPoint = module.getObjectByName("RR_PowerCell_InsertPoint");
  if (insertPoint) return insertPoint.getWorldPosition(new THREE.Vector3());

  return module.localToWorld(state.powerInsertLocalPosition.clone());
}

function getPowerBodyObject(module) {
  return findFirstObjectByName(module, [
    "RR_PowerCell_Beveled_Rectangular_Battery_Body",
    "RR_PowerModule_Body",
    "RR_PowerCell_Body",
    "PowerModule_Body",
    "PowerCell_Body",
    "PowerModuleBody",
    "PowerCellBody",
  ]);
}

function getPowerDockSeatObject(slot = getPowerCellSlotDefinition("main")) {
  return findFirstObjectByName(rover?.group, slot.seatNames);
}

function getPowerBodyLocalCenter(module) {
  const bodyObject = getPowerBodyObject(module);
  if (!bodyObject) return state.powerCellBodyLocalPosition.clone();

  module.updateMatrixWorld(true);
  bodyObject.updateMatrixWorld(true);

  const bodyBox = new THREE.Box3().setFromObject(bodyObject);
  const bodyWorldCenter = bodyBox.getCenter(new THREE.Vector3());
  return module.worldToLocal(bodyWorldCenter);
}

function getPowerBodyWorldCenter(module) {
  const bodyObject = getPowerBodyObject(module);
  if (bodyObject) {
    module.updateMatrixWorld(true);
    bodyObject.updateMatrixWorld(true);
    return new THREE.Box3().setFromObject(bodyObject).getCenter(new THREE.Vector3());
  }

  return module.localToWorld(state.powerCellBodyLocalPosition.clone());
}

function getPowerDockBodyCenterWorldPosition(module, slot = getPowerCellSlotDefinition("main")) {
  if (!rover?.group) return null;

  const seatObject = getPowerDockSeatObject(slot);
  if (seatObject) {
    seatObject.updateMatrixWorld(true);
    const seatBox = new THREE.Box3().setFromObject(seatObject);
    const seatCenter = seatBox.getCenter(new THREE.Vector3());

    // Power-cell seated body center.
    seatCenter.y = seatBox.max.y + state.powerCellBodyHalfHeight + state.powerDockSeatTopClearance;
    return seatCenter;
  }

  const installedRootWorld =
    slot.id === "main"
      ? rover.group.localToWorld(state.powerInstallLocalPosition.clone())
      : getPowerSnapWorldPosition(slot);
  if (!installedRootWorld) return null;
  const installedQuaternion = getPowerInstalledWorldQuaternion();
  const bodyOffset = getPowerBodyLocalCenter(module).applyQuaternion(installedQuaternion);
  return installedRootWorld.clone().add(bodyOffset);
}

function isPowerModuleObject(object) {
  if (!object) return false;
  return getPowerModules().some(
    (module) => object === module || module.children.includes(object) || object.parent === module,
  );
}

function getHeldPowerModule() {
  const modules = getPowerModules().filter((module) => module && !module.userData.locked);
  if (modules.length === 0) return null;

  if (modules.includes(mouseHeld)) return mouseHeld;

  for (const heldObject of state.held.values()) {
    if (modules.includes(heldObject)) return heldObject;
  }

  return null;
}

function isPowerModuleCurrentlyHeld() {
  return Boolean(getHeldPowerModule()) && getOpenPowerCellSlots().length > 0;
}

function updatePowerModuleSnapThrottled(delta) {
  if (!isPowerModuleCurrentlyHeld()) {
    state.powerSnapCheckTimer = 0;
    return;
  }

  state.powerSnapCheckTimer -= delta;
  if (state.powerSnapCheckTimer > 0) return;

  state.powerSnapCheckTimer = state.powerSnapCheckInterval;
  updatePowerModuleSnap();
}

function updatePowerModuleSnap() {
  if (!rover || !state.roverInteractionsReady || state.roverArriving || state.roverTurning) return;

  const module = getHeldPowerModule();
  if (!module) return;

  const slotHit = getNearestOpenPowerCellSlot(module);
  if (!slotHit) return;

  snapPowerModuleToRover(module, slotHit.slot);
}

function getNearestOpenPowerCellSlot(module) {
  const moduleBodyCenter = getPowerBodyWorldCenter(module);
  if (!moduleBodyCenter) return null;

  let bestHit = null;
  for (const slot of getOpenPowerCellSlots()) {
    const dockBodyCenter = getPowerDockBodyCenterWorldPosition(module, slot);
    const snapWorld = getPowerSnapWorldPosition(slot);
    if (!dockBodyCenter || !snapWorld) continue;

    const bodyDistance = moduleBodyCenter.distanceTo(dockBodyCenter);
    const insertDistance = getPowerInsertWorldPosition(module).distanceTo(snapWorld);
    const distance = Math.min(bodyDistance, insertDistance);
    if (!bestHit || distance < bestHit.distance) bestHit = { slot, distance };
  }

  return bestHit?.distance <= state.powerSnapDistance ? bestHit : null;
}

function clonePowerBlueMaterial(material) {
  if (!material?.clone) return material;

  const blueMaterial = material.clone();
  const readyBlue = new THREE.Color(0x31a8ff);

  if (blueMaterial.color) blueMaterial.color.copy(readyBlue);
  if (blueMaterial.emissive) {
    blueMaterial.emissive.copy(readyBlue);
    blueMaterial.emissiveIntensity = Math.max(blueMaterial.emissiveIntensity ?? 1, 3.5);
  }

  blueMaterial.needsUpdate = true;
  return blueMaterial;
}

function getMaterialColorScore(material) {
  if (!material) return new THREE.Color(0x000000);

  if (material.emissive && material.emissive.getHex() !== 0x000000) {
    return material.emissive;
  }

  return material.color ?? new THREE.Color(0x000000);
}

function materialLooksBlue(material) {
  const color = getMaterialColorScore(material);
  return color.b > 0.45 && color.b > color.r * 1.35 && color.b > color.g * 0.85;
}

function meshLooksBlue(mesh) {
  const meshMaterials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  return meshMaterials.some((material) => materialLooksBlue(material));
}

const POWER_READY_CONTACT_NAMES = new Set([
  // Rover dock contact indicators.
  "RR_Rover_PowerCellDock_Positive_Cyan_Contact",
  "RR_Rover_PowerCellDock_Negative_Steel_Contact",

  // Power-cell contact indicators.
  "RR_PowerCell_Front_Contact_Pad_Positive",
  "RR_PowerCell_Front_Contact_Pad_Negative",
]);

function isPowerIndicatorMesh(mesh) {
  if (!mesh?.isMesh) return false;

  const lowerName = mesh.name.toLowerCase();

  // Power indicator name matching.
  if (POWER_READY_CONTACT_NAMES.has(mesh.name)) return true;
  if (lowerName.includes("powercelldock") && lowerName.includes("contact")) return true;
  if (lowerName.includes("powercell_front_contact_pad")) return true;

  // Generic indicator name matching.
  const indicatorTerms = ["button", "indicator", "light", "led", "lamp", "lens", "glow"];
  const blockedTerms = ["wheel", "tire", "tread", "body", "chassis", "seat", "recess", "snap"];

  return (
    indicatorTerms.some((term) => lowerName.includes(term)) && !blockedTerms.some((term) => lowerName.includes(term))
  );
}

function getMeshWorldCenter(mesh) {
  mesh.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(mesh);
  if (box.isEmpty()) return mesh.getWorldPosition(new THREE.Vector3());
  return box.getCenter(new THREE.Vector3());
}

function setMeshIndicatorBlue(mesh) {
  if (!mesh?.isMesh || mesh.userData.powerReadyBlue) return;
  if (meshLooksBlue(mesh)) return;

  mesh.material = Array.isArray(mesh.material)
    ? mesh.material.map((material) => clonePowerBlueMaterial(material))
    : clonePowerBlueMaterial(mesh.material);

  mesh.userData.powerReadyBlue = true;
}

function findPowerDockIndicatorCenter(module, slot) {
  const seatObject = getPowerDockSeatObject(slot);
  if (seatObject?.isObject3D) return getMeshWorldCenter(seatObject);

  const snapWorld = getPowerSnapWorldPosition(slot);
  if (snapWorld) return snapWorld;

  return module?.getWorldPosition(new THREE.Vector3()) ?? null;
}

function setPowerCellReadyIndicatorsBlue(module, slot) {
  const dockCenter = findPowerDockIndicatorCenter(module, slot);

  // Inserted power-cell indicators.
  module?.traverse?.((child) => {
    if (!isPowerIndicatorMesh(child)) return;
    setMeshIndicatorBlue(child);
  });

  // Rover dock indicators.
  rover?.group?.traverse?.((child) => {
    if (!isPowerIndicatorMesh(child)) return;

    if (dockCenter) {
      const distanceToDock = getMeshWorldCenter(child).distanceTo(dockCenter);
      if (distanceToDock > 1.25) return;
    }

    setMeshIndicatorBlue(child);
  });
}

function snapPowerModuleToRover(module, slot = getPowerCellSlotDefinition("main"), options = {}) {
  const { awardScore = true, updateObjectiveText = true, enableCheckButton = true } = options;
  const moduleWorldQuaternion = getPowerInstalledWorldQuaternion();
  const bodyTargetWorldPosition = getPowerDockBodyCenterWorldPosition(module, slot);
  if (!moduleWorldQuaternion || !bodyTargetWorldPosition) return;
  state.installedPowerCellSlots.add(slot.id);
  state.powerModuleInstalled = hasRequiredPowerCellsInstalled();
  state.powerSnapCheckTimer = 0;

  for (const [controller, heldObject] of state.held) {
    if (heldObject === module) state.held.delete(controller);
  }

  if (mouseHeld === module) mouseHeld = null;

  const body = physics.bodies.get(module);
  if (body) {
    physics.world.removeBody(body);
    physics.bodies.delete(module);
  }

  module.userData.locked = true;
  module.userData.grabbable = false;
  module.userData.powerCellSlotId = slot.id;
  state.grabbables = state.grabbables.filter((object) => object !== module);

  scene.attach(module);

  const bodyLocalCenter = getPowerBodyLocalCenter(module);
  const bodyOffset = bodyLocalCenter.clone().applyQuaternion(moduleWorldQuaternion);

  module.quaternion.copy(moduleWorldQuaternion);
  module.position.copy(bodyTargetWorldPosition.clone().sub(bodyOffset));
  module.updateMatrixWorld(true);

  rover.group.attach(module);

  module.traverse?.((child) => {
    child.castShadow = true;
    child.receiveShadow = true;
  });

  setPowerCellReadyIndicatorsBlue(module, slot);

  markShadowsDirty();
  if (awardScore) state.score += 100;
  state.roverChecked = false;
  state.roverGoodForLevel = false;
  updateHud();

  if (enableCheckButton) setCheckButtonEnabled(true);
  setButtonEnabled(launchButton, false, materials.lightOn, materials.lightOff);

  const slotLabel = slot.label ? ` in slot ${slot.label}` : "";
  if (updateObjectiveText) updateObjective(`Power cell installed${slotLabel}. ${getNextRepairObjective()}`);
}

function render() {
  const delta = Math.min(clock.getDelta(), 0.033);
  if (state.timerActive) {
    state.timeRemaining = Math.max(0, state.timeRemaining - delta);
    const currentSecond = Math.ceil(state.timeRemaining);
    if (currentSecond !== lastDrawnSecond) {
      lastDrawnSecond = currentSecond;
      drawVrHud();
      drawStatusScreen();
    }

    if (state.timeRemaining <= 0) {
      state.timerActive = false;
      updateObjective("Timer expired.");
    }
  }
  updateLocomotion(delta);
  enforceHeadCollision();

  for (const object of state.held.values()) {
    const body = physics.bodies.get(object);
    if (body) {
      body.position.copy(toCannonVec(object.getWorldPosition(new THREE.Vector3())));
      body.quaternion.copy(toCannonQuat(object.getWorldQuaternion(new THREE.Quaternion())));
    }
  }

  updateRoverArrival(delta);
  updateRoverTurn(delta);
  updateRoverLeavingTurn(delta);
  updateRoverLeaving(delta);
  updateDoorMotion(delta);
  updatePowerModuleSnapThrottled(delta);
  updateMissingPartSnapThrottled(delta);
  updateRepairInteractions(delta);
  physics.world.step(1 / 60, delta, 6);
  keepGrabbablesOnRackSurfaces();

  const heldObjects = new Set(state.held.values());
  for (const [object, body] of physics.bodies) {
    if (object.parent !== scene || object.userData.locked || heldObjects.has(object)) continue;
    object.position.copy(body.position);
    object.quaternion.copy(body.quaternion);
  }

  if (state.vrHud?.panel) {
    state.vrHud.panel.visible = renderer.xr.isPresenting;
  }

  renderer.render(scene, camera);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function toCannonVec(vector) {
  return new CANNON.Vec3(vector.x, vector.y, vector.z);
}

function toCannonQuat(quaternion) {
  return new CANNON.Quaternion(quaternion.x, quaternion.y, quaternion.z, quaternion.w);
}
