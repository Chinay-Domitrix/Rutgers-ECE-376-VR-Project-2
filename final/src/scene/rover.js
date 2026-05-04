import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const ROVER_GLB_URLS = {
  regular: "./src/assets/models/rover.glb",
  complex: "./src/assets/models/rover_complex.glb",
};
const ROVER_TARGET_FOOTPRINTS = {
  regular: 2.9,
  complex: 3.35,
};

export function createRover({ scene, materials, meshBox, addRoverStaticBodies, options = {} }) {
  const group = new THREE.Group();
  group.name = "rover";
  group.userData.roverType = options.roverType ?? "regular";
  group.position.copy(options.position ?? new THREE.Vector3(0, 0.55, -0.8));
  scene.add(group);
  const staticRoverMeshes = [];
  const wheels = [];
  group.userData.staticMeshes = staticRoverMeshes;

  const roverType = group.userData.roverType;
  const bodySize = roverType === "complex" ? [2.35, 0.62, 1.35] : [1.8, 0.56, 1.2];
  const body = meshBox(bodySize, materials.rover);
  body.userData.physicsSize = bodySize;
  body.visible = false;
  body.castShadow = true;
  body.receiveShadow = true;
  group.add(body);
  staticRoverMeshes.push(body);

  const cabinSize = roverType === "complex" ? [1.08, 0.52, 0.82] : [0.82, 0.46, 0.72];
  const cabin = meshBox(cabinSize, materials.roverDark);
  cabin.userData.physicsSize = cabinSize;
  cabin.visible = false;
  cabin.position.set(roverType === "complex" ? 0.28 : 0.18, 0.48, -0.08);
  cabin.castShadow = true;
  group.add(cabin);
  staticRoverMeshes.push(cabin);

  for (const x of [-1.05, 1.05]) {
    for (const z of [-0.48, 0.48]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.22, 16), materials.roverDark);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, -0.28, z);
      wheel.userData.physicsSize = [0.28, 0.5, 0.5];
      wheel.userData.spinAxis = "x";
      wheel.userData.spinDirection = -1;
      wheel.userData.spinEnabled = true;
      wheel.visible = false;
      wheel.castShadow = true;
      group.add(wheel);
      wheels.push(wheel);
      staticRoverMeshes.push(wheel);
    }
  }

  loadExternalRoverModel(group, wheels, options);

  group.updateMatrixWorld(true);
  addRoverStaticBodies(group);

  return { group, wheels };
}

function loadExternalRoverModel(group, wheels, options) {
  const loader = new GLTFLoader();
  const roverType = options.roverType ?? "regular";
  const modelUrl = options.modelUrl ?? ROVER_GLB_URLS[roverType] ?? ROVER_GLB_URLS.regular;
  loader.load(
    modelUrl,
    (gltf) => {
      const model = gltf.scene;
      model.name = "externalRoverModel";
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = false;
        }
      });

      fitModelToRover(model, roverType);
      createVisibleWheelPivots(model, wheels);
      group.add(model);
      options.onModelLoaded?.(model, group);
    },
    undefined,
    (error) => {
      console.warn(`Unable to load rover GLB ${modelUrl}:`, error);
    },
  );
}

function createVisibleWheelPivots(model, wheels) {
  const wheelParts = new Map();
  const wheelNamePattern = /RR_Rover_(Left|Right)_Wheel_(\d+)_/;

  model.updateMatrixWorld(true);
  model.traverse((child) => {
    if (!child.isMesh) return;
    const match = child.name.match(wheelNamePattern);
    if (!match) return;

    const side = match[1].toLowerCase();
    const index = match[2];
    const key = `${side}Wheel${index}`;
    if (!wheelParts.has(key)) wheelParts.set(key, []);
    wheelParts.get(key).push(child);
  });

  for (const [key, parts] of wheelParts) {
    if (parts.length === 0) continue;

    const worldBox = new THREE.Box3();
    for (const part of parts) worldBox.expandByObject(part);

    const worldCenter = worldBox.getCenter(new THREE.Vector3());
    const localCenter = model.worldToLocal(worldCenter.clone());
    const pivot = new THREE.Group();
    pivot.name = `RR_Rover_${key}_SpinPivot`;
    pivot.position.copy(localCenter);
    pivot.userData.spinAxis = "z";
    pivot.userData.spinDirection = -1;
    pivot.userData.wheelId = key;
    pivot.userData.spinEnabled = true;

    model.add(pivot);
    model.updateMatrixWorld(true);
    pivot.updateMatrixWorld(true);

    for (const part of parts) {
      part.updateMatrixWorld(true);
      pivot.attach(part);
    }

    wheels.push(pivot);
  }
}

function fitModelToRover(model, roverType) {
  let box = new THREE.Box3().setFromObject(model);
  const size = new THREE.Vector3();
  box.getSize(size);
  const largestFootprint = Math.max(size.x, size.z) || 1;
  const targetFootprint = ROVER_TARGET_FOOTPRINTS[roverType] ?? ROVER_TARGET_FOOTPRINTS.regular;
  const scale = targetFootprint / largestFootprint;
  model.scale.setScalar(scale);

  box = new THREE.Box3().setFromObject(model);
  const center = new THREE.Vector3();
  box.getCenter(center);
  model.position.sub(center);

  box = new THREE.Box3().setFromObject(model);
  model.position.y -= box.min.y + 0.28;
}
