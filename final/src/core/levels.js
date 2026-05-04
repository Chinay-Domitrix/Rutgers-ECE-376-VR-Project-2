import * as THREE from "three";

const tableSpawnX = -5.75;
const tableSpawnY = 1.42;

const regularRepairPartDefinitions = [
  {
    id: "sideAccessPanel",
    label: "side access panel",
    rootName: "RR_Rover_Component_SideAccessPanel_Root",
    usePointName: "RR_Rover_Component_SideAccessPanel_UsePoint",
    missingPartId: "sideAccessPanel",
  },
  {
    id: "frontRightWheelMount",
    label: "front right wheel mount",
    rootName: "RR_Rover_Component_FrontRightWheelMount_Root",
    usePointName: "RR_Rover_Component_FrontRightWheelMount_UsePoint",
  },
  {
    id: "antennaModule",
    label: "antenna module",
    rootName: "RR_Rover_Component_AntennaModule_Root",
    usePointName: "RR_Rover_Component_AntennaModule_UsePoint",
    missingPartId: "antennaModule",
  },
  {
    id: "frontLeftHeadlamp",
    label: "front left headlamp",
    meshNames: ["RR_Rover_Headlamp_Left"],
  },
  {
    id: "frontRightHeadlamp",
    label: "front right headlamp",
    meshNames: ["RR_Rover_Headlamp_Right"],
  },
  {
    id: "frontBumper",
    label: "front bumper",
    meshNames: ["RR_Rover_Front_Bumper"],
  },
  {
    id: "rearBumper",
    label: "rear bumper",
    meshNames: ["RR_Rover_Rear_Bumper"],
  },
  {
    id: "rearLeftStatusLight",
    label: "rear left status light",
    meshNames: ["RR_Rover_Rear_Cyan_Status_Left"],
  },
  {
    id: "rearRightStatusLight",
    label: "rear right status light",
    meshNames: ["RR_Rover_Rear_Cyan_Status_Right"],
  },
  {
    id: "frontLeftWheel",
    label: "front left wheel",
    meshNamePattern: /^RR_Rover_Left_Wheel_3_/,
  },
  {
    id: "frontRightWheel",
    label: "front right wheel",
    meshNamePattern: /^RR_Rover_Right_Wheel_3_/,
  },
  {
    id: "powerDockContacts",
    label: "power dock contacts",
    meshNames: [
      "RR_Rover_PowerCellDock_Positive_Cyan_Contact",
      "RR_Rover_PowerCellDock_Negative_Steel_Contact",
      "RR_Rover_PowerCellDock_Terminal_Block",
    ],
  },
];

const regularMissingPartDefinitions = [
  {
    id: "sideAccessPanel",
    label: "side access panel",
    rootName: "RR_Rover_Component_SideAccessPanel_Root",
    snapTargetName: "RR_Rover_Component_SideAccessPanel_SnapTarget",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -1.2),
    physicsSize: [0.72, 0.32, 0.52],
  },
  {
    id: "frontRightWheelMount",
    label: "front right wheel mount",
    rootName: "RR_Rover_Component_FrontRightWheelMount_Root",
    snapTargetName: "RR_Rover_Component_FrontRightWheelMount_SnapTarget",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 0.15),
    physicsSize: [0.44, 0.34, 0.42],
  },
  {
    id: "antennaModule",
    label: "antenna module",
    rootName: "RR_Rover_Component_AntennaModule_Root",
    snapTargetName: "RR_Rover_Component_AntennaModule_SnapTarget",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 1.45),
    physicsSize: [0.5, 0.82, 0.5],
  },
  {
    id: "frontLeftWheel",
    label: "front left wheel",
    meshNamePattern: /^RR_Rover_Left_Wheel_3_/,
    snapLocalPosition: new THREE.Vector3(0.93, 0.36, 0.78),
    wheelId: "leftWheel3",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -2.55),
    physicsSize: [0.62, 0.62, 0.44],
  },
  {
    id: "frontRightWheel",
    label: "front right wheel",
    meshNamePattern: /^RR_Rover_Right_Wheel_3_/,
    snapLocalPosition: new THREE.Vector3(0.93, 0.36, -0.78),
    wheelId: "rightWheel3",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 2.55),
    physicsSize: [0.62, 0.62, 0.44],
  },
  {
    id: "frontBumper",
    label: "front bumper",
    meshNames: ["RR_Rover_Front_Bumper"],
    snapLocalPosition: new THREE.Vector3(1.32, 0.64, 0),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -0.55),
    physicsSize: [0.34, 0.3, 1.16],
  },
  {
    id: "rearBumper",
    label: "rear bumper",
    meshNames: ["RR_Rover_Rear_Bumper"],
    snapLocalPosition: new THREE.Vector3(-1.32, 0.64, 0),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 0.85),
    physicsSize: [0.34, 0.3, 1.16],
  },
  {
    id: "frontLeftHeadlamp",
    label: "front left headlamp",
    meshNames: ["RR_Rover_Headlamp_Left"],
    snapLocalPosition: new THREE.Vector3(1.39, 0.83, 0.33),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -3.05),
    physicsSize: [0.24, 0.22, 0.24],
  },
  {
    id: "frontRightHeadlamp",
    label: "front right headlamp",
    meshNames: ["RR_Rover_Headlamp_Right"],
    snapLocalPosition: new THREE.Vector3(1.39, 0.83, -0.33),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 3.05),
    physicsSize: [0.24, 0.22, 0.24],
  },
  {
    id: "rearLeftStatusLight",
    label: "rear left status light",
    meshNames: ["RR_Rover_Rear_Cyan_Status_Left"],
    snapLocalPosition: new THREE.Vector3(-1.39, 0.84, 0.33),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -3.35),
    physicsSize: [0.22, 0.2, 0.22],
  },
  {
    id: "rearRightStatusLight",
    label: "rear right status light",
    meshNames: ["RR_Rover_Rear_Cyan_Status_Right"],
    snapLocalPosition: new THREE.Vector3(-1.39, 0.84, -0.33),
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 3.35),
    physicsSize: [0.22, 0.2, 0.22],
  },
];

