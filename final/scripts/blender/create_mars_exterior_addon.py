from importlib import import_module
import math
import random
from typing import Any

bpy: Any = import_module("bpy")
mathutils: Any = import_module("mathutils")
Matrix: Any = mathutils.Matrix
Vector: Any = mathutils.Vector

# ============================================================
# Mars Exterior Add-On for Rover Bay
# Run this AFTER your main rover bay script.
# It does NOT clear the scene.
# ============================================================

# Your original bay dimensions:
# X half width = 7, Y front exit = +5, Z height = 5
W, D, H = 7.0, 5.0, 5.0

# Controls
OPEN_BAY_DOORS_FOR_VIEW = False
CREATE_MARS_CAMERA = True
SET_MARS_CAMERA_ACTIVE = True
RANDOM_SEED = 42


# ------------------------------------------------------------
# Collection helpers
# ------------------------------------------------------------


def remove_collection_if_exists(name):
    col = bpy.data.collections.get(name)
    if not col:
        return

    for obj in tuple(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    bpy.data.collections.remove(col)


def make_collection(name):
    remove_collection_if_exists(name)
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link_to_collection(obj, col):
    if obj.name not in col.objects.keys():
        col.objects.link(obj)

    for old_col in tuple(obj.users_collection):
        if old_col != col:
            old_col.objects.unlink(obj)


# ------------------------------------------------------------
# Material helpers
# ------------------------------------------------------------


def make_mat(name, color, metallic=0.0, roughness=0.8, alpha=1.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (*color, alpha)

    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic

    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness

    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha

    if emission:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        try:
            mat.show_transparent_back = True
        except Exception:
            pass

    return mat


def build_mars_materials():
    return {
        "soil": make_mat("M_Mars_Red_Soil", (0.55, 0.18, 0.08), roughness=0.95),
        "soil_dark": make_mat("M_Mars_Dark_Track_Soil", (0.28, 0.08, 0.035), roughness=0.98),
        "soil_light": make_mat("M_Mars_Light_Dust", (0.85, 0.34, 0.12), roughness=1.0),
        "rock": make_mat("M_Mars_Rock", (0.33, 0.12, 0.065), roughness=0.90),
        "rock_dark": make_mat("M_Mars_Dark_Rock", (0.18, 0.07, 0.045), roughness=0.92),
        "dust": make_mat(
            "M_Mars_Dust_Haze",
            (0.95, 0.38, 0.12),
            roughness=1.0,
            alpha=0.22,
            emission=(0.95, 0.32, 0.10),
            emission_strength=0.15,
        ),
        "sky": make_mat(
            "M_Mars_Dusty_Sky", (0.62, 0.25, 0.12), roughness=1.0, emission=(0.62, 0.25, 0.12), emission_strength=0.45
        ),
        "sun": make_mat(
            "M_Mars_Low_Sun", (1.0, 0.54, 0.22), roughness=1.0, emission=(1.0, 0.45, 0.16), emission_strength=8.0
        ),
        "bay_ramp_dust": make_mat("M_Bay_Ramp_Mars_Dust", (0.68, 0.22, 0.08), roughness=0.95),
    }


# ------------------------------------------------------------
# Geometry helpers
# ------------------------------------------------------------


def add_cube(name, loc, scale, mat=None, col=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale

    if mat:
        obj.data.materials.append(mat)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if col:
        link_to_collection(obj, col)

    return obj


def shade_smooth(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass

    obj.select_set(False)


# ------------------------------------------------------------
# Terrain height function
# ------------------------------------------------------------


def mars_height(x, y):
    """
    Procedural Mars terrain.
    Keeps the area near the garage door mostly flat,
    then adds dunes, uneven ground, and shallow craters farther out.
    """
    # Smoothly increase roughness as we move away from bay door.
    distance_from_door = max(0.0, y - (D + 1.2))
    roughness_factor = min(distance_from_door / 16.0, 1.0)

    # Keep rover path flatter in the middle.
    center_path_factor = 1.0
    if abs(x) < 3.0 and y < 22.0:
        center_path_factor = 0.35

    dunes = (
        0.18 * math.sin(0.23 * x + 0.31 * y)
        + 0.11 * math.sin(0.57 * x - 0.16 * y)
        + 0.06 * math.sin(1.15 * x + 0.42 * y)
    )

    # Crater depressions.
    crater1 = -0.38 * math.exp(-(((x - 7.5) ** 2) / 16.0 + ((y - 21.0) ** 2) / 22.0))
    crater2 = -0.24 * math.exp(-(((x + 9.0) ** 2) / 25.0 + ((y - 31.0) ** 2) / 16.0))
    crater3 = -0.18 * math.exp(-(((x - 2.5) ** 2) / 8.0 + ((y - 39.0) ** 2) / 12.0))

    return 0.015 + roughness_factor * center_path_factor * (dunes + crater1 + crater2 + crater3)


# ------------------------------------------------------------
# Mars terrain mesh
# ------------------------------------------------------------


def build_mars_terrain(materials, col):
    x_min, x_max = -32.0, 32.0
    y_min, y_max = D + 0.55, 52.0

    nx = 72
    ny = 72

    verts = []
    faces = []

    for iy in range(ny):
        y = y_min + (y_max - y_min) * iy / (ny - 1)
        for ix in range(nx):
            x = x_min + (x_max - x_min) * ix / (nx - 1)
            z = mars_height(x, y)
            verts.append((x, y, z))

    for iy in range(ny - 1):
        for ix in range(nx - 1):
            a = iy * nx + ix
            b = a + 1
            c = a + nx + 1
            d = a + nx
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("Mars_Surface_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    terrain = bpy.data.objects.new("Mars_Surface_Outside_Bay", mesh)
    terrain.data.materials.append(materials["soil"])
    col.objects.link(terrain)

    shade_smooth(terrain)

    try:
        normal_mod = terrain.modifiers.new("Mars_Surface_WeightedNormals", "WEIGHTED_NORMAL")
        normal_mod.weight = 50
    except Exception:
        pass

    return terrain


# ------------------------------------------------------------
# Rover path and tire tracks
# ------------------------------------------------------------


def build_rover_path(materials, col):
    # Main dusty path leading away from the garage.
    add_cube("Mars_Rover_Exit_Path", (0, D + 8.6, 0.055), (2.55, 7.8, 0.018), materials["soil_dark"], col)

    # Two darker wheel-track strips.
    for side, x in [("Left", -1.05), ("Right", 1.05)]:
        add_cube(f"Mars_{side}_Wheel_Track_Strip", (x, D + 8.6, 0.075), (0.23, 7.7, 0.012), materials["soil_dark"], col)

        # Tread marks.
        for i in range(22):
            y = D + 1.6 + i * 0.62
            z = mars_height(x, y) + 0.09

            add_cube(
                f"Mars_{side}_Tread_{i}",
                (x, y, z),
                (0.18, 0.045, 0.012),
                materials["soil_light"],
                col,
                rot=(0, 0, math.radians(16 if side == "Left" else -16)),
            )

    # Blend material near the existing garage ramp.
    add_cube(
        "Mars_Dust_Buildup_At_Garage_Threshold",
        (0, D + 0.78, 0.115),
        (3.65, 0.55, 0.018),
        materials["bay_ramp_dust"],
        col,
    )


# ------------------------------------------------------------
# Rocks, boulders, and crater rings
# ------------------------------------------------------------


def distort_rock(obj, amount=0.32):
    rng = random.Random(hash(obj.name) & 999999)

    for v in obj.data.vertices:
        factor = 1.0 + rng.uniform(-amount, amount)
        v.co.x *= factor
        v.co.y *= 1.0 + rng.uniform(-amount, amount)
        v.co.z *= 1.0 + rng.uniform(-amount * 0.6, amount * 0.8)

    obj.data.update()


def add_rock(name, x, y, radius, materials, col, dark=False):
    z = mars_height(x, y) + radius * 0.35

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(x, y, z))

    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (random.uniform(1.0, 1.7), random.uniform(0.7, 1.25), random.uniform(0.35, 0.85))

    obj.rotation_euler = (random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25), random.uniform(0, math.tau))

    mat = materials["rock_dark"] if dark else materials["rock"]
    obj.data.materials.append(mat)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    distort_rock(obj)
    shade_smooth(obj)
    link_to_collection(obj, col)

    return obj


def add_crater_ring(name, x, y, radius, materials, col):
    z = mars_height(x, y) + 0.035

    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius, minor_radius=0.035, major_segments=64, minor_segments=8, location=(x, y, z)
    )

    obj = bpy.context.active_object
    obj.name = name
    obj.scale.z = 0.08
    obj.data.materials.append(materials["soil_dark"])

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shade_smooth(obj)
    link_to_collection(obj, col)

    return obj


def build_rocks_and_craters(materials, col):
    random.seed(RANDOM_SEED)

    rock_positions = [
        (-5.8, 8.2, 0.34),
        (5.4, 9.0, 0.28),
        (-8.2, 13.2, 0.55),
        (7.6, 15.8, 0.42),
        (-13.5, 20.4, 0.75),
        (11.5, 22.2, 0.60),
        (-4.5, 25.7, 0.33),
        (4.0, 29.5, 0.40),
        (-16.0, 34.5, 0.95),
        (15.3, 36.0, 0.85),
        (-8.5, 42.0, 0.70),
        (8.4, 44.0, 0.72),
    ]

    for i, (x, y, r) in enumerate(rock_positions):
        add_rock(f"Mars_Rock_{i}", x, y, r, materials, col, dark=(i % 3 == 0))

    # Small scattered pebbles.
    for i in range(45):
        x = random.uniform(-24, 24)
        y = random.uniform(D + 4, 48)

        # Keep the main rover path mostly clear.
        if abs(x) < 2.8 and y < 24:
            continue

        r = random.uniform(0.07, 0.20)
        add_rock(f"Mars_Pebble_{i}", x, y, r, materials, col, dark=random.random() < 0.35)

    # Visible crater rims.
    add_crater_ring("Mars_Crater_Ring_Right", 7.5, 21.0, 2.15, materials, col)
    add_crater_ring("Mars_Crater_Ring_LeftFar", -9.0, 31.0, 2.55, materials, col)
    add_crater_ring("Mars_Crater_Ring_CenterFar", 2.5, 39.0, 1.45, materials, col)


# ------------------------------------------------------------
# Horizon dunes and background
# ------------------------------------------------------------


def add_dune(name, loc, scale, mat, col):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=16, radius=1.0, location=loc)

    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shade_smooth(obj)
    link_to_collection(obj, col)

    return obj


def build_horizon(materials, col):
    dune_data = [
        ("Mars_Horizon_Dune_L1", (-21, 47, -0.9), (12, 4.5, 2.0)),
        ("Mars_Horizon_Dune_L2", (-7, 49, -0.7), (15, 5.2, 2.6)),
        ("Mars_Horizon_Dune_C", (8, 48, -0.8), (16, 5.0, 2.2)),
        ("Mars_Horizon_Dune_R", (23, 46, -0.7), (13, 4.5, 2.4)),
    ]

    for name, loc, scale in dune_data:
        add_dune(name, loc, scale, materials["soil_light"], col)

    # Large dusty sky dome.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.0, location=(0, 24, 2))

    sky = bpy.context.active_object
    sky.name = "Mars_Dusty_Sky_Dome"
    sky.scale = (58, 58, 26)
    sky.data.materials.append(materials["sky"])

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_to_collection(sky, col)

    # Low sun disk near horizon.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.15, location=(-18, 43, 8.5))

    sun_disk = bpy.context.active_object
    sun_disk.name = "Mars_Low_Sun_Disk"
    sun_disk.data.materials.append(materials["sun"])
    shade_smooth(sun_disk)
    link_to_collection(sun_disk, col)


# ------------------------------------------------------------
# Dust haze layers
# ------------------------------------------------------------


def build_dust_haze(materials, col):
    haze_layers = [
        ("Mars_Dust_Haze_Near", 0, 13, 1.15, 11.0, 0.03, 1.1),
        ("Mars_Dust_Haze_Mid", -5, 24, 1.65, 16.0, 0.03, 1.6),
        ("Mars_Dust_Haze_Far", 7, 37, 2.05, 22.0, 0.03, 2.2),
    ]

    for name, x, y, z, sx, sy, sz in haze_layers:
        add_cube(name, (x, y, z), (sx, sy, sz), materials["dust"], col)

    # Small drifting dust wisps beside rover path.
    for i, x in enumerate([-2.8, 2.9, -4.2, 4.6]):
        y = D + 4.0 + i * 2.7
        z = 0.55 + i * 0.12

        add_cube(
            f"Mars_Path_Dust_Wisp_{i}",
            (x, y, z),
            (0.85, 0.025, 0.42),
            materials["dust"],
            col,
            rot=(0, 0, math.radians(random.uniform(-12, 12))),
        )


# ------------------------------------------------------------
# Lighting
# ------------------------------------------------------------


def build_mars_lighting(col):
    # Low warm Mars sun. Gives long dramatic shadows.
    bpy.ops.object.light_add(type="SUN", location=(-12, 18, 14))
    sun = bpy.context.active_object
    sun.name = "Mars_Low_Angle_Sun"
    sun.data.energy = 2.6
    sun.data.color = (1.0, 0.62, 0.32)

    # Direction of sunlight.
    sun.rotation_euler = (math.radians(48), math.radians(0), math.radians(-34))

    try:
        sun.data.angle = math.radians(3.5)
    except Exception:
        pass

    link_to_collection(sun, col)

    # Large exterior sky fill so the terrain is visible but still dusty.
    bpy.ops.object.light_add(type="AREA", location=(0, D + 13, 9))
    fill = bpy.context.active_object
    fill.name = "Mars_Exterior_Soft_Sky_Fill"
    fill.data.energy = 360
    fill.data.size = 18
    fill.data.color = (1.0, 0.45, 0.22)
    link_to_collection(fill, col)

    # Warm light spilling into the garage doorway.
    bpy.ops.object.light_add(type="AREA", location=(0, D + 2.2, 2.7))
    door_fill = bpy.context.active_object
    door_fill.name = "Mars_Doorway_Orange_Fill"
    door_fill.data.energy = 250
    door_fill.data.size = 5.4
    door_fill.data.color = (1.0, 0.42, 0.18)
    link_to_collection(door_fill, col)

    # Strong but soft rim light near the open door.
    bpy.ops.object.light_add(type="POINT", location=(0, D + 1.0, 2.8))
    rim = bpy.context.active_object
    rim.name = "GLB_Mars_Door_Rim_Light"
    rim.data.energy = 110
    rim.data.color = (1.0, 0.40, 0.16)
    rim.data.shadow_soft_size = 4.0
    link_to_collection(rim, col)


def update_world_for_mars():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")

    if bg:
        bg.inputs["Color"].default_value = (0.33, 0.13, 0.07, 1.0)
        bg.inputs["Strength"].default_value = 0.18


# ------------------------------------------------------------
# Optional: open existing carriage doors
# ------------------------------------------------------------


def rotate_object_around_z(obj, pivot, angle):
    pivot_vec = Vector(pivot)
    transform = Matrix.Translation(pivot_vec) @ Matrix.Rotation(angle, 4, "Z") @ Matrix.Translation(-pivot_vec)

    obj.matrix_world = transform @ obj.matrix_world


def open_existing_bay_doors():
    """
    Your original script creates the carriage door with open_angle = 0.
    This add-on rotates the existing door pieces open so the Mars exterior
    is visible through the garage entrance.
    """
    door_half = 6.2 / 2
    front_y = D
    door_height = 3.7

    left_hinge = (-door_half, front_y + 0.14, door_height / 2)
    right_hinge = (door_half, front_y + 0.14, door_height / 2)

    left_angle = math.radians(68)
    right_angle = math.radians(-68)

    for obj in bpy.data.objects:
        if obj.get("mars_addon_opened"):
            continue

        if obj.name.startswith("Wall_Front_Sill_LeftDoor"):
            rotate_object_around_z(obj, left_hinge, left_angle)
            obj["mars_addon_opened"] = True

        elif obj.name.startswith("Wall_Front_Sill_RightDoor"):
            rotate_object_around_z(obj, right_hinge, right_angle)
            obj["mars_addon_opened"] = True


# ------------------------------------------------------------
# Camera
# ------------------------------------------------------------


def build_mars_camera(col):
    bpy.ops.object.camera_add(location=(9.5, 18.5, 4.6))
    cam = bpy.context.active_object
    cam.name = "Camera_Mars_Exterior_View"
    cam.data.lens = 26

    target = Vector((0, D + 1.5, 1.8))
    direction = target - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    link_to_collection(cam, col)

    if SET_MARS_CAMERA_ACTIVE:
        bpy.context.scene.camera = cam

    return cam


# ------------------------------------------------------------
# Render settings
# ------------------------------------------------------------


def setup_mars_render_settings():
    scn = bpy.context.scene

    # Keep Cycles for nicer shadows.
    scn.render.engine = "CYCLES"

    if hasattr(scn, "cycles"):
        scn.cycles.samples = max(scn.cycles.samples, 96)

    scn.render.resolution_x = 1920
    scn.render.resolution_y = 1080
    scn.render.film_transparent = False

    # Slightly more cinematic color handling.
    try:
        scn.view_settings.view_transform = "Filmic"
        scn.view_settings.look = "Medium High Contrast"
        scn.view_settings.exposure = 0.0
        scn.view_settings.gamma = 1.0
    except Exception:
        pass


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main():
    mars_col = make_collection("Mars_Exterior")

    materials = build_mars_materials()

    build_mars_terrain(materials, mars_col)
    build_rover_path(materials, mars_col)
    build_rocks_and_craters(materials, mars_col)
    build_horizon(materials, mars_col)
    build_dust_haze(materials, mars_col)
    build_mars_lighting(mars_col)
    update_world_for_mars()

    if OPEN_BAY_DOORS_FOR_VIEW:
        open_existing_bay_doors()

    if CREATE_MARS_CAMERA:
        build_mars_camera(mars_col)

    setup_mars_render_settings()

    print("✅ Mars exterior add-on complete!")
    print("   Added: procedural Martian terrain, rover tracks, rocks, craters, dusty sky, haze, and Mars lighting.")
    print("   Run this after your main rover bay script.")
    print("   Press F12 to render.")


if __name__ == "__main__":
    main()
