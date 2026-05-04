import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { ObjectType } from "../core/types.js";

const POWER_CELL_GLB_URL = "./src/assets/models/power_cell.glb";
const REPAIR_TOOL_GLB_URL = "./src/assets/models/repair_tool.glb";

export function createPowerModule({
  scene,
  materials,
  meshBox,
  addPhysicsBox,
  grabbables,
  name = "powerModule",
  position = [-5.35, 1.45, -3.3],
}) {
  const group = createRackPart({
    scene,
    materials,
    meshBox,
    addPhysicsBox,
    grabbables,
    url: POWER_CELL_GLB_URL,
    modelName: "powerCellModel",
    name,
    type: ObjectType.POWER_MODULE,
    position,
    physicsSize: [0.72, 0.58, 0.94],
    targetSize: 0.72,
    mass: 2,
  });
  return group;
}

export function createRepairTool({ scene, materials, meshBox, addPhysicsBox, grabbables }) {
  const group = createRackPart({
    scene,
    materials,
    meshBox,
    addPhysicsBox,
    grabbables,
    url: REPAIR_TOOL_GLB_URL,
    modelName: "repairToolModel",
    name: "repairTool",
    type: ObjectType.REPAIR_TOOL,
    position: [-6.05, 2.02, -2.75],
    rotation: [0, Math.PI / 2, 0],
    physicsSize: [0.82, 0.62, 1.32],
    targetSize: 0.76,
    mass: 1.4,
  });
  return group;
}

function createRackPart({
  scene,
  materials,
  meshBox,
  addPhysicsBox,
  grabbables,
  url,
  modelName,
  name,
  type,
  position,
  rotation = [0, 0, 0],
  physicsSize,
  targetSize,
  mass,
}) {
  const group = new THREE.Group();
  group.name = name;
  group.position.fromArray(position);
  group.rotation.set(rotation[0], rotation[1], rotation[2]);
  group.userData = { type, grabbable: true, locked: false, physicsSize };
  scene.add(group);

  const hitBox = meshBox(physicsSize, materials.roverDark);
  hitBox.name = `${name}FullBox`;
  hitBox.visible = false;
  group.add(hitBox);

  loadGlbIntoGroup(url, group, { name: modelName, targetSize });
  addPhysicsBox(group, physicsSize, mass);
  grabbables.push(group);
  return group;
}

function loadGlbIntoGroup(url, group, { name, targetSize }) {
  const loader = new GLTFLoader();
  loader.load(
    url,
    (gltf) => {
      const model = gltf.scene;
      model.name = name;
      model.traverse((child) => {
        if (!child.isMesh) return;
        child.castShadow = true;
        child.receiveShadow = true;
      });
      fitModel(model, targetSize);
      group.add(model);
    },
    undefined,
    (error) => {
      console.warn(`Unable to load ${url}:`, error);
    },
  );
}

function fitModel(model, targetSize) {
  let box = new THREE.Box3().setFromObject(model);
  const size = new THREE.Vector3();
  box.getSize(size);
  const largestDimension = Math.max(size.x, size.y, size.z) || 1;
  model.scale.setScalar(targetSize / largestDimension);

  box = new THREE.Box3().setFromObject(model);
  const center = new THREE.Vector3();
  box.getCenter(center);
  model.position.sub(center);
}
