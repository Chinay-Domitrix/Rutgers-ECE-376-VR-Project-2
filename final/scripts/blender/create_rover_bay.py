from importlib import import_module
import math
from typing import Any

bpy: Any = import_module("bpy")
mathutils: Any = import_module("mathutils")
Vector: Any = mathutils.Vector

# Helpers


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for col in tuple(bpy.data.collections):
        bpy.data.collections.remove(col)


def new_mat(name, color, metallic=0.0, roughness=0.7, emission=None, emission_strength=3.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_cube(name, loc, scale, mat=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    bpy.ops.object.transform_apply(scale=True)
    return obj


def add_cube_rot(name, loc, scale, mat=None, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    bpy.ops.object.transform_apply(scale=True)
    return obj


def add_cylinder(name, loc, radius, depth, mat=None, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot, vertices=8)
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link(col, obj):
    col.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)


def add_glb_point_light(name, loc, color=(1.0, 1.0, 1.0), power=120, radius=2.0, col=None):
    """Real point light that exports well to GLB viewers using glTF punctual lights."""
    bpy.ops.object.light_add(type="POINT", location=loc)
    light = bpy.context.active_object
    light.name = name
    light.data.color = color
    light.data.energy = power
    light.data.shadow_soft_size = radius
    if col:
        link(col, light)
    return light


def local_to_world(base, local, rot_z):
    """Local door coordinates to world coordinates for rotated carriage-door pieces."""
    bx, by, bz = base
    lx, ly, lz = local
    c = math.cos(rot_z)
    s = math.sin(rot_z)
    return (bx + lx * c - ly * s, by + lx * s + ly * c, bz + lz)


def add_door_cube(name, base, local, scale, rot_z, mat, col):
    obj = add_cube_rot(name, local_to_world(base, local, rot_z), scale, mat, rot=(0, 0, rot_z))
    link(col, obj)
    return obj


def tube_between(name, start, end, radius, mat, col):
    """Cylinder tube between two points, used for carriage-door diagonal braces."""
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    length = direction.length
    if length <= 0.0001:
        return None

    mid = start_v + direction * 0.5
    obj = add_cylinder(name, mid, radius, length, mat)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    link(col, obj)
    return obj


# Materials palette


def build_materials():
    return {
        "floor": new_mat("M_Floor", (0.18, 0.18, 0.20), roughness=0.85),
        "wall": new_mat("M_Wall", (0.18, 0.35, 0.70), roughness=0.90),
        "ceiling": new_mat("M_Ceiling", (0.62, 0.62, 0.60), roughness=0.95),
        "metal_dark": new_mat("M_MetalDark", (0.08, 0.10, 0.12), metallic=0.9, roughness=0.4),
        "metal_mid": new_mat("M_MetalMid", (0.25, 0.28, 0.30), metallic=0.8, roughness=0.5),
        "metal_light": new_mat("M_MetalLight", (0.55, 0.58, 0.60), metallic=0.7, roughness=0.35),
        "table_top": new_mat("M_TableTop", (0.30, 0.32, 0.34), metallic=0.6, roughness=0.4),
        "screen_bg": new_mat("M_ScreenBg", (0.02, 0.06, 0.12), roughness=1.0),
        "screen_glow": new_mat(
            "M_ScreenGlow", (0.05, 0.55, 1.00), roughness=1.0, emission=(0.05, 0.55, 1.00), emission_strength=8.0
        ),
        "screen_line": new_mat(
            "M_ScreenLine", (0.10, 0.90, 0.50), roughness=1.0, emission=(0.10, 0.90, 0.50), emission_strength=6.0
        ),
        "btn_green": new_mat(
            "M_BtnGreen", (0.05, 0.80, 0.20), roughness=0.5, emission=(0.05, 0.80, 0.20), emission_strength=5.0
        ),
        "btn_red": new_mat(
            "M_BtnRed", (0.90, 0.10, 0.08), roughness=0.5, emission=(0.90, 0.10, 0.08), emission_strength=5.0
        ),
        "btn_yellow": new_mat(
            "M_BtnYellow", (0.90, 0.75, 0.05), roughness=0.5, emission=(0.90, 0.75, 0.05), emission_strength=5.0
        ),
        "panel": new_mat("M_Panel", (0.10, 0.12, 0.15), metallic=0.5, roughness=0.6),
        "panel_trim": new_mat("M_PanelTrim", (0.40, 0.65, 0.80), metallic=0.6, roughness=0.4),
        "lift_plat": new_mat("M_LiftPlat", (0.20, 0.22, 0.25), metallic=0.7, roughness=0.5),
        "yellow_stripe": new_mat(
            "M_YellowStripe", (0.95, 0.80, 0.00), roughness=0.6, emission=(0.95, 0.80, 0.00), emission_strength=1.8
        ),
        "ceiling_light": new_mat(
            "M_CeilLight", (1.00, 0.98, 0.90), roughness=1.0, emission=(1.00, 0.98, 0.90), emission_strength=12.0
        ),
        "pipe": new_mat("M_Pipe", (0.35, 0.38, 0.40), metallic=0.8, roughness=0.45),
        "wire_orange": new_mat("M_WireOrange", (0.90, 0.40, 0.00), roughness=0.8),
        # Garage carriage door materials
        "door_main": new_mat("M_DoorMain", (0.22, 0.25, 0.28), metallic=0.55, roughness=0.55),
        "door_panel": new_mat("M_DoorPanel", (0.14, 0.16, 0.19), metallic=0.35, roughness=0.70),
        "door_trim": new_mat("M_DoorTrim", (0.48, 0.52, 0.52), metallic=0.75, roughness=0.40),
        "door_window": new_mat(
            "M_DoorWindow", (0.03, 0.16, 0.26), roughness=0.25, emission=(0.02, 0.25, 0.40), emission_strength=4.0
        ),
        "rubber": new_mat("M_RubberSeal", (0.02, 0.02, 0.02), roughness=0.95),
    }


# Room shell
# Bay dimensions:  X = 14 m wide, Y = 10 m deep, Z = 5 m tall
# Orientation:
#   Left  wall  → x = -7  (tool table side)
#   Right wall  → x = +7  (button panel side)
#   Back  wall  → y = -5  (diagnostic screen)
#   Front open  → y = +5  (entry/exit bay door)

W, D, H = 7.0, 5.0, 5.0  # half-extents


def build_front_carriage_door(materials, col):
    """Replaces Wall_Front_Sill with a segmented carriage-style garage bay door."""
    thick = 0.15
    front_y = D

    door_width = 6.2
    door_half = door_width / 2
    door_height = 3.7
    door_thick = 0.08
    leaf_w = door_width / 2
    open_angle = math.radians(0)

    # Wall returns around the garage opening, so the front wall still feels complete.
    side_return_w = (W - door_half) / 2
    left_return = add_cube(
        "Wall_Front_LeftReturn",
        (-(door_half + side_return_w), front_y, H / 2),
        (side_return_w, thick, H / 2),
        materials["wall"],
    )
    link(col, left_return)

    right_return = add_cube(
        "Wall_Front_RightReturn",
        ((door_half + side_return_w), front_y, H / 2),
        (side_return_w, thick, H / 2),
        materials["wall"],
    )
    link(col, right_return)

    header_h = (H - door_height) / 2
    header = add_cube(
        "Wall_Front_Header", (0, front_y, door_height + header_h), (W, thick, header_h), materials["wall"]
    )
    link(col, header)

    # Keep the original name in the scene, but make it a threshold/sill for the bay door.
    sill = add_cube("Wall_Front_Sill", (0, front_y + 0.02, 0.12), (door_half + 0.35, 0.16, 0.12), materials["rubber"])
    link(col, sill)

    # Metal jambs and top track.
    for side_name, x in [("Left", -door_half), ("Right", door_half)]:
        jamb = add_cube(
            f"GarageDoor_{side_name}_Jamb",
            (x, front_y + 0.03, door_height / 2),
            (0.10, 0.25, door_height / 2),
            materials["metal_dark"],
        )
        link(col, jamb)

        hinge_post = add_cube(
            f"GarageDoor_{side_name}_HingePost",
            (x, front_y + 0.16, door_height / 2),
            (0.07, 0.08, door_height / 2),
            materials["metal_light"],
        )
        link(col, hinge_post)

    top_track = add_cube(
        "GarageDoor_TopTrack",
        (0, front_y + 0.10, door_height + 0.08),
        (door_half + 0.22, 0.35, 0.1),
        materials["metal_dark"],
    )
    link(col, top_track)

    # Small exterior ramp/lip outside the door.
    ramp = add_cube(
        "GarageDoor_ExteriorRamp", (0, front_y + 0.75, 0.06), (door_half + 0.45, 0.70, 0.06), materials["metal_mid"]
    )
    link(col, ramp)

    build_carriage_leaf(
        materials,
        col,
        "Wall_Front_Sill_LeftDoor",
        hinge=(-door_half, front_y + 0.14, door_height / 2),
        leaf_w=leaf_w,
        door_height=door_height,
        door_thick=door_thick,
        rot_z=open_angle,
        side_sign=1,
    )

    build_carriage_leaf(
        materials,
        col,
        "Wall_Front_Sill_RightDoor",
        hinge=(door_half, front_y + 0.14, door_height / 2),
        leaf_w=leaf_w,
        door_height=door_height,
        door_thick=door_thick,
        rot_z=-open_angle,
        side_sign=-1,
    )


def build_carriage_leaf(materials, col, name, hinge, leaf_w, door_height, door_thick, rot_z, side_sign):
    """Build one opened carriage-door leaf with segmented panels."""
    center_local_x = side_sign * leaf_w / 2
    base = local_to_world(hinge, (center_local_x, 0, 0), rot_z)

    # Main opened door leaf.
    slab = add_cube_rot(
        name, base, (leaf_w / 2, door_thick, door_height / 2), materials["door_main"], rot=(0, 0, rot_z)
    )
    link(col, slab)

    face_y = door_thick + 0.018

    # Outer frame/stiles/rails.
    add_door_cube(
        f"{name}_TopRail",
        base,
        (0, face_y, door_height / 2 - 0.08),
        (leaf_w / 2, 0.025, 0.055),
        rot_z,
        materials["door_trim"],
        col,
    )
    add_door_cube(
        f"{name}_BottomRail",
        base,
        (0, face_y, -door_height / 2 + 0.08),
        (leaf_w / 2, 0.025, 0.055),
        rot_z,
        materials["door_trim"],
        col,
    )
    add_door_cube(
        f"{name}_OuterStile",
        base,
        (-leaf_w / 2 + 0.06, face_y, 0),
        (0.055, 0.025, door_height / 2),
        rot_z,
        materials["door_trim"],
        col,
    )
    add_door_cube(
        f"{name}_InnerStile",
        base,
        (leaf_w / 2 - 0.06, face_y, 0),
        (0.055, 0.025, door_height / 2),
        rot_z,
        materials["door_trim"],
        col,
    )

    # Segmented door panels: 2 columns x 3 rows.
    cols = 2
    rows = 3
    gap_x = 0.18
    gap_z = 0.22
    panel_w = (leaf_w - gap_x * (cols + 1)) / cols
    panel_h = (door_height - gap_z * (rows + 1)) / rows

    for c in range(cols):
        for r in range(rows):
            local_x = -leaf_w / 2 + gap_x + panel_w / 2 + c * (panel_w + gap_x)
            local_z = -door_height / 2 + gap_z + panel_h / 2 + r * (panel_h + gap_z)

            add_door_cube(
                f"{name}_Segment_{c}_{r}",
                base,
                (local_x, face_y + 0.01, local_z),
                (panel_w / 2, 0.020, panel_h / 2),
                rot_z,
                materials["door_panel"],
                col,
            )

            # Window segments on the top row.
            if r == rows - 1:
                add_door_cube(
                    f"{name}_Window_{c}",
                    base,
                    (local_x, face_y + 0.035, local_z),
                    (panel_w * 0.28, 0.012, panel_h * 0.18),
                    rot_z,
                    materials["door_window"],
                    col,
                )

    # Segment divider rails.
    for z in [-door_height / 6, door_height / 6]:
        add_door_cube(
            f"{name}_HorizontalSegmentRail_{z:.2f}",
            base,
            (0, face_y + 0.04, z),
            (leaf_w / 2, 0.020, 0.035),
            rot_z,
            materials["door_trim"],
            col,
        )

    add_door_cube(
        f"{name}_CenterVerticalStile",
        base,
        (0, face_y + 0.04, 0),
        (0.045, 0.020, door_height / 2),
        rot_z,
        materials["door_trim"],
        col,
    )

    # Carriage style diagonal braces on the face.
    x0 = -leaf_w / 2 + 0.22
    x1 = leaf_w / 2 - 0.22
    z0 = -door_height / 2 + 0.25
    z1 = door_height / 2 - 0.25
    y = face_y + 0.08

    p1 = local_to_world(base, (x0, y, z0), rot_z)
    p2 = local_to_world(base, (x1, y, z1), rot_z)
    p3 = local_to_world(base, (x1, y, z0), rot_z)
    p4 = local_to_world(base, (x0, y, z1), rot_z)
    tube_between(f"{name}_DiagonalBrace_A", p1, p2, 0.030, materials["door_trim"], col)
    tube_between(f"{name}_DiagonalBrace_B", p3, p4, 0.030, materials["door_trim"], col)

    # Hinge barrels on the jamb side.
    hx, hy, _ = hinge
    for i, z in enumerate([0.72, 1.55, 2.38, 3.22]):
        barrel = add_cylinder(
            f"{name}_HingeBarrel_{i}", (hx, hy, z), 0.055, 0.28, materials["metal_light"], rot=(0, 0, 0)
        )
        link(col, barrel)

        plate = add_cube(
            f"{name}_HingePlate_{i}",
            (hx + side_sign * 0.11, hy + 0.03, z),
            (0.12, 0.025, 0.10),
            materials["metal_dark"],
        )
        link(col, plate)

    # Door handle.
    handle_x = side_sign * leaf_w * 0.25
    h1 = local_to_world(base, (handle_x, face_y + 0.14, 0.10), rot_z)
    h2 = local_to_world(base, (handle_x, face_y + 0.14, 0.55), rot_z)
    tube_between(f"{name}_Handle", h1, h2, 0.025, materials["metal_light"], col)


def build_room(materials, col):
    thick = 0.15
    # Floor
    floor = add_cube("Floor", (0, 0, 0), (W, D, thick), materials["floor"])
    link(col, floor)
    # Ceiling
    ceiling = add_cube("Ceiling", (0, 0, H), (W, D, thick), materials["ceiling"])
    link(col, ceiling)
    # Left wall
    left_wall = add_cube("Wall_Left", (-W, 0, H / 2), (thick, D, H / 2), materials["wall"])
    link(col, left_wall)
    # Right wall
    right_wall = add_cube("Wall_Right", (W, 0, H / 2), (thick, D, H / 2), materials["wall"])
    link(col, right_wall)
    # Back wall
    back_wall = add_cube("Wall_Back", (0, -D, H / 2), (W, thick, H / 2), materials["wall"])
    link(col, back_wall)

    # Front carriage-style garage bay door.
    build_front_carriage_door(materials, col)

    # Floor markings – yellow 4-sided dashed outline showing where the rover drives/parks
    # This replaces the old loose center stripes with a clear rover target zone.
    outline_z = 0.14
    target_x_half = 2.45
    target_y_half = 1.65
    dash_len = 0.32
    dash_thick = 0.055

    # Front and back dashed outline edges, running left/right across X.
    dash_count_x = 9
    for i in range(dash_count_x):
        x = -target_x_half + 0.35 + i * ((target_x_half * 2 - 0.70) / (dash_count_x - 1))

        front_dash = add_cube(
            f"RoverTarget_FrontDash_{i}",
            (x, target_y_half, outline_z),
            (dash_len, dash_thick, 0.012),
            materials["yellow_stripe"],
        )
        link(col, front_dash)

        back_dash = add_cube(
            f"RoverTarget_BackDash_{i}",
            (x, -target_y_half, outline_z),
            (dash_len, dash_thick, 0.012),
            materials["yellow_stripe"],
        )
        link(col, back_dash)

    # Left and right dashed outline edges, running front/back across Y.
    dash_count_y = 6
    for i in range(dash_count_y):
        y = -target_y_half + 0.32 + i * ((target_y_half * 2 - 0.64) / (dash_count_y - 1))

        left_dash = add_cube(
            f"RoverTarget_LeftDash_{i}",
            (-target_x_half, y, outline_z),
            (dash_thick, dash_len, 0.012),
            materials["yellow_stripe"],
        )
        link(col, left_dash)

        right_dash = add_cube(
            f"RoverTarget_RightDash_{i}",
            (target_x_half, y, outline_z),
            (dash_thick, dash_len, 0.012),
            materials["yellow_stripe"],
        )
        link(col, right_dash)

    # Solid corner blocks make the four-sided outline read clearly.
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            corner = add_cube(
                f"RoverTarget_Corner_{sx}_{sy}",
                (sx * target_x_half, sy * target_y_half, outline_z + 0.002),
                (0.14, 0.14, 0.014),
                materials["yellow_stripe"],
            )
            link(col, corner)

    # Ceiling light strips: emissive visible bars + real GLB point lights underneath.
    for xp in [-3.5, 0, 3.5]:
        ls = add_cube(f"CeilLight_{xp}", (xp, 0, H - 0.12), (0.18, D * 0.70, 0.06), materials["ceiling_light"])
        link(col, ls)
        add_glb_point_light(
            f"GLB_CeilLight_Emitter_{xp}", (xp, 0, H - 0.75), color=(1.0, 0.96, 0.82), power=420, radius=4.0, col=col
        )

    # Overhead pipes along left wall
    for yp in [-2.0, 0.0, 2.0]:
        pipe = add_cylinder(
            f"Pipe_{yp}", (-W + 0.35, yp, H - 0.5), 0.06, 3.5, materials["pipe"], rot=(0, math.pi / 2, 0)
        )
        link(col, pipe)


# Tool & Parts Table  (left side, x ≈ -5.5)


def build_tool_table(materials, col):
    tx = -W + 1.2

    # Back rail
    rail = add_cube("Table_WallRail", (tx - 0.55, 0, 2.0), (0.06, D * 0.80, 0.06), materials["metal_dark"])
    link(col, rail)

    # Table surface
    top = add_cube("Table_Top", (tx, 0, 1.10), (0.75, D * 0.72, 0.06), materials["table_top"])
    link(col, top)

    # Legs
    for yp in [-D * 0.60, D * 0.60]:
        leg = add_cube(f"Table_Leg_{yp:.1f}", (tx, yp, 0.55), (0.08, 0.08, 0.55), materials["metal_dark"])
        link(col, leg)

    # Lower shelf
    shelf = add_cube("Table_Shelf", (tx, 0, 0.45), (0.70, D * 0.70, 0.05), materials["metal_mid"])
    link(col, shelf)

    # Pegboard on wall above table
    peg = add_cube("Pegboard", (tx - 0.65, 0, 2.35), (0.06, D * 0.75, 1.00), materials["metal_dark"])
    link(col, peg)

    # Overhead tool-light bar: emissive visible bar + real GLB point light.
    tl = add_cube("ToolLight", (tx, 0, 4.4), (0.55, D * 0.65, 0.04), materials["ceiling_light"])
    link(col, tl)
    add_glb_point_light("GLB_ToolLight_Emitter", (tx, 0, 3.8), color=(1.0, 0.96, 0.82), power=250, radius=3.0, col=col)


# Diagnostic Screen Console  (back wall centre)


def build_screen_console(materials, col):
    yback = -D + 0.22

    # Console base / desk
    base = add_cube("Screen_Base", (0, yback + 0.45, 0.65), (2.10, 0.55, 0.65), materials["panel"])
    link(col, base)

    # Monitor bezel
    bezel = add_cube("Screen_Bezel", (0, yback + 0.08, 2.20), (2.00, 0.12, 1.50), materials["metal_dark"])
    link(col, bezel)

    # Screen face (glowing)
    scr = add_cube("Screen_Face", (0, yback + 0.16, 2.20), (1.85, 0.06, 1.35), materials["screen_bg"])
    link(col, scr)

    # Side status light bar
    for i, col_key in enumerate(["btn_green", "btn_yellow", "btn_red"]):
        slb = add_cube(f"StatusBar_{i}", (2.20, yback + 0.20, 1.80 + i * 0.40), (0.06, 0.06, 0.14), materials[col_key])
        link(col, slb)

    # Keyboard/input slab
    kbd = add_cube("Screen_Keyboard", (0, yback + 0.52, 1.34), (1.40, 0.36, 0.06), materials["metal_mid"])
    link(col, kbd)

    # Speaker grilles (side pillars)
    for xp in [-1.75, 1.75]:
        spk = add_cube(f"Speaker_{xp}", (xp, yback + 0.14, 2.20), (0.16, 0.10, 1.20), materials["panel"])
        link(col, spk)

    # Wire bundle from console down to floor
    wr = add_cube("WireBundle", (0.80, yback + 0.35, 0.65), (0.06, 0.06, 0.65), materials["wire_orange"])
    link(col, wr)


# Control Button Panel  (right wall)


def build_button_panel(materials, col):
    px = W - 0.22

    # Right wall is at x = +7. The room interior is toward smaller x values.
    panel_x = px - 0.04
    face_x = panel_x - 0.18
    guard_x = face_x - 0.02
    btn_x = face_x - 0.10
    label_x = face_x - 0.035

    # Row positions: check/send aligned; call moved away so top labels do not overlap.
    check_y = 1.45
    send_y = 1.45
    call_y = -0.65

    check_label_z = 2.70
    send_label_z = 1.45
    call_label_z = 2.70

    check_button_z = 2.05
    send_button_z = 0.8
    call_button_z = 1.95

    panel = add_cube("BtnPanel_Back", (panel_x, 0.50, 2.00), (0.08, 2.20, 2.20), materials["panel"])
    link(col, panel)

    trim = add_cube("BtnPanel_Trim", (face_x, 0.50, 3.15), (0.045, 2.20, 0.06), materials["panel_trim"])
    link(col, trim)

    # ── Button: CHECK ROVER ──
    btn1_lbl = add_cube(
        "Btn_CheckLabel", (label_x, check_y, check_label_z), (0.035, 0.90, 0.28), materials["screen_line"]
    )
    link(col, btn1_lbl)

    guard1 = add_cylinder(
        "Btn_CheckGuard",
        (guard_x, check_y, check_button_z),
        0.30,
        0.08,
        materials["metal_dark"],
        rot=(0, math.pi / 2, 0),
    )
    link(col, guard1)

    btn1 = add_cylinder(
        "Btn_CheckRover", (btn_x, check_y, check_button_z), 0.22, 0.14, materials["btn_green"], rot=(0, math.pi / 2, 0)
    )
    link(col, btn1)

    # ── Button: SEND ROVER OUT ──
    btn2_lbl = add_cube("Btn_SendLabel", (label_x, send_y, send_label_z), (0.035, 0.90, 0.28), materials["screen_glow"])
    link(col, btn2_lbl)

    guard2 = add_cylinder(
        "Btn_SendGuard", (guard_x, send_y, send_button_z), 0.30, 0.08, materials["metal_dark"], rot=(0, math.pi / 2, 0)
    )
    link(col, guard2)

    btn2 = add_cylinder(
        "Btn_SendRover", (btn_x, send_y, send_button_z), 0.22, 0.14, materials["btn_yellow"], rot=(0, math.pi / 2, 0)
    )
    link(col, btn2)

    # ── Button: CALL NEW ROVER ──
    btn3_lbl = add_cube("Btn_CallLabel", (label_x, call_y, call_label_z), (0.035, 0.90, 0.28), materials["btn_red"])
    link(col, btn3_lbl)

    guard3 = add_cylinder(
        "Btn_CallGuard", (guard_x, call_y, call_button_z), 0.38, 0.08, materials["metal_dark"], rot=(0, math.pi / 2, 0)
    )
    link(col, guard3)

    btn3 = add_cylinder(
        "Btn_CallRover", (btn_x, call_y, call_button_z), 0.28, 0.16, materials["btn_red"], rot=(0, math.pi / 2, 0)
    )
    link(col, btn3)

    # Toggle switch row, lowered.
    toggle_base_z = 0.78
    toggle_knob_z = 0.93

    for i in range(4):
        y = -1.50 + i * 0.40
        tgl = add_cube(f"Toggle_{i}", (face_x - 0.04, y, toggle_base_z), (0.07, 0.05, 0.18), materials["metal_light"])
        link(col, tgl)
        tgl_knob = add_cube(
            f"ToggleKnob_{i}", (face_x - 0.11, y, toggle_knob_z), (0.08, 0.06, 0.08), materials["btn_green"]
        )
        link(col, tgl_knob)

    # Small monitor on panel, now placed ABOVE the BtnPanel_Trim.
    # Trim center z = 3.15 with thickness 0.12 total, so the screen bottom starts above it.
    mini_screen_z = 3.75
    mini_scr = add_cube(
        "MiniScreen", (face_x - 0.015, 0.50, mini_screen_z), (0.035, 2.20, 0.50), materials["screen_bg"]
    )
    link(col, mini_scr)
    mini_ui = add_cube(
        "MiniScreenUI", (face_x - 0.065, 0.50, mini_screen_z), (0.025, 2.10, 0.40), materials["screen_glow"]
    )
    link(col, mini_ui)


# Lighting


def build_lighting():
    # Main room lighting: 6 ceiling fixtures for even floor coverage.
    fixture_pos = [(-3.6, -2.2), (0.0, -2.2), (3.6, -2.2), (-3.6, 2.2), (0.0, 2.2), (3.6, 2.2)]
    for i, (xp, yp) in enumerate(fixture_pos):
        bpy.ops.object.light_add(type="AREA", location=(xp, yp, H - 0.18), rotation=(0, 0, 0))
        light = bpy.context.active_object
        light.name = f"CeilingArea_{i}"
        light.data.shape = "RECTANGLE"
        light.data.size = 0.85
        light.data.size_y = 2.35
        light.data.energy = 1400
        light.data.color = (1.0, 0.97, 0.92)

    # Large soft fill so the bottom/floor is evenly lit and shadows are not too harsh.
    bpy.ops.object.light_add(type="AREA", location=(0, 0, H - 0.28), rotation=(0, 0, 0))
    fill = bpy.context.active_object
    fill.name = "RoomFill"
    fill.data.shape = "RECTANGLE"
    fill.data.size = 6.5
    fill.data.size_y = 4.2
    fill.data.energy = 450
    fill.data.color = (1.0, 0.98, 0.95)

    # Subtle accent lights only, not strong enough to make weird hotspots.
    add_glb_point_light("GLB_Screen_Blue_Emitter", (0, -D + 1.0, 2.2), color=(0.25, 0.55, 1.0), power=55, radius=2.0)
    add_glb_point_light("GLB_ButtonPanel_Emitter", (W - 1.0, 0.5, 2.0), color=(0.35, 1.0, 0.50), power=45, radius=1.8)
    add_glb_point_light(
        "GLB_GarageDoor_Window_Emitter", (0, D - 0.25, 2.8), color=(0.35, 0.70, 1.0), power=65, radius=2.4
    )

    # Optional low-power GLB ceiling lights for viewers/export.
    for i, (xp, yp) in enumerate(fixture_pos):
        add_glb_point_light(f"GLB_Ceil_{i}", (xp, yp, H - 0.75), color=(1.0, 0.97, 0.92), power=120, radius=2.8)


# Camera


def build_camera():
    bpy.ops.object.camera_add(location=(6.5, 8.5, 3.8), rotation=(math.radians(68), 0, math.radians(145)))
    cam = bpy.context.active_object
    cam.name = "Camera_Main"
    cam.data.lens = 28
    bpy.context.scene.camera = cam


# World background


def build_world():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.02, 0.03, 1.0)
        bg.inputs["Strength"].default_value = 0.08


# Render settings (Cycles, 1080p)


def setup_render():
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.samples = 64
    scn.render.resolution_x = 1920
    scn.render.resolution_y = 1080
    scn.render.film_transparent = False


# Main


def main():
    clear_scene()
    materials = build_materials()

    room_col = collection("Room")
    table_col = collection("ToolTable")
    screen_col = collection("ScreenConsole")
    panel_col = collection("ButtonPanel")
    build_room(materials, room_col)
    build_tool_table(materials, table_col)
    build_screen_console(materials, screen_col)
    build_button_panel(materials, panel_col)
    build_lighting()
    build_camera()
    build_world()
    setup_render()

    print("✅  Rover Repair Bay scene built successfully!")
    print("   Collections: Room | ToolTable | ScreenConsole | ButtonPanel")
    print("   Front bay: Wall_Front_Sill is now a segmented carriage-style garage door.")
    print("   Lighting: emissive materials + GLB-friendly POINT lights added for model viewers.")
    print("   Press F12 to render.")


if __name__ == "__main__":
    main()