const complexRepairPartDefinitions = [
  complexRootRepair("complexSideAccessPanel", "side access panel", "SideAccessPanel", "complexSideAccessPanel"),
  complexRootRepair("complexAntennaModule", "antenna module", "AntennaModule", "complexAntennaModule"),
  complexRootRepair(
    "complexCenterMastCameraBox",
    "center mast camera box",
    "CenterMastCameraBox",
    "complexCenterMastCameraBox",
  ),
  complexRootRepair("complexFrontSensorArray", "front sensor array", "FrontSensorArray"),
  complexRootRepair("complexLeftSciencePod", "left science pod", "LeftSciencePod", "complexLeftSciencePod"),
  complexRootRepair("complexRightSciencePod", "right science pod", "RightSciencePod", "complexRightSciencePod"),
  complexRootRepair("complexTopServiceBox1", "top service box 1", "TopServiceBox1", "complexTopServiceBox1"),
  complexRootRepair("complexTopServiceBox2", "top service box 2", "TopServiceBox2", "complexTopServiceBox2"),
  complexRootRepair("complexTopServiceBox3", "top service box 3", "TopServiceBox3", "complexTopServiceBox3"),
  {
    id: "complexFrontLeftHeadlamp",
    label: "front left headlamp",
    meshNames: ["RR_Rover_Headlamp_Left"],
  },
  {
    id: "complexFrontRightHeadlamp",
    label: "front right headlamp",
    meshNames: ["RR_Rover_Headlamp_Right"],
  },
  {
    id: "complexHeavyFrontBumper",
    label: "heavy front bumper",
    meshNames: ["RR_Rover_Heavy_Front_Bumper"],
  },
  {
    id: "complexHeavyRearBumper",
    label: "heavy rear bumper",
    meshNames: ["RR_Rover_Heavy_Rear_Bumper"],
  },
];

const complexMissingPartDefinitions = [
  complexRootMissing("complexSideAccessPanel", "side access panel", "SideAccessPanel", -3.3, [0.72, 0.32, 0.52]),
  complexRootMissing("complexAntennaModule", "antenna module", "AntennaModule", -2.55, [0.5, 0.82, 0.5]),
  complexRootMissing(
    "complexCenterMastCameraBox",
    "center mast camera box",
    "CenterMastCameraBox",
    -1.8,
    [0.46, 0.42, 0.46],
  ),
  complexRootMissing("complexLeftSciencePod", "left science pod", "LeftSciencePod", -1.05, [0.62, 0.44, 0.52]),
  complexRootMissing("complexRightSciencePod", "right science pod", "RightSciencePod", -0.3, [0.62, 0.44, 0.52]),
  complexRootMissing("complexTopServiceBox1", "top service box 1", "TopServiceBox1", 0.45, [0.48, 0.38, 0.44]),
  complexRootMissing("complexTopServiceBox2", "top service box 2", "TopServiceBox2", 1.2, [0.48, 0.38, 0.44]),
  complexRootMissing("complexTopServiceBox3", "top service box 3", "TopServiceBox3", 1.95, [0.48, 0.38, 0.44]),
  complexRootMissing("complexFrontSensorArray", "front sensor array", "FrontSensorArray", 2.7, [0.34, 0.28, 0.82]),
  {
    id: "complexLeftWheel4",
    label: "front left wheel",
    meshNamePattern: /^RR_Rover_Left_Wheel_4_/,
    wheelId: "leftWheel4",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -3.0),
    physicsSize: [0.62, 0.62, 0.44],
  },
  {
    id: "complexRightWheel4",
    label: "front right wheel",
    meshNamePattern: /^RR_Rover_Right_Wheel_4_/,
    wheelId: "rightWheel4",
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 3.0),
    physicsSize: [0.62, 0.62, 0.44],
  },
  {
    id: "complexHeavyFrontBumper",
    label: "heavy front bumper",
    meshNames: ["RR_Rover_Heavy_Front_Bumper"],
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, -0.65),
    physicsSize: [0.42, 0.34, 1.28],
  },
  {
    id: "complexHeavyRearBumper",
    label: "heavy rear bumper",
    meshNames: ["RR_Rover_Heavy_Rear_Bumper"],
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, 0.85),
    physicsSize: [0.42, 0.34, 1.28],
  },
];

