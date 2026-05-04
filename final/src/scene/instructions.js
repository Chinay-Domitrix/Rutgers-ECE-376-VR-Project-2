import * as THREE from "three";

export function createInstructionText({ scene }) {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 384;
  const texture = new THREE.CanvasTexture(canvas);
  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(2.8, 1.05),
    new THREE.MeshBasicMaterial({ map: texture, transparent: true }),
  );
  panel.position.set(-6.82, 2.05, 0.25);
  panel.rotation.y = Math.PI / 2;
  scene.add(panel);
  panel.userData = { canvas, texture };
  return panel;
}
