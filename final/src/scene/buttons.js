import * as THREE from "three";
import { ObjectType } from "../core/types.js";

export function createControlButtons({ scene, materials, meshBox, addStaticBodyForMesh, buttonTargets }) {
  const launchButton = createButtonProxy({
    scene,
    materials,
    meshBox,
    addStaticBodyForMesh,
    buttonTargets,
    name: "launchButton",
    action: "launch",
    position: [6.46, 1.2, -1.3],
    buttonMaterial: materials.lightOff,
  });
  const callButton = createButtonProxy({
    scene,
    materials,
    meshBox,
    addStaticBodyForMesh,
    buttonTargets,
    name: "callRoverButton",
    action: "call",
    position: [6.46, 2.2, 0.3],
    buttonMaterial: materials.socketIdle,
  });
  const checkButton = createButtonProxy({
    scene,
    materials,
    meshBox,
    addStaticBodyForMesh,
    buttonTargets,
    name: "checkRoverButton",
    action: "check",
    position: [6.46, 2.05, -1.45],
    buttonMaterial: materials.socketIdle,
  });

  return { launchButton, callButton, checkButton };
}

export function bindBayButtonMeshes({ bayRoot, controls, buttonTargets }) {
  const sendMesh = bayRoot.getObjectByName("Btn_SendRover");
  const callMesh = bayRoot.getObjectByName("Btn_CallRover");
  const checkMesh = bayRoot.getObjectByName("Btn_CheckRover");

  buttonTargets.length = 0;
  bindButtonMesh(sendMesh, controls.launchButton, "launch", buttonTargets);
  bindButtonMesh(callMesh, controls.callButton, "call", buttonTargets);
  bindButtonMesh(checkMesh, controls.checkButton, "check", buttonTargets);
}

function createButtonProxy({
  scene,
  materials,
  meshBox,
  addStaticBodyForMesh,
  buttonTargets,
  name,
  action,
  position,
  buttonMaterial,
}) {
  const group = new THREE.Group();
  group.name = name;
  group.position.fromArray(position);
  group.visible = false;
  group.userData = { type: ObjectType.LAUNCH_BUTTON, action, enabled: false };
  scene.add(group);

  const panel = meshBox([0.12, 0.48, 0.72], materials.roverDark);
  panel.castShadow = true;
  group.add(panel);

  const button = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.26, 0.26), buttonMaterial);
  button.name = `${name}ProxyFace`;
  button.position.x = -0.08;
  button.userData = { type: ObjectType.LAUNCH_BUTTON, action, parentButton: group };
  group.add(button);

  group.userData.button = button;
  buttonTargets.push(button);
  addStaticBodyForMesh(panel, [0.12, 0.48, 0.72]);
  return group;
}

function bindButtonMesh(mesh, buttonGroup, action, buttonTargets) {
  if (!mesh) return;

  mesh.userData = {
    ...mesh.userData,
    type: ObjectType.LAUNCH_BUTTON,
    action,
    parentButton: buttonGroup,
  };
  buttonGroup.userData.button = mesh;
  buttonTargets.push(mesh);
}
