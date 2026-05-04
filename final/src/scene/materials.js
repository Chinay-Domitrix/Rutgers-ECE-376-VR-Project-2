import * as THREE from "three";

export function createMaterials() {
  return {
    floor: new THREE.MeshStandardMaterial({ color: 0x3d4248, roughness: 0.82 }),
    wall: new THREE.MeshStandardMaterial({ color: 0x2b3036, roughness: 0.88 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xf6c453, roughness: 0.6 }),
    rover: new THREE.MeshStandardMaterial({ color: 0x7c858c, roughness: 0.7 }),
    roverDark: new THREE.MeshStandardMaterial({ color: 0x32383d, roughness: 0.75 }),
    socketIdle: new THREE.MeshStandardMaterial({ color: 0x171a1d, emissive: 0x000000, roughness: 0.48 }),
    lightOff: new THREE.MeshStandardMaterial({ color: 0x351111, emissive: 0x140000 }),
    lightOn: new THREE.MeshStandardMaterial({ color: 0x56d88a, emissive: 0x1c5c35 }),
  };
}
