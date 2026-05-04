"""
Rover Ready Blender asset generator.

Run from the project root (`.`) with Blender:

    blender --background --python ./scripts/blender/create_rover_ready_assets.py

The script creates three custom low-poly assets for the single-bay rover repair
project and exports them as individual GLB files for later Three.js GLTFLoader
use. It also saves one combined .blend scene as source evidence for submission.
"""

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

ROT_X_90 = (math.pi / 2.0, 0.0, 0.0)
ROT_Y_90 = (0.0, math.pi / 2.0, 0.0)


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
        "sand": make_material("RR_muted_sand_hull", (0.55, 0.50, 0.40, 1.0)),
        "warm_gray": make_material("RR_warm_gray_panels", (0.33, 0.35, 0.35, 1.0)),
        "dark": make_material("RR_dark_gunmetal", (0.07, 0.08, 0.09, 1.0), metallic=0.25),
        "steel": make_material("RR_brushed_steel", (0.43, 0.45, 0.45, 1.0), metallic=0.35),
        "rubber": make_material("RR_flat_black_rubber", (0.015, 0.014, 0.013, 1.0)),
        "orange": make_material("RR_safety_orange", (1.0, 0.36, 0.08, 1.0)),
        "yellow": make_material("RR_warning_yellow", (1.0, 0.73, 0.09, 1.0)),
        "red": make_material("RR_damage_red", (0.88, 0.08, 0.04, 1.0)),
        "glass": make_material("RR_smoked_blue_glass", (0.04, 0.12, 0.16, 0.82), roughness=0.28),
        "cyan": make_material(
            "RR_cyan_indicator_light",
            (0.03, 0.85, 1.0, 1.0),
            emission=(0.03, 0.85, 1.0, 1.0),
            emission_strength=1.8,
        ),
        "white_light": make_material(
            "RR_soft_white_light",
            (0.95, 0.95, 0.82, 1.0),
            emission=(0.95, 0.95, 0.82, 1.0),
            emission_strength=1.2,
        ),
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


def add_bevel(obj: Object, width: float) -> None:
    if width <= 0:
        return
    bevel = obj.modifiers.new("single_segment_bevel", "BEVEL")
    bevel.width = width
    bevel.segments = 1
    bevel.profile = 0.5

    normals = obj.modifiers.new("weighted_corner_normals", "WEIGHTED_NORMAL")
    normals.keep_sharp = True


def assign_material(obj: Object, mat: Material | None) -> None:
    if mat is not None:
        obj.data.materials.append(mat)


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
    add_bevel(obj, bevel)
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
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
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
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    return create_mesh_object(name, verts, faces, loc, mat, collection, parent=parent, bevel=bevel)


def add_panel_bolts(
    prefix: str,
    centers: list[tuple[float, float, float]],
    mat: Material,
    collection: Collection,
    parent: Object | None,
    *,
    axis: str = "y",
) -> None:
    rotation = ROT_X_90 if axis == "y" else ROT_Y_90
    for index, loc in enumerate(centers, start=1):
        create_cylinder(
            f"{prefix}_Bolt_{index:02d}",
            loc,
            0.025,
            0.018,
            mat,
            collection,
            vertices=8,
            parent=parent,
            rotation=rotation,
        )


def add_wheel_treads(
    prefix: str,
    wheel_center: tuple[float, float, float],
    side_sign: int,
    mats: dict[str, Material],
    collection: Collection,
    parent: Object | None,
) -> None:
    cx, cy, cz = wheel_center
    radius = 0.325
    for index in range(10):
        angle = (math.tau / 10.0) * index
        x = cx + math.cos(angle) * radius
        z = cz + math.sin(angle) * radius
        create_cube(
            f"{prefix}_Tread_{index:02d}",
            (x, cy + side_sign * 0.01, z),
            (0.10, 0.30, 0.045),
            mats["rubber"],
            collection,
            parent=parent,
            rotation=(0.0, -angle, 0.0),
            bevel=0.008,
        )


