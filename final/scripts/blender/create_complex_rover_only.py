from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module
import math
from pathlib import Path
from typing import Any

bpy: Any = import_module("bpy")
Collection = Any
Material = Any
Node = Any
Object = Any

PROJECT_ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path(".").resolve()
ASSET_ROOT = PROJECT_ROOT / "src" / "assets"
MODEL_DIR = ASSET_ROOT / "models"
BLEND_DIR = ASSET_ROOT / "blend"
BLEND_FILE = BLEND_DIR / "rover_complex_only.blend"

ROT_X_90 = (math.pi / 2.0, 0.0, 0.0)
ROT_Y_90 = (0.0, math.pi / 2.0, 0.0)
ROT_Z_90 = (0.0, 0.0, math.pi / 2.0)


# ============================================================
# Scene / material helpers
# ============================================================


def ensure_output_dirs() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    BLEND_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    for block in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.textures,
        bpy.data.images,
        bpy.data.collections,
    ):
        for item in (*block,):
            if item.users == 0:
                block.remove(item)


def set_node_input(node: Node, input_name: str, value: Any) -> bool:
    socket = node.inputs.get(input_name)
    if socket is None:
        return False
    socket.default_value = value
    return True


def set_custom_props(obj: Object, **props: str) -> Object:
    for key, value in props.items():
        obj[key] = value
    return obj


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.75,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        set_node_input(bsdf, "Base Color", color)
        set_node_input(bsdf, "Metallic", metallic)
        set_node_input(bsdf, "Roughness", roughness)

        if emission is not None:
            if not set_node_input(bsdf, "Emission Color", emission):
                set_node_input(bsdf, "Emission", emission)
            set_node_input(bsdf, "Emission Strength", emission_strength)

    return mat


def make_materials() -> dict[str, Material]:
    return {
        "sand": make_material("RR2_muted_sand_hull", (0.56, 0.51, 0.40, 1.0)),
        "sand_dark": make_material("RR2_darker_sand_panels", (0.38, 0.33, 0.25, 1.0)),
        "warm_gray": make_material("RR2_warm_gray_panels", (0.33, 0.35, 0.35, 1.0)),
        "dark": make_material("RR2_dark_gunmetal", (0.055, 0.062, 0.070, 1.0), metallic=0.28),
        "steel": make_material("RR2_brushed_steel", (0.45, 0.47, 0.47, 1.0), metallic=0.42, roughness=0.45),
        "rubber": make_material("RR2_flat_black_rubber", (0.014, 0.013, 0.012, 1.0), roughness=0.92),
        "orange": make_material("RR2_safety_orange", (1.0, 0.36, 0.08, 1.0)),
        "yellow": make_material("RR2_warning_yellow", (1.0, 0.73, 0.09, 1.0)),
        "red": make_material("RR2_damage_red", (0.88, 0.08, 0.04, 1.0)),
        "green": make_material(
            "RR2_ready_green_light",
            (0.09, 1.0, 0.32, 1.0),
            emission=(0.09, 1.0, 0.32, 1.0),
            emission_strength=1.4,
        ),
        "glass": make_material("RR2_smoked_blue_glass", (0.04, 0.12, 0.17, 0.86), roughness=0.24),
        "cyan": make_material(
            "RR2_cyan_indicator_light",
            (0.03, 0.85, 1.0, 1.0),
            emission=(0.03, 0.85, 1.0, 1.0),
            emission_strength=2.2,
        ),
        "white_light": make_material(
            "RR2_soft_white_light",
            (0.95, 0.95, 0.82, 1.0),
            emission=(0.95, 0.95, 0.82, 1.0),
            emission_strength=1.5,
        ),
        "blue_dark": make_material("RR2_deep_blue_panel", (0.02, 0.06, 0.12, 1.0), roughness=0.55),
    }


def make_collection(name: str) -> Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: Object, collection: Collection) -> None:
    if obj.name not in collection.objects.keys():
        collection.objects.link(obj)
    for user_collection in (*obj.users_collection,):
        if user_collection != collection:
            user_collection.objects.unlink(obj)


def add_bevel(obj: Object, width: float, segments: int = 1) -> None:
    if width <= 0:
        return
    bevel = obj.modifiers.new("small_bevel", "BEVEL")
    bevel.width = width
    bevel.segments = segments
    bevel.profile = 0.5

    normals = obj.modifiers.new("weighted_corner_normals", "WEIGHTED_NORMAL")
    normals.keep_sharp = True


