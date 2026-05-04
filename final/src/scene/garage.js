import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const BAY_GLB_URL = "./src/assets/models/Rover_Bay.glb";

export function createLighting(scene) {
  const ambient = new THREE.HemisphereLight(0xd6e8ff, 0x2f2419, 1.1);
  scene.add(ambient);

  const main = new THREE.DirectionalLight(0xffffff, 1.85);
  main.position.set(3, 6, 4);
  main.castShadow = true;
  main.shadow.mapSize.set(1024, 1024);
  main.shadow.camera.near = 0.5;
  main.shadow.camera.far = 20;
  main.shadow.camera.left = -8;
  main.shadow.camera.right = 8;
  main.shadow.camera.top = 6;
  main.shadow.camera.bottom = -6;
  main.shadow.autoUpdate = false;
  main.shadow.needsUpdate = true;
  scene.add(main);

  const bayLight = new THREE.PointLight(0xf6c453, 1.2, 12);
  bayLight.position.set(0, 3.3, -1.4);
  bayLight.name = "bayStatusLight";
  scene.add(bayLight);

  return { main, bayLight };
}

export function createGarage({ scene, addBox, materials, onBayLoaded }) {
  createBayCollision({ addBox, materials });

  const loader = new GLTFLoader();
  loader.load(
    BAY_GLB_URL,
    (gltf) => {
      const bay = gltf.scene;
      bay.name = "roverBayGLB";
      bay.position.set(0, 0, 0);
      bay.scale.setScalar(1);
      prepareBayMeshes(bay);
      scene.add(bay);
      onBayLoaded?.(bay);
    },
    undefined,
    (error) => {
      console.warn(`Unable to load ${BAY_GLB_URL}. Keeping invisible collision fallback only.`, error);
    },
  );
}

function prepareBayMeshes(root) {
  root.traverse((child) => {
    if (!child.isMesh) return;

    // Room shell shadow settings.
    const isRoomShell = child.name.includes("Ceiling") || child.name.includes("Wall") || child.name.includes("Roof");

    child.castShadow = !isRoomShell;
    child.receiveShadow = false;

    if (Array.isArray(child.material)) {
      child.material = child.material.map((material) => material.clone());
    } else if (child.material) {
      child.material = child.material.clone();
    }
  });
}

function createBayCollision({ addBox, materials }) {
  // Floor collision.
  addBox("bayCollisionFloor", [14, 0.12, 11], [0, -0.06, 0], materials.floor, true, false);

  // Ceiling collision.
  addBox("bayCollisionCeiling", [14, 0.2, 11], [0, 3.7, 0], materials.wall, true, false);

  // Wall collision.
  addBox("bayCollisionBackWall", [14, 3.6, 0.16], [0, 1.8, 5.35], materials.wall, true, false);
  addBox("bayCollisionLeftWall", [0.16, 3.6, 11], [-7, 1.8, 0], materials.wall, true, false);
  addBox("bayCollisionRightWall", [0.16, 3.6, 11], [7, 1.8, 0], materials.wall, true, false);

  // Front bay opening collision.
  addBox("bayCollisionFrontLeft", [3.9, 3.6, 0.16], [-5.05, 1.8, -5.35], materials.wall, true, false);
  addBox("bayCollisionFrontRight", [3.9, 3.6, 0.16], [5.05, 1.8, -5.35], materials.wall, true, false);
  addBox("bayCollisionFrontHeader", [6.2, 0.4, 0.16], [0, 3.4, -5.35], materials.wall, true, false);

  // Work table collision.
  addBox("bayCollisionTableTop", [1.55, 0.24, 7.25], [-5.8, 1.04, 0], materials.roverDark, true, false);
  addBox("bayCollisionTableShelf", [1.45, 0.22, 7.05], [-5.8, 0.39, 0], materials.roverDark, true, false);
  addBox("bayCollisionTableBackRail", [0.18, 0.28, 8.05], [-6.35, 2.0, 0], materials.roverDark, true, false);

  // Table leg collision.
  const legHalfZ = 3.3;
  for (const [lx, lz] of [
    [-5.1, -legHalfZ],
    [-5.1, legHalfZ],
    [-6.4, -legHalfZ],
    [-6.4, legHalfZ],
  ]) {
    addBox(
      `bayCollisionTableLeg_${lx > 0 ? "R" : "L"}${lz > 0 ? "B" : "F"}`,
      [0.14, 0.28, 0.14],
      [lx, 0.14, lz],
      materials.roverDark,
      true,
      false,
    );
  }

  // Table side panels.
  addBox("bayCollisionTableEndLeft", [1.55, 1.16, 0.14], [-5.8, 0.58, -3.66], materials.roverDark, true, false);
  addBox("bayCollisionTableEndRight", [1.55, 1.16, 0.14], [-5.8, 0.58, 3.66], materials.roverDark, true, false);
  addBox("bayCollisionTableBackPanel", [0.12, 0.5, 7.25], [-6.38, 0.74, 0], materials.roverDark, true, false);

  // Diagnostic screen console collision.
  addBox("bayCollisionScreenBase", [4.25, 1.3, 1.1], [0, 0.65, 4.33], materials.roverDark, true, false);

  addBox("bayCollisionScreenKeyboard", [2.9, 0.14, 0.78], [0, 1.33, 4.24], materials.roverDark, true, false);

  addBox("bayCollisionScreenBezel", [4.05, 3.0, 0.22], [0, 2.2, 4.7], materials.roverDark, true, false);

  // Diagnostic screen edge collision.
  addBox("bayCollisionScreenBaseFrontLip", [4.2, 0.16, 0.12], [0, 1.38, 3.75], materials.roverDark, true, false);

  addBox("bayCollisionScreenBaseBackStop", [4.2, 0.18, 0.12], [0, 1.39, 4.9], materials.roverDark, true, false);

  addBox("bayCollisionScreenBaseLeftLip", [0.12, 0.16, 1.1], [-2.15, 1.38, 4.33], materials.roverDark, true, false);

  addBox("bayCollisionScreenBaseRightLip", [0.12, 0.16, 1.1], [2.15, 1.38, 4.33], materials.roverDark, true, false);

  // Crate collision.
  addBox("bayCollisionCrateBackLeftStack", [1.4, 0.86, 1.0], [-5.6, 0.43, 3.75], materials.roverDark, true, false);
  addBox("bayCollisionCrateBackRightStack", [1.45, 0.6, 1.0], [5.58, 0.3, 3.75], materials.roverDark, true, false);
  addBox("bayCollisionCrateFrontLeftStack", [1.25, 0.48, 1.0], [-5.68, 0.24, -3.82], materials.roverDark, true, false);
  addBox("bayCollisionCrateFrontRightStack", [1.25, 0.48, 1.0], [5.68, 0.24, -3.82], materials.roverDark, true, false);
  addBox("bayCollisionCrateLeftWall", [0.55, 0.4, 0.6], [-6.05, 0.2, 0.3], materials.roverDark, true, false);
  addBox("bayCollisionCrateRightWall", [0.55, 0.4, 0.6], [6.05, 0.2, -0.55], materials.roverDark, true, false);

  // Button panel collision.
  addBox("bayCollisionButtonPanelBase", [0.18, 0.8, 2.9], [6.74, 0.4, -1.25], materials.roverDark, true, false);
  addBox("bayCollisionButtonPanelFace", [0.18, 2.6, 2.9], [6.74, 2.1, -1.25], materials.roverDark, true, false);
  addBox("bayCollisionButtonPanelTop", [0.18, 0.2, 2.9], [6.74, 3.5, -1.25], materials.roverDark, true, false);
}