export const repairPartDefinitions = [...regularRepairPartDefinitions, ...complexRepairPartDefinitions];

export const missingPartDefinitions = [...regularMissingPartDefinitions, ...complexMissingPartDefinitions];

export function getLevelConfig(level) {
  const normalizedLevel = Math.max(1, Math.floor(level));
  const completionBonus = 150 + normalizedLevel * 50;
  const timerDuration = Math.max(90, 190 - normalizedLevel * 10);

  if (normalizedLevel === 1) {
    return {
      level: normalizedLevel,
      roverType: "regular",
      requiresPowerCell: true,
      powerCellSlots: ["main"],
      requiredPowerCellCount: 1,
      repairTargetIds: [],
      missingPartIds: [],
      completionBonus,
      timerDuration: 180,
    };
  }

  if (normalizedLevel === 2) {
    return {
      level: normalizedLevel,
      roverType: "regular",
      requiresPowerCell: false,
      powerCellSlots: [],
      requiredPowerCellCount: 0,
      repairTargetIds: ["sideAccessPanel"],
      missingPartIds: [],
      completionBonus,
      timerDuration: 170,
    };
  }

  if (normalizedLevel <= 5) {
    const repairCount = normalizedLevel <= 3 ? 1 : 2;
    const missingCount = normalizedLevel <= 4 ? 1 : 2;
    const repairTargetIds = pickCycledIds(regularRepairPartDefinitions, repairCount, normalizedLevel - 3);
    const missingPartIds = pickCycledIds(regularMissingPartDefinitions, missingCount, normalizedLevel - 1);

    return {
      level: normalizedLevel,
      roverType: "regular",
      requiresPowerCell: normalizedLevel !== 4,
      powerCellSlots: normalizedLevel !== 4 ? ["main"] : [],
      requiredPowerCellCount: normalizedLevel !== 4 ? 1 : 0,
      repairTargetIds,
      missingPartIds,
      completionBonus,
      timerDuration,
    };
  }

  const repairCount = Math.min(complexRepairPartDefinitions.length, 2 + Math.floor((normalizedLevel - 6) / 2));
  const missingCount = Math.min(complexMissingPartDefinitions.length, 2 + Math.floor((normalizedLevel - 6) / 3));
  const initialPowerCellSlots = getComplexInitialPowerCellSlots(normalizedLevel);

  return {
    level: normalizedLevel,
    roverType: "complex",
    requiresPowerCell: true,
    powerCellSlots: ["A", "B"],
    requiredPowerCellCount: 2,
    initialPowerCellSlots,
    repairTargetIds: pickCycledIds(complexRepairPartDefinitions, repairCount, normalizedLevel - 6),
    missingPartIds: pickCycledIds(complexMissingPartDefinitions, missingCount, normalizedLevel - 6),
    completionBonus,
    timerDuration,
  };
}

function getComplexInitialPowerCellSlots(level) {
  const cycle = (level - 6) % 3;
  if (cycle === 1) return ["A"];
  if (cycle === 2) return ["B"];
  return [];
}

function complexRootRepair(id, label, componentName, missingPartId = "") {
  return {
    id,
    label,
    rootName: `RR_Rover_Component_${componentName}_Root`,
    usePointName: `RR_Rover_Component_${componentName}_UsePoint`,
    ...(missingPartId ? { missingPartId } : {}),
  };
}

function complexRootMissing(id, label, componentName, spawnZ, physicsSize) {
  return {
    id,
    label,
    rootName: `RR_Rover_Component_${componentName}_Root`,
    snapTargetName: `RR_Rover_Component_${componentName}_SnapTarget`,
    spawnPosition: new THREE.Vector3(tableSpawnX, tableSpawnY, spawnZ),
    physicsSize,
  };
}

function pickCycledIds(definitions, count, offset) {
  const ids = [];
  for (let index = 0; index < count; index += 1) {
    ids.push(definitions[(index + offset) % definitions.length].id);
  }
  return ids;
}