def assign_material(obj: Object, mat: Material | None) -> None:
    if mat is not None:
        obj.data.materials.append(mat)


# ============================================================
# Primitive helpers
# ============================================================


def create_empty(
    name: str,
    loc: tuple[float, float, float],
    collection: Collection,
    *,
    parent: Object | None = None,
    display_type: str = "PLAIN_AXES",
    display_size: float = 0.18,
) -> Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = display_type
    obj.empty_display_size = display_size
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    return obj


def create_cube(
    name: str,
    loc: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: Material,
    collection: Collection,
    *,
    parent: Object | None = None,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
    bevel_segments: int = 1,
) -> Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    move_to_collection(obj, collection)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rotation
    obj.scale = scale
    assign_material(obj, mat)
    add_bevel(obj, bevel, bevel_segments)
    return obj


def create_cylinder(
    name: str,
    loc: tuple[float, float, float],
    radius: float,
    depth: float,
    mat: Material,
    collection: Collection,
    *,
    vertices: int = 12,
    parent: Object | None = None,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
) -> Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        end_fill_type="NGON",
        location=(0.0, 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    move_to_collection(obj, collection)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rotation
    assign_material(obj, mat)
    add_bevel(obj, bevel)
    return obj


def create_cone(
    name: str,
    loc: tuple[float, float, float],
    radius1: float,
    radius2: float,
    depth: float,
    mat: Material,
    collection: Collection,
    *,
    vertices: int = 8,
    parent: Object | None = None,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
) -> Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=(0.0, 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    move_to_collection(obj, collection)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rotation
    assign_material(obj, mat)
    add_bevel(obj, bevel)
    return obj


def create_mesh_object(
    name: str,
    verts: Sequence[tuple[float, float, float]],
    faces: Sequence[tuple[int, ...]],
    loc: tuple[float, float, float],
    mat: Material,
    collection: Collection,
    *,
    parent: Object | None = None,
    bevel: float = 0.0,
) -> Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    assign_material(obj, mat)
    add_bevel(obj, bevel)
    return obj


def create_tapered_box(
    name: str,
    loc: tuple[float, float, float],
    bottom_size: tuple[float, float],
    top_size: tuple[float, float],
    height: float,
    mat: Material,
    collection: Collection,
    *,
    parent: Object | None = None,
    bevel: float = 0.0,
) -> Object:
    bx, by = bottom_size
    tx, ty = top_size
    h = height / 2.0
    verts = [
        (-bx / 2, -by / 2, -h),
        (bx / 2, -by / 2, -h),
        (bx / 2, by / 2, -h),
        (-bx / 2, by / 2, -h),
        (-tx / 2, -ty / 2, h),
        (tx / 2, -ty / 2, h),
        (tx / 2, ty / 2, h),
        (-tx / 2, ty / 2, h),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return create_mesh_object(name, verts, faces, loc, mat, collection, parent=parent, bevel=bevel)


def create_sloped_box(
    name: str,
    loc: tuple[float, float, float],
    size: tuple[float, float, float],
    mat: Material,
    collection: Collection,
    *,
    parent: Object | None = None,
    front_top_z: float = 0.0,
    back_top_z: float = 0.0,
    bevel: float = 0.0,
) -> Object:
    length, width, height = size
    lx = length / 2.0
    wy = width / 2.0
    bottom_z = -height / 2.0
    verts = [
        (-lx, -wy, bottom_z),
        (lx, -wy, bottom_z),
        (lx, wy, bottom_z),
        (-lx, wy, bottom_z),
        (-lx, -wy, back_top_z),
        (lx, -wy, front_top_z),
        (lx, wy, front_top_z),
        (-lx, wy, back_top_z),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return create_mesh_object(name, verts, faces, loc, mat, collection, parent=parent, bevel=bevel)


def add_panel_bolts(
    prefix: str,
    centers: list[tuple[float, float, float]],
    mat: Material,
    collection: Collection,
    parent: Object | None,
    *,
    axis: str = "y",
    radius: float = 0.025,
) -> None:
    rotation = ROT_X_90 if axis == "y" else ROT_Y_90
    for index, loc in enumerate(centers, start=1):
        create_cylinder(
            f"{prefix}_Bolt_{index:02d}",
            loc,
            radius,
            0.018,
            mat,
            collection,
            vertices=8,
            parent=parent,
            rotation=rotation,
        )


# ============================================================
# Detail builders
# ============================================================


def add_wheel_treads(
    prefix: str,
    wheel_center: tuple[float, float, float],
    side_sign: int,
    mats: dict[str, Material],
    collection: Collection,
    parent: Object | None,
) -> None:
    cx, cy, cz = wheel_center
    radius = 0.335
    for index in range(12):
        angle = (math.tau / 12.0) * index
        x = cx + math.cos(angle) * radius
        z = cz + math.sin(angle) * radius
        create_cube(
            f"{prefix}_Tread_{index:02d}",
            (x, cy + side_sign * 0.012, z),
            (0.095, 0.325, 0.040),
            mats["rubber"],
            collection,
            parent=parent,
            rotation=(0.0, -angle, 0.0),
            bevel=0.006,
        )


def add_side_science_pod(
    side_name: str,
    side_sign: int,
    mats: dict[str, Material],
    collection: Collection,
    root: Object,
) -> None:
    y = side_sign * 0.72
    face_y = side_sign * 0.795
    light_y = side_sign * 0.812
    vent_y = side_sign * 0.808

    component_id = f"{side_name.lower()}_science_pod"

    pod_root = set_custom_props(
        create_empty(
            f"RR_Rover_Component_{side_name}SciencePod_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.20,
        ),
        interaction_role="removable_component",
        component_id=component_id,
    )

    # Main pod body. Parent it to the component root so levels.js can hide it,
    # clone it, spawn it on the tool table, and snap it back onto the rover.
    create_cube(
        f"RR_Rover_{side_name}_SciencePod_MainBox",
        (-0.38, y, 0.91),
        (0.66, 0.105, 0.34),
        mats["warm_gray"],
        collection,
        parent=pod_root,
        bevel=0.020,
    )

    # Outer face plate so the cyan indicators and vents sit on a visible surface
    # instead of appearing embedded inside the main box.
    create_cube(
        f"RR_Rover_{side_name}_SciencePod_FacePlate",
        (-0.38, face_y, 0.92),
        (0.60, 0.020, 0.26),
        mats["blue_dark"],
        collection,
        parent=pod_root,
        bevel=0.008,
    )

    for i, x in enumerate([-0.63, -0.38, -0.13], start=1):
        create_cube(
            f"RR_Rover_{side_name}_SciencePod_CyanLight_{i}",
            (x, light_y, 1.00),
            (0.070, 0.014, 0.055),
            mats["cyan"],
            collection,
            parent=pod_root,
            bevel=0.004,
        )

    for i, z in enumerate([0.80, 0.91, 1.02], start=1):
        create_cube(
            f"RR_Rover_{side_name}_SciencePod_Vent_{i}",
            (-0.08, vent_y, z),
            (0.24, 0.012, 0.024),
            mats["dark"],
            collection,
            parent=pod_root,
            bevel=0.002,
        )

    set_custom_props(
        create_empty(
            f"RR_Rover_Component_{side_name}SciencePod_GrabPoint",
            (-0.38, side_sign * 0.92, 0.95),
            collection,
            parent=pod_root,
            display_type="SPHERE",
            display_size=0.12,
        ),
        interaction_role="component_grab_point",
        component_id=component_id,
    )

    set_custom_props(
        create_empty(
            f"RR_Rover_Component_{side_name}SciencePod_UsePoint",
            (-0.38, side_sign * 0.90, 0.92),
            collection,
            parent=pod_root,
            display_type="ARROWS",
            display_size=0.13,
        ),
        interaction_role="repair_use_point",
        component_id=component_id,
    )

    set_custom_props(
        create_empty(
            f"RR_Rover_Component_{side_name}SciencePod_SnapTarget",
            (-0.38, y, 0.91),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id=component_id,
    )


def add_sensor_mast(mats: dict[str, Material], collection: Collection, root: Object) -> None:
    create_cube(
        "RR_Rover_Center_Mast_Base",
        (-0.65, 0.0, 1.32),
        (0.26, 0.24, 0.08),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.012,
    )
    create_cylinder(
        "RR_Rover_Center_Mast_Pole",
        (-0.65, 0.0, 1.62),
        0.035,
        0.58,
        mats["steel"],
        collection,
        vertices=10,
        parent=root,
        bevel=0.005,
    )

    component_id = "center_mast_camera_box"
    camera_root = set_custom_props(
        create_empty(
            "RR_Rover_Component_CenterMastCameraBox_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.16,
        ),
        interaction_role="removable_component",
        component_id=component_id,
    )

    create_cube(
        "RR_Rover_Center_Mast_Camera_Box",
        (-0.65, 0.0, 1.95),
        (0.30, 0.18, 0.12),
        mats["dark"],
        collection,
        parent=camera_root,
        bevel=0.015,
    )

    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        create_cylinder(
            f"RR_Rover_Center_Mast_{side_name}_CyanLens",
            (-0.65, side_sign * 0.105, 1.95),
            0.035,
            0.018,
            mats["cyan"],
            collection,
            vertices=8,
            parent=camera_root,
            rotation=ROT_X_90,
            bevel=0.002,
        )

    set_custom_props(
        create_empty(
            "RR_Rover_Component_CenterMastCameraBox_GrabPoint",
            (-0.65, 0.0, 2.06),
            collection,
            parent=camera_root,
            display_type="SPHERE",
            display_size=0.11,
        ),
        interaction_role="component_grab_point",
        component_id=component_id,
    )

    set_custom_props(
        create_empty(
            "RR_Rover_Component_CenterMastCameraBox_UsePoint",
            (-0.65, 0.0, 2.05),
            collection,
            parent=camera_root,
            display_type="ARROWS",
            display_size=0.12,
        ),
        interaction_role="repair_use_point",
        component_id=component_id,
    )

    set_custom_props(
        create_empty(
            "RR_Rover_Component_CenterMastCameraBox_SnapTarget",
            (-0.65, 0.0, 1.95),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.14,
        ),
        interaction_role="component_snap_target",
        component_id=component_id,
    )


def add_roof_equipment(mats: dict[str, Material], collection: Collection, root: Object) -> None:
    # Raised sensor rail and small storage boxes on the top deck.
    create_cube(
        "RR_Rover_Top_Equipment_Rail_Left",
        (-0.05, -0.46, 1.255),
        (1.75, 0.045, 0.06),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.008,
    )
    create_cube(
        "RR_Rover_Top_Equipment_Rail_Right",
        (-0.05, 0.46, 1.255),
        (1.75, 0.045, 0.06),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.008,
    )

    for i, x in enumerate([-0.96, -0.72, -0.48, 0.38, 0.62], start=1):
        create_cube(
            f"RR_Rover_TopVent_Slat_{i:02d}",
            (x, 0.50, 1.14),
            (0.14, 0.040, 0.026),
            mats["dark"],
            collection,
            parent=root,
            bevel=0.002,
        )

    service_box_data = [
        (1, (0.12, -0.40, 1.27), (0.26, 0.18, 0.11)),
        (2, (0.46, -0.40, 1.27), (0.26, 0.18, 0.11)),
        (3, (0.82, 0.40, 1.27), (0.26, 0.18, 0.11)),
    ]

    for index, (x, y, z), size in service_box_data:
        component_id = f"top_service_box_{index}"

        box_root = set_custom_props(
            create_empty(
                f"RR_Rover_Component_TopServiceBox{index}_Root",
                (0.0, 0.0, 0.0),
                collection,
                parent=root,
                display_type="CUBE",
                display_size=0.16,
            ),
            interaction_role="removable_component",
            component_id=component_id,
        )

        create_cube(
            f"RR_Rover_Top_Service_Box_{index}",
            (x, y, z),
            size,
            mats["sand_dark"],
            collection,
            parent=box_root,
            bevel=0.012,
        )
        create_cube(
            f"RR_Rover_Top_Service_Box_{index}_LidPanel",
            (x, y, z + 0.065),
            (0.18, 0.12, 0.012),
            mats["blue_dark"],
            collection,
            parent=box_root,
            bevel=0.003,
        )
        create_cube(
            f"RR_Rover_Top_Service_Box_{index}_StatusLight",
            (x, y, z + 0.074),
            (0.045, 0.030, 0.012),
            mats["cyan"],
            collection,
            parent=box_root,
            bevel=0.002,
        )

        set_custom_props(
            create_empty(
                f"RR_Rover_Component_TopServiceBox{index}_GrabPoint",
                (x, y, z + 0.13),
                collection,
                parent=box_root,
                display_type="SPHERE",
                display_size=0.11,
            ),
            interaction_role="component_grab_point",
            component_id=component_id,
        )

        set_custom_props(
            create_empty(
                f"RR_Rover_Component_TopServiceBox{index}_UsePoint",
                (x, y, z + 0.14),
                collection,
                parent=box_root,
                display_type="ARROWS",
                display_size=0.12,
            ),
            interaction_role="repair_use_point",
            component_id=component_id,
        )

        set_custom_props(
            create_empty(
                f"RR_Rover_Component_TopServiceBox{index}_SnapTarget",
                (x, y, z),
                collection,
                parent=root,
                display_type="ARROWS",
                display_size=0.14,
            ),
            interaction_role="component_snap_target",
            component_id=component_id,
        )


def add_dual_power_cell_dock(
    dock_id: str,
    x: float,
    y: float,
    mats: dict[str, Material],
    collection: Collection,
    root: Object,
    *,
    create_legacy_alias: bool = False,
) -> Object:
    dock_root = set_custom_props(
        create_empty(
            f"RR_Rover_PowerCellDock_{dock_id}_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.20,
        ),
        interaction_role="power_cell_receiver",
        accepts="RR_PowerCell_Root",
        dock_id=dock_id,
    )

    create_cube(
        f"RR_Rover_PowerCellDock_{dock_id}_Outer_Bezeled_Frame",
        (x, y, 1.145),
        (0.98, 0.45, 0.080),
        mats["dark"],
        collection,
        parent=dock_root,
        bevel=0.024,
    )
    create_cube(
        f"RR_Rover_PowerCellDock_{dock_id}_Rectangular_Recess",
        (x, y, 1.205),
        (0.84, 0.34, 0.045),
        mats["rubber"],
        collection,
        parent=dock_root,
        bevel=0.016,
    )
    create_cube(
        f"RR_Rover_PowerCellDock_{dock_id}_Battery_Seat",
        (x, y, 1.245),
        (0.78, 0.30, 0.032),
        mats["warm_gray"],
        collection,
        parent=dock_root,
        bevel=0.010,
    )

    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        create_cube(
            f"RR_Rover_PowerCellDock_{dock_id}_{side_name}_Guide_Rail",
            (x, y + side_sign * 0.225, 1.315),
            (0.88, 0.046, 0.105),
            mats["yellow"],
            collection,
            parent=dock_root,
            bevel=0.010,
        )

    create_cube(
        f"RR_Rover_PowerCellDock_{dock_id}_Terminal_Block",
        (x - 0.47, y, 1.330),
        (0.070, 0.31, 0.155),
        mats["steel"],
        collection,
        parent=dock_root,
        bevel=0.012,
    )
    create_cylinder(
        f"RR_Rover_PowerCellDock_{dock_id}_Positive_Cyan_Contact",
        (x - 0.515, y - 0.070, 1.345),
        0.045,
        0.028,
        mats["cyan"],
        collection,
        vertices=8,
        parent=dock_root,
        rotation=ROT_Y_90,
        bevel=0.003,
    )
    create_cylinder(
        f"RR_Rover_PowerCellDock_{dock_id}_Negative_Steel_Contact",
        (x - 0.515, y + 0.070, 1.345),
        0.045,
        0.028,
        mats["dark"],
        collection,
        vertices=8,
        parent=dock_root,
        rotation=ROT_Y_90,
        bevel=0.003,
    )

    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        create_cube(
            f"RR_Rover_PowerCellDock_{dock_id}_{side_name}_Latch",
            (x + 0.40, y + side_sign * 0.125, 1.392),
            (0.085, 0.036, 0.125),
            mats["orange"],
            collection,
            parent=dock_root,
            bevel=0.009,
        )

    set_custom_props(
        create_empty(
            f"RR_Rover_PowerCell{dock_id}_SnapTarget",
            (x, y, 1.365),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.22,
        ),
        interaction_role="socket_snap_target",
        accepts="RR_PowerCell_InsertPoint",
        dock_id=dock_id,
    )

    # Compatibility with your current one-power-cell JS. This aliases Dock A as the old name.
    if create_legacy_alias:
        set_custom_props(
            create_empty(
                "RR_Rover_PowerCell_SnapTarget",
                (x, y, 1.365),
                collection,
                parent=root,
                display_type="ARROWS",
                display_size=0.25,
            ),
            interaction_role="socket_snap_target",
            accepts="RR_PowerCell_InsertPoint",
            dock_id=dock_id,
        )

    return dock_root


# ============================================================
# Complex rover
# ============================================================


def build_complex_rover(mats: dict[str, Material], preview_offset: tuple[float, float, float]) -> Object:
    collection = make_collection("RR_Asset_Rover_Complex")
    root = create_empty(
        "RR_Rover_Root",
        preview_offset,
        collection,
        display_type="CUBE",
        display_size=0.40,
    )

    # Longer base than the original rover: approximately 3.6 m footprint.
    create_cube(
        "RR_Rover_Extended_Underbody_Frame",
        (0.0, 0.0, 0.52),
        (3.45, 1.42, 0.18),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.040,
    )
    create_cube(
        "RR_Rover_Extended_Main_Chassis",
        (0.0, 0.0, 0.77),
        (3.15, 1.18, 0.40),
        mats["sand"],
        collection,
        parent=root,
        bevel=0.060,
    )
    create_cube(
        "RR_Rover_Lower_Side_Armor_Left",
        (0.0, -0.69, 0.76),
        (3.05, 0.075, 0.34),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.015,
    )
    create_cube(
        "RR_Rover_Lower_Side_Armor_Right",
        (0.0, 0.69, 0.76),
        (3.05, 0.075, 0.34),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.015,
    )

    create_sloped_box(
        "RR_Rover_Sloped_Front_Hood_Long",
        (1.08, 0.0, 1.04),
        (0.95, 1.03, 0.48),
        mats["warm_gray"],
        collection,
        parent=root,
        front_top_z=-0.055,
        back_top_z=0.25,
        bevel=0.035,
    )
    create_tapered_box(
        "RR_Rover_Reinforced_Cockpit",
        (0.08, 0.0, 1.22),
        (0.96, 0.90),
        (0.58, 0.58),
        0.46,
        mats["glass"],
        collection,
        parent=root,
        bevel=0.030,
    )
    create_cube(
        "RR_Rover_Rear_Dual_Battery_Service_Deck",
        (-1.03, 0.0, 1.04),
        (1.25, 1.02, 0.14),
        mats["warm_gray"],
        collection,
        parent=root,
        bevel=0.026,
    )

    # 8 wheels total: 4 on each side.
    wheel_x_positions = [-1.32, -0.44, 0.44, 1.32]
    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        y = side_sign * 0.80
        for wheel_index, x in enumerate(wheel_x_positions, start=1):
            prefix = f"RR_Rover_{side_name}_Wheel_{wheel_index}"
            create_cylinder(
                f"{prefix}_Rubber_Tire",
                (x, y, 0.36),
                0.33,
                0.30,
                mats["rubber"],
                collection,
                vertices=14,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.016,
            )
            create_cylinder(
                f"{prefix}_Orange_Hub",
                (x, y, 0.36),
                0.165,
                0.325,
                mats["orange"],
                collection,
                vertices=10,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.010,
            )
            create_cylinder(
                f"{prefix}_Cyan_Center_Cap",
                (x, y + side_sign * 0.172, 0.36),
                0.055,
                0.018,
                mats["cyan"],
                collection,
                vertices=8,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.002,
            )
            add_wheel_treads(prefix, (x, y, 0.36), side_sign, mats, collection, root)
            create_cube(
                f"RR_Rover_{side_name}_Suspension_Arm_{wheel_index}",
                (x, side_sign * 0.55, 0.59),
                (0.18, 0.43, 0.080),
                mats["steel"],
                collection,
                parent=root,
                rotation=(0.0, 0.0, side_sign * 0.08),
                bevel=0.012,
            )
            create_cylinder(
                f"RR_Rover_{side_name}_Suspension_Joint_{wheel_index}",
                (x, side_sign * 0.49, 0.60),
                0.055,
                0.055,
                mats["dark"],
                collection,
                vertices=8,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.004,
            )

    # Bumpers, headlights, rear lights, tow hooks.
    create_cube(
        "RR_Rover_Heavy_Front_Bumper",
        (1.73, 0.0, 0.65),
        (0.14, 1.16, 0.18),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.025,
    )
    create_cube(
        "RR_Rover_Heavy_Rear_Bumper",
        (-1.73, 0.0, 0.65),
        (0.14, 1.16, 0.18),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.025,
    )
    for side_y in [-0.40, 0.40]:
        create_cylinder(
            f"RR_Rover_Headlamp_{'Left' if side_y < 0 else 'Right'}",
            (1.82, side_y, 0.86),
            0.078,
            0.038,
            mats["white_light"],
            collection,
            vertices=10,
            parent=root,
            rotation=ROT_Y_90,
            bevel=0.004,
        )
        create_cube(
            f"RR_Rover_Rear_Cyan_Status_{'Left' if side_y < 0 else 'Right'}",
            (-1.82, side_y, 0.86),
            (0.035, 0.13, 0.060),
            mats["cyan"],
            collection,
            parent=root,
            bevel=0.006,
        )
        create_cube(
            f"RR_Rover_Rear_Red_Brake_{'Left' if side_y < 0 else 'Right'}",
            (-1.825, side_y, 0.72),
            (0.032, 0.11, 0.045),
            mats["red"],
            collection,
            parent=root,
            bevel=0.004,
        )

    # Two power-cell docks on the rear service deck.
    add_dual_power_cell_dock("A", -0.82, -0.26, mats, collection, root, create_legacy_alias=True)
    add_dual_power_cell_dock("B", -0.82, 0.26, mats, collection, root)

    # Extra science/equipment detail.
    add_roof_equipment(mats, collection, root)
    add_sensor_mast(mats, collection, root)
    add_side_science_pod("Left", -1, mats, collection, root)
    add_side_science_pod("Right", 1, mats, collection, root)

    # Front sensor bar and underside skid plates.
    create_cube(
        "RR_Rover_Front_Cyan_Sensor_Bar",
        (1.77, 0.0, 1.02),
        (0.035, 0.64, 0.045),
        mats["cyan"],
        collection,
        parent=root,
        bevel=0.004,
    )
    for i, x in enumerate([-0.95, -0.35, 0.35, 0.95], start=1):
        create_cube(
            f"RR_Rover_Bottom_SkidPlate_{i}",
            (x, 0.0, 0.39),
            (0.36, 0.92, 0.030),
            mats["steel"],
            collection,
            parent=root,
            bevel=0.006,
        )

    # Repair/removable components similar to your original naming style.
    side_panel_root = set_custom_props(
        create_empty(
            "RR_Rover_Component_SideAccessPanel_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.18,
        ),
        interaction_role="removable_component",
        component_id="side_access_panel",
    )
    # Make the side access panel thicker so the front/back faces do not z-fight
    # or show texture/display artifacts when exported.
    # Make the side access panel thicker and align it with the science pod protrusion.
    # Left science pod outer face is around Y = -0.795 to -0.812.
    create_cube(
        "RR_Rover_Component_SideAccessPanel_Panel",
        (0.40, -0.755, 0.91),
        (0.66, 0.105, 0.30),
        mats["warm_gray"],
        collection,
        parent=side_panel_root,
        bevel=0.014,
    )
    create_cube(
        "RR_Rover_Component_SideAccessPanel_Trim",
        (0.40, -0.815, 0.91),
        (0.58, 0.020, 0.22),
        mats["blue_dark"],
        collection,
        parent=side_panel_root,
        bevel=0.004,
    )
    create_cube(
        "RR_Rover_Component_SideAccessPanel_Damaged_Seam",
        (0.40, -0.832, 0.92),
        (0.48, 0.016, 0.045),
        mats["red"],
        collection,
        parent=side_panel_root,
        rotation=(0.0, 0.0, 0.18),
        bevel=0.004,
    )
    add_panel_bolts(
        "RR_Rover_Component_SideAccessPanel",
        [(0.12, -0.830, 0.77), (0.68, -0.830, 0.77), (0.12, -0.830, 1.04), (0.68, -0.830, 1.04)],
        mats["steel"],
        collection,
        side_panel_root,
        axis="y",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_SideAccessPanel_GrabPoint",
            (0.40, -0.90, 0.93),
            collection,
            parent=side_panel_root,
            display_type="SPHERE",
            display_size=0.12,
        ),
        interaction_role="component_grab_point",
        component_id="side_access_panel",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_SideAccessPanel_UsePoint",
            (0.40, -0.90, 0.91),
            collection,
            parent=side_panel_root,
            display_type="ARROWS",
            display_size=0.13,
        ),
        interaction_role="repair_use_point",
        component_id="side_access_panel",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_SideAccessPanel_SnapTarget",
            (0.40, -0.755, 0.91),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id="side_access_panel",
    )

    antenna_root = set_custom_props(
        create_empty(
            "RR_Rover_Component_AntennaModule_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.18,
        ),
        interaction_role="removable_component",
        component_id="antenna_module",
    )
    create_cube(
        "RR_Rover_Component_AntennaModule_BasePlate",
        (-1.34, 0.47, 1.17),
        (0.34, 0.27, 0.060),
        mats["steel"],
        collection,
        parent=antenna_root,
        bevel=0.012,
    )
    create_cube(
        "RR_Rover_Component_AntennaModule_Damaged_Collar",
        (-1.34, 0.47, 1.235),
        (0.20, 0.18, 0.045),
        mats["red"],
        collection,
        parent=antenna_root,
        bevel=0.008,
    )
    create_cylinder(
        "RR_Rover_Component_AntennaModule_Mast",
        (-1.34, 0.47, 1.48),
        0.035,
        0.62,
        mats["steel"],
        collection,
        vertices=8,
        parent=antenna_root,
        bevel=0.006,
    )
    create_cone(
        "RR_Rover_Component_AntennaModule_Dish_LowPoly",
        (-1.34, 0.47, 1.85),
        0.20,
        0.060,
        0.17,
        mats["warm_gray"],
        collection,
        vertices=8,
        parent=antenna_root,
        bevel=0.006,
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_AntennaModule_GrabPoint",
            (-1.34, 0.47, 1.52),
            collection,
            parent=antenna_root,
            display_type="SPHERE",
            display_size=0.12,
        ),
        interaction_role="component_grab_point",
        component_id="antenna_module",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_AntennaModule_UsePoint",
            (-1.34, 0.47, 1.23),
            collection,
            parent=antenna_root,
            display_type="ARROWS",
            display_size=0.13,
        ),
        interaction_role="repair_use_point",
        component_id="antenna_module",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_AntennaModule_SnapTarget",
            (-1.34, 0.47, 1.17),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id="antenna_module",
    )

    # A new repair point on the front sensor bar.
    sensor_root = set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontSensorArray_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.16,
        ),
        interaction_role="removable_component",
        component_id="front_sensor_array",
    )
    create_cube(
        "RR_Rover_Component_FrontSensorArray_Bar",
        (1.79, 0.0, 1.02),
        (0.036, 0.70, 0.055),
        mats["cyan"],
        collection,
        parent=sensor_root,
        bevel=0.004,
    )
    create_cube(
        "RR_Rover_Component_FrontSensorArray_Damaged_Module",
        (1.82, 0.24, 1.03),
        (0.030, 0.16, 0.085),
        mats["red"],
        collection,
        parent=sensor_root,
        bevel=0.004,
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontSensorArray_UsePoint",
            (1.86, 0.24, 1.03),
            collection,
            parent=sensor_root,
            display_type="ARROWS",
            display_size=0.13,
        ),
        interaction_role="repair_use_point",
        component_id="front_sensor_array",
    )

    return root