def build_rover(mats: dict[str, Material], preview_offset: tuple[float, float, float]) -> Object:
    collection = make_collection("RR_Asset_Rover")
    root = create_empty(
        "RR_Rover_Root",
        preview_offset,
        collection,
        display_type="CUBE",
        display_size=0.35,
    )

    create_cube(
        "RR_Rover_Underbody_Frame",
        (0.0, 0.0, 0.52),
        (2.68, 1.40, 0.18),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.035,
    )
    create_cube(
        "RR_Rover_Main_Chassis",
        (0.0, 0.0, 0.77),
        (2.35, 1.18, 0.38),
        mats["sand"],
        collection,
        parent=root,
        bevel=0.055,
    )
    create_sloped_box(
        "RR_Rover_Sloped_Front_Hood",
        (0.78, 0.0, 1.03),
        (0.78, 1.02, 0.46),
        mats["warm_gray"],
        collection,
        parent=root,
        front_top_z=-0.06,
        back_top_z=0.23,
        bevel=0.035,
    )
    create_tapered_box(
        "RR_Rover_LowPoly_Cockpit",
        (-0.13, 0.0, 1.19),
        (0.88, 0.86),
        (0.54, 0.56),
        0.42,
        mats["glass"],
        collection,
        parent=root,
        bevel=0.025,
    )
    create_cube(
        "RR_Rover_Rear_Service_Deck",
        (-0.78, 0.0, 1.04),
        (0.82, 0.98, 0.14),
        mats["warm_gray"],
        collection,
        parent=root,
        bevel=0.025,
    )

    wheel_x_positions = [-0.93, 0.0, 0.93]
    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        y = side_sign * 0.78
        for wheel_index, x in enumerate(wheel_x_positions, start=1):
            prefix = f"RR_Rover_{side_name}_Wheel_{wheel_index}"
            create_cylinder(
                f"{prefix}_Rubber_Tire",
                (x, y, 0.36),
                0.32,
                0.28,
                mats["rubber"],
                collection,
                vertices=12,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.015,
            )
            create_cylinder(
                f"{prefix}_Orange_Hub",
                (x, y, 0.36),
                0.16,
                0.31,
                mats["orange"],
                collection,
                vertices=8,
                parent=root,
                rotation=ROT_X_90,
                bevel=0.01,
            )
            add_wheel_treads(prefix, (x, y, 0.36), side_sign, mats, collection, root)
            create_cube(
                f"RR_Rover_{side_name}_Suspension_Arm_{wheel_index}",
                (x, side_sign * 0.54, 0.58),
                (0.16, 0.42, 0.075),
                mats["steel"],
                collection,
                parent=root,
                rotation=(0.0, 0.0, side_sign * 0.08),
                bevel=0.012,
            )

    create_cube(
        "RR_Rover_Front_Bumper",
        (1.32, 0.0, 0.64),
        (0.12, 1.12, 0.16),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.02,
    )
    create_cube(
        "RR_Rover_Rear_Bumper",
        (-1.32, 0.0, 0.64),
        (0.12, 1.12, 0.16),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.02,
    )

    for side_y in [-0.33, 0.33]:
        create_cylinder(
            f"RR_Rover_Headlamp_{'Left' if side_y < 0 else 'Right'}",
            (1.39, side_y, 0.83),
            0.075,
            0.035,
            mats["white_light"],
            collection,
            vertices=8,
            parent=root,
            rotation=ROT_Y_90,
            bevel=0.004,
        )
        create_cube(
            f"RR_Rover_Rear_Cyan_Status_{'Left' if side_y < 0 else 'Right'}",
            (-1.39, side_y, 0.84),
            (0.035, 0.12, 0.055),
            mats["cyan"],
            collection,
            parent=root,
            bevel=0.006,
        )

    dock_root = set_custom_props(
        create_empty(
            "RR_Rover_PowerCellDock_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.22,
        ),
        interaction_role="power_cell_receiver",
        accepts="RR_PowerCell_Root",
    )
    create_cube(
        "RR_Rover_PowerCellDock_Outer_Bezeled_Frame",
        (-0.72, 0.0, 1.135),
        (1.04, 0.58, 0.080),
        mats["dark"],
        collection,
        parent=dock_root,
        bevel=0.025,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Rectangular_Recess",
        (-0.72, 0.0, 1.192),
        (0.90, 0.44, 0.045),
        mats["rubber"],
        collection,
        parent=dock_root,
        bevel=0.018,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Battery_Seat",
        (-0.72, 0.0, 1.230),
        (0.82, 0.38, 0.032),
        mats["warm_gray"],
        collection,
        parent=dock_root,
        bevel=0.010,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Left_Guide_Rail",
        (-0.72, -0.255, 1.305),
        (0.94, 0.055, 0.120),
        mats["yellow"],
        collection,
        parent=dock_root,
        bevel=0.012,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Right_Guide_Rail",
        (-0.72, 0.255, 1.305),
        (0.94, 0.055, 0.120),
        mats["yellow"],
        collection,
        parent=dock_root,
        bevel=0.012,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Terminal_Block",
        (-1.20, 0.0, 1.315),
        (0.070, 0.38, 0.165),
        mats["steel"],
        collection,
        parent=dock_root,
        bevel=0.012,
    )
    create_cylinder(
        "RR_Rover_PowerCellDock_Positive_Cyan_Contact",
        (-1.245, -0.085, 1.335),
        0.050,
        0.030,
        mats["cyan"],
        collection,
        vertices=8,
        parent=dock_root,
        rotation=ROT_Y_90,
        bevel=0.004,
    )
    create_cylinder(
        "RR_Rover_PowerCellDock_Negative_Steel_Contact",
        (-1.245, 0.085, 1.335),
        0.050,
        0.030,
        mats["dark"],
        collection,
        vertices=8,
        parent=dock_root,
        rotation=ROT_Y_90,
        bevel=0.004,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Left_Latch",
        (-0.30, -0.165, 1.390),
        (0.090, 0.040, 0.135),
        mats["orange"],
        collection,
        parent=dock_root,
        bevel=0.010,
    )
    create_cube(
        "RR_Rover_PowerCellDock_Right_Latch",
        (-0.30, 0.165, 1.390),
        (0.090, 0.040, 0.135),
        mats["orange"],
        collection,
        parent=dock_root,
        bevel=0.010,
    )
    set_custom_props(
        create_empty(
            "RR_Rover_PowerCell_SnapTarget",
            (-0.72, 0.0, 1.350),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.25,
        ),
        interaction_role="socket_snap_target",
        accepts="RR_PowerCell_InsertPoint",
    )

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
    create_cube(
        "RR_Rover_Component_SideAccessPanel_Panel",
        (0.26, -0.622, 0.88),
        (0.58, 0.045, 0.27),
        mats["warm_gray"],
        collection,
        parent=side_panel_root,
        bevel=0.014,
    )
    create_cube(
        "RR_Rover_Component_SideAccessPanel_Damaged_Seam",
        (0.26, -0.650, 0.89),
        (0.42, 0.018, 0.045),
        mats["red"],
        collection,
        parent=side_panel_root,
        rotation=(0.0, 0.0, 0.18),
        bevel=0.004,
    )
    add_panel_bolts(
        "RR_Rover_Component_SideAccessPanel",
        [
            (0.02, -0.655, 0.76),
            (0.50, -0.655, 0.76),
            (0.02, -0.655, 1.00),
            (0.50, -0.655, 1.00),
        ],
        mats["steel"],
        collection,
        side_panel_root,
        axis="y",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_SideAccessPanel_GrabPoint",
            (0.26, -0.70, 0.90),
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
            (0.26, -0.70, 0.88),
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
            (0.26, -0.622, 0.88),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id="side_access_panel",
    )

    wheel_mount_root = set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontRightWheelMount_Root",
            (0.0, 0.0, 0.0),
            collection,
            parent=root,
            display_type="CUBE",
            display_size=0.18,
        ),
        interaction_role="removable_component",
        component_id="front_right_wheel_mount",
    )
    create_cube(
        "RR_Rover_Component_FrontRightWheelMount_Bracket",
        (0.93, 0.49, 0.62),
        (0.34, 0.090, 0.18),
        mats["steel"],
        collection,
        parent=wheel_mount_root,
        bevel=0.014,
    )
    create_cube(
        "RR_Rover_Component_FrontRightWheelMount_Damaged_Cap",
        (0.93, 0.545, 0.62),
        (0.26, 0.030, 0.12),
        mats["red"],
        collection,
        parent=wheel_mount_root,
        bevel=0.008,
    )
    add_panel_bolts(
        "RR_Rover_Component_FrontRightWheelMount",
        [
            (0.80, 0.595, 0.56),
            (1.06, 0.595, 0.56),
            (0.80, 0.595, 0.68),
            (1.06, 0.595, 0.68),
        ],
        mats["dark"],
        collection,
        wheel_mount_root,
        axis="y",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontRightWheelMount_GrabPoint",
            (0.93, 0.66, 0.62),
            collection,
            parent=wheel_mount_root,
            display_type="SPHERE",
            display_size=0.12,
        ),
        interaction_role="component_grab_point",
        component_id="front_right_wheel_mount",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontRightWheelMount_UsePoint",
            (0.93, 0.65, 0.62),
            collection,
            parent=wheel_mount_root,
            display_type="ARROWS",
            display_size=0.13,
        ),
        interaction_role="repair_use_point",
        component_id="front_right_wheel_mount",
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_FrontRightWheelMount_SnapTarget",
            (0.93, 0.49, 0.62),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id="front_right_wheel_mount",
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
        (-0.95, 0.42, 1.14),
        (0.28, 0.24, 0.060),
        mats["steel"],
        collection,
        parent=antenna_root,
        bevel=0.012,
    )
    create_cube(
        "RR_Rover_Component_AntennaModule_Damaged_Collar",
        (-0.95, 0.42, 1.205),
        (0.18, 0.16, 0.045),
        mats["red"],
        collection,
        parent=antenna_root,
        bevel=0.008,
    )
    create_cylinder(
        "RR_Rover_Component_AntennaModule_Mast",
        (-0.95, 0.42, 1.43),
        0.035,
        0.58,
        mats["steel"],
        collection,
        vertices=8,
        parent=antenna_root,
        bevel=0.006,
    )
    create_cone(
        "RR_Rover_Component_AntennaModule_Dish_LowPoly",
        (-0.95, 0.42, 1.78),
        0.18,
        0.055,
        0.16,
        mats["warm_gray"],
        collection,
        vertices=8,
        parent=antenna_root,
        rotation=(0.0, 0.0, 0.0),
        bevel=0.006,
    )
    set_custom_props(
        create_empty(
            "RR_Rover_Component_AntennaModule_GrabPoint",
            (-0.95, 0.42, 1.48),
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
            (-0.95, 0.42, 1.20),
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
            (-0.95, 0.42, 1.14),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="component_snap_target",
        component_id="antenna_module",
    )

    for index, x in enumerate([-0.38, -0.18, 0.02, 0.22], start=1):
        create_cube(
            f"RR_Rover_TopVent_Slat_{index}",
            (x, 0.43, 1.06),
            (0.12, 0.040, 0.025),
            mats["dark"],
            collection,
            parent=root,
        )

    return root


def build_power_cell(mats: dict[str, Material], preview_offset: tuple[float, float, float]) -> Object:
    collection = make_collection("RR_Asset_PowerCell")
    root = create_empty(
        "RR_PowerCell_Root",
        preview_offset,
        collection,
        display_type="CUBE",
        display_size=0.24,
    )

    create_cube(
        "RR_PowerCell_Beveled_Rectangular_Battery_Body",
        (0.0, 0.0, 0.38),
        (0.86, 0.40, 0.34),
        mats["dark"],
        collection,
        parent=root,
        bevel=0.055,
    )
    create_cube(
        "RR_PowerCell_Top_Label_Decal",
        (0.04, 0.0, 0.575),
        (0.58, 0.30, 0.018),
        mats["sand"],
        collection,
        parent=root,
        bevel=0.006,
    )
    create_cube(
        "RR_PowerCell_LightningBolt_UpperStroke",
        (-0.05, 0.0, 0.592),
        (0.070, 0.035, 0.020),
        mats["yellow"],
        collection,
        parent=root,
        rotation=(0.0, 0.0, -0.42),
        bevel=0.003,
    )
    create_cube(
        "RR_PowerCell_LightningBolt_MiddleStroke",
        (0.02, 0.0, 0.594),
        (0.105, 0.035, 0.020),
        mats["yellow"],
        collection,
        parent=root,
        rotation=(0.0, 0.0, 0.44),
        bevel=0.003,
    )
    create_cube(
        "RR_PowerCell_LightningBolt_LowerStroke",
        (0.075, 0.0, 0.592),
        (0.080, 0.035, 0.020),
        mats["yellow"],
        collection,
        parent=root,
        rotation=(0.0, 0.0, -0.42),
        bevel=0.003,
    )
    create_cube(
        "RR_PowerCell_Orange_Label_Band",
        (0.27, 0.0, 0.595),
        (0.040, 0.30, 0.020),
        mats["orange"],
        collection,
        parent=root,
        bevel=0.003,
    )
    create_cube(
        "RR_PowerCell_Front_Contact_Pad_Positive",
        (-0.455, -0.085, 0.415),
        (0.018, 0.080, 0.055),
        mats["cyan"],
        collection,
        parent=root,
        bevel=0.003,
    )
    create_cube(
        "RR_PowerCell_Front_Contact_Pad_Negative",
        (-0.455, 0.085, 0.415),
        (0.018, 0.080, 0.055),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.003,
    )
    set_custom_props(
        create_empty(
            "RR_PowerCell_InsertPoint",
            (-0.510, 0.0, 0.415),
            collection,
            parent=root,
            display_type="ARROWS",
            display_size=0.16,
        ),
        interaction_role="battery_insert_point",
        mates_with="RR_Rover_PowerCell_SnapTarget",
    )
    set_custom_props(
        create_empty(
            "RR_PowerCell_GripPoint",
            (0.0, 0.0, 0.60),
            collection,
            parent=root,
            display_type="SPHERE",
            display_size=0.14,
        ),
        interaction_role="battery_grab_point",
        component_id="power_cell",
    )

    return root


def build_repair_tool(mats: dict[str, Material], preview_offset: tuple[float, float, float]) -> Object:
    collection = make_collection("RR_Asset_RepairTool")
    root = create_empty(
        "RR_RepairTool_Root",
        preview_offset,
        collection,
        display_type="CUBE",
        display_size=0.24,
    )

    create_cube(
        "RR_RepairTool_Angled_Grip",
        (-0.26, 0.0, 0.36),
        (0.17, 0.23, 0.52),
        mats["dark"],
        collection,
        parent=root,
        rotation=(0.0, -0.28, 0.0),
        bevel=0.030,
    )
    create_cube(
        "RR_RepairTool_Orange_Grip_Base",
        (-0.34, 0.0, 0.12),
        (0.20, 0.25, 0.075),
        mats["orange"],
        collection,
        parent=root,
        rotation=(0.0, -0.28, 0.0),
        bevel=0.018,
    )
    create_cube(
        "RR_RepairTool_Main_Motor_Housing",
        (0.05, 0.0, 0.72),
        (0.62, 0.26, 0.24),
        mats["warm_gray"],
        collection,
        parent=root,
        bevel=0.040,
    )
    create_tapered_box(
        "RR_RepairTool_Top_Control_Shroud",
        (0.03, 0.0, 0.90),
        (0.48, 0.23),
        (0.36, 0.17),
        0.16,
        mats["sand"],
        collection,
        parent=root,
        bevel=0.015,
    )
    create_cube(
        "RR_RepairTool_Trigger",
        (-0.12, 0.0, 0.52),
        (0.075, 0.09, 0.18),
        mats["orange"],
        collection,
        parent=root,
        bevel=0.012,
    )
    create_cube(
        "RR_RepairTool_Trigger_Guard_Back",
        (-0.21, 0.0, 0.54),
        (0.045, 0.16, 0.25),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.008,
    )
    create_cube(
        "RR_RepairTool_Trigger_Guard_Front",
        (0.03, 0.0, 0.56),
        (0.045, 0.16, 0.20),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.008,
    )
    create_cube(
        "RR_RepairTool_Trigger_Guard_Bottom",
        (-0.09, 0.0, 0.43),
        (0.26, 0.16, 0.045),
        mats["steel"],
        collection,
        parent=root,
        bevel=0.008,
    )

    create_cylinder(
        "RR_RepairTool_Barrel",
        (0.55, 0.0, 0.74),
        0.095,
        0.48,
        mats["steel"],
        collection,
        vertices=10,
        parent=root,
        rotation=ROT_Y_90,
        bevel=0.010,
    )
    create_cylinder(
        "RR_RepairTool_Cyan_Status_Ring",
        (0.33, 0.0, 0.74),
        0.125,
        0.050,
        mats["cyan"],
        collection,
        vertices=10,
        parent=root,
        rotation=ROT_Y_90,
        bevel=0.004,
    )
    create_cone(
        "RR_RepairTool_Focused_Nozzle",
        (0.86, 0.0, 0.74),
        0.13,
        0.055,
        0.25,
        mats["dark"],
        collection,
        vertices=10,
        parent=root,
        rotation=ROT_Y_90,
        bevel=0.008,
    )
    create_cylinder(
        "RR_RepairTool_White_Tip_Light",
        (0.99, 0.0, 0.74),
        0.052,
        0.026,
        mats["white_light"],
        collection,
        vertices=8,
        parent=root,
        rotation=ROT_Y_90,
        bevel=0.003,
    )

    for side_sign, side_name in [(-1, "Left"), (1, "Right")]:
        create_cube(
            f"RR_RepairTool_{side_name}_Mode_Button",
            (0.05, side_sign * 0.15, 0.76),
            (0.16, 0.025, 0.052),
            mats["yellow"] if side_sign < 0 else mats["cyan"],
            collection,
            parent=root,
            bevel=0.004,
        )
        create_cube(
            f"RR_RepairTool_{side_name}_Cooling_Vent",
            (-0.08, side_sign * 0.151, 0.67),
            (0.22, 0.018, 0.030),
            mats["dark"],
            collection,
            parent=root,
        )

    create_cylinder(
        "RR_RepairTool_Back_Cable_Port",
        (-0.32, 0.0, 0.76),
        0.075,
        0.070,
        mats["dark"],
        collection,
        vertices=8,
        parent=root,
        rotation=ROT_Y_90,
        bevel=0.006,
    )
    create_empty(
        "RR_RepairTool_GripPoint",
        (-0.26, 0.0, 0.38),
        collection,
        parent=root,
        display_type="SPHERE",
        display_size=0.14,
    )
    create_empty(
        "RR_RepairTool_TipUsePoint",
        (1.04, 0.0, 0.74),
        collection,
        parent=root,
        display_type="ARROWS",
        display_size=0.15,
    )

    return root


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
    create_cube(
        "RR_Preview_Garage_Floor_Swatch",
        (0.0, 0.0, -0.035),
        (7.0, 2.4, 0.035),
        mats["warm_gray"],
        preview,
        bevel=0.0,
    )

    bpy.ops.object.light_add(type="AREA", location=(0.0, -4.0, 4.5))
    area = bpy.context.object
    area.name = "RR_Preview_Large_Softbox"
    area.data.energy = 500
    area.data.size = 5
    move_to_collection(area, preview)

    bpy.ops.object.light_add(type="POINT", location=(0.0, 1.6, 2.2))
    point = bpy.context.object
    point.name = "RR_Preview_Cyan_Service_Light"
    point.data.energy = 90
    point.data.color = (0.08, 0.80, 1.0)
    move_to_collection(point, preview)

    bpy.ops.object.camera_add(location=(4.2, -4.4, 2.5), rotation=(math.radians(62), 0.0, math.radians(43)))
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
    rover_root = build_rover(mats, (0.0, 0.0, 0.0))
    power_cell_root = build_power_cell(mats, (-2.3, 0.0, 0.0))
    repair_tool_root = build_repair_tool(mats, (2.3, 0.0, 0.0))
    add_preview_lighting(mats)

    export_root(rover_root, MODEL_DIR / "rover.glb")
    export_root(power_cell_root, MODEL_DIR / "power_cell.glb")
    export_root(repair_tool_root, MODEL_DIR / "repair_tool.glb")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_DIR / "rover_ready_assets.blend"))
    print(f"Saved Blender source to: {BLEND_DIR / 'rover_ready_assets.blend'}")
    print(f"Exported GLB files to: {MODEL_DIR}")


if __name__ == "__main__":
    main()