# ============================================================
# Export / preview
# ============================================================


def collect_hierarchy(root: Object) -> list[Object]:
    items = [root]
    for child in root.children:
        items.extend(collect_hierarchy(child))
    return items


def export_root(root: Object, filepath: Path) -> None:
    previous_location = root.location.copy()
    root.location = (0.0, 0.0, 0.0)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in collect_hierarchy(root):
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root

    export_kwargs = {
        "filepath": str(filepath),
        "export_format": "GLB",
        "use_selection": True,
        "export_yup": True,
        "export_extras": True,
    }
    try:
        bpy.ops.export_scene.gltf(**export_kwargs, export_apply=True)
    except TypeError:
        bpy.ops.export_scene.gltf(**export_kwargs)

    root.location = previous_location


def add_preview_lighting(mats: dict[str, Material]) -> None:
    preview = make_collection("RR_Preview_Only")
    create_cube("RR_Preview_Garage_Floor_Swatch", (0.0, 0.0, -0.035), (7.0, 2.8, 0.035), mats["warm_gray"], preview)

    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.0, 4.8))
    area = bpy.context.object
    area.name = "RR_Preview_Large_Softbox"
    area.data.energy = 650
    area.data.size = 5.8
    move_to_collection(area, preview)

    bpy.ops.object.light_add(type="POINT", location=(0.0, 1.8, 2.4))
    point = bpy.context.object
    point.name = "RR_Preview_Cyan_Service_Light"
    point.data.energy = 120
    point.data.color = (0.08, 0.80, 1.0)
    move_to_collection(point, preview)

    bpy.ops.object.camera_add(location=(4.7, -5.0, 2.8), rotation=(math.radians(62), 0.0, math.radians(43)))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.object.name = "RR_Preview_Camera"
    move_to_collection(bpy.context.object, preview)


def main() -> None:
    ensure_output_dirs()
    clean_scene()

    bpy.context.scene.unit_settings.system = "METRIC"
    try:
        bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        bpy.context.scene.render.engine = "BLENDER_EEVEE"

    mats = make_materials()
    rover_root = build_complex_rover(mats, (0.0, 0.0, 0.0))
    add_preview_lighting(mats)

    export_root(rover_root, MODEL_DIR / "rover_complex.glb")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))

    print(f"Saved Blender source to: {BLEND_FILE}")
    print(f"Exported rover GLB to: {MODEL_DIR / 'rover_complex.glb'}")


if __name__ == "__main__":
    main()
