from importlib import import_module
import math
import random
from typing import Any

bpy: Any = import_module("bpy")

W, D, H = 7.0, 5.0, 5.0  # same room dimensions as your bay
RANDOM_SEED = 22

# Keep center rover area mostly clear
CLEAR_X_HALF = 2.8
CLEAR_Y_HALF = 2.0


# ------------------------------------------------------------
# Helpers
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


def make_mat(name, color, metallic=0.0, roughness=0.8):
    mat = bpy.data.materials.get(name)
    if mat is None:
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

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_cube(name, loc, scale, mat=None, rot=(0, 0, 0), col=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale

    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
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


def is_in_clear_zone(x, y, margin=0.0):
    return (abs(x) < (CLEAR_X_HALF + margin)) and (abs(y) < (CLEAR_Y_HALF + margin))


# ------------------------------------------------------------
# Materials
# ------------------------------------------------------------


def build_detail_materials():
    return {
        "rock": make_mat("M_BayRock", (0.35, 0.14, 0.08), roughness=0.90),
        "rock_dark": make_mat("M_BayRockDark", (0.22, 0.09, 0.05), roughness=0.95),
        "crate": make_mat("M_BayCrate", (0.32, 0.22, 0.12), roughness=0.85),
        "crate_dark": make_mat("M_BayCrateDark", (0.18, 0.12, 0.07), roughness=0.90),
        "metal": make_mat("M_BayCrateMetal", (0.30, 0.33, 0.36), metallic=0.7, roughness=0.45),
        "strap": make_mat("M_BayCrateStrap", (0.08, 0.08, 0.08), roughness=0.85),
    }


# ------------------------------------------------------------
# Rocks / pebbles
# ------------------------------------------------------------


def distort_object_randomly(obj, amount_xy=0.25, amount_z=0.18):
    rng = random.Random(hash(obj.name) & 999999)
    mesh = obj.data

    for v in mesh.vertices:
        v.co.x *= 1.0 + rng.uniform(-amount_xy, amount_xy)
        v.co.y *= 1.0 + rng.uniform(-amount_xy, amount_xy)
        v.co.z *= 1.0 + rng.uniform(-amount_z, amount_z)

    mesh.update()


def add_small_rock(name, x, y, radius, mat, col):
    z = 0.155 + radius * 0.55

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=(x, y, z))

    obj = bpy.context.active_object
    obj.name = name

    obj.scale = (random.uniform(0.9, 1.45), random.uniform(0.8, 1.35), random.uniform(0.55, 1.0))

    obj.rotation_euler = (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), random.uniform(0, math.tau))

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    distort_object_randomly(obj)
    shade_smooth(obj)
    link_to_collection(obj, col)

    return obj


def random_bay_rock_material(materials, dark_chance):
    return materials["rock_dark"] if random.random() < dark_chance else materials["rock"]


def add_cluster_rocks(cx, cy, start_idx, materials, col):
    idx = start_idx
    count = random.randint(5, 10)

    for _ in range(count):
        x = cx + random.uniform(-0.45, 0.45)
        y = cy + random.uniform(-0.45, 0.45)

        if is_in_clear_zone(x, y, margin=0.4):
            continue

        radius = random.uniform(0.03, 0.11)
        mat = random_bay_rock_material(materials, 0.35)
        add_small_rock(f"Bay_Rock_{idx}", x, y, radius, mat, col)
        idx += 1

    return idx


def build_small_rocks(materials, col):
    random.seed(RANDOM_SEED)

    # Hand-placed clusters near corners/walls.
    clusters = [
        (-5.8, -3.8),
        (-5.7, 3.5),
        (5.8, -3.6),
        (5.8, 3.6),
        (0.0, 4.2),
        (-4.5, 4.0),
        (4.7, 4.0),
        (-6.0, 0.0),
        (6.0, 0.2),
    ]

    idx = 0

    for cx, cy in clusters:
        idx = add_cluster_rocks(cx, cy, idx, materials, col)

    # Extra scattered pebbles.
    for i in range(40):
        x = random.uniform(-6.2, 6.2)
        y = random.uniform(-4.3, 4.3)

        if is_in_clear_zone(x, y, margin=0.25):
            continue

        # Bias toward edges so the main rover area stays clean.
        if abs(x) < 4.0 and abs(y) < 3.0:
            continue

        radius = random.uniform(0.02, 0.07)
        mat = random_bay_rock_material(materials, 0.30)

        add_small_rock(f"Bay_Pebble_{i}", x, y, radius, mat, col)


# ------------------------------------------------------------
# Crates
# ------------------------------------------------------------


def add_crate(name, loc, size, materials, col, rot=(0, 0, 0)):
    sx, sy, sz = size
    x, y, z = loc

    body = add_cube(name, (x, y, z), (sx, sy, sz), materials["crate"], rot=rot, col=col)

    # Metal corner protectors.
    corner_offsets = [
        (-sx * 0.82, -sy * 0.82),
        (sx * 0.82, -sy * 0.82),
        (-sx * 0.82, sy * 0.82),
        (sx * 0.82, sy * 0.82),
    ]

    for i, (ox, oy) in enumerate(corner_offsets):
        add_cube(
            f"{name}_Corner_{i}", (x + ox, y + oy, z), (0.04, 0.04, sz * 0.92), materials["metal"], rot=rot, col=col
        )

    # Horizontal straps.
    add_cube(f"{name}_Strap_X", (x, y, z), (sx * 0.92, 0.025, sz * 0.94), materials["strap"], rot=rot, col=col)

    add_cube(f"{name}_Strap_Y", (x, y, z), (0.025, sy * 0.92, sz * 0.94), materials["strap"], rot=rot, col=col)

    # Lid trim.
    add_cube(
        f"{name}_LidTrim",
        (x, y, z + sz * 0.86),
        (sx * 0.94, sy * 0.94, 0.03),
        materials["crate_dark"],
        rot=rot,
        col=col,
    )

    return body


def build_corner_crates(materials, col):
    # Back-left corner stack.
    add_crate("Crate_BackLeft_0", (-5.75, -3.95, 0.28), (0.45, 0.38, 0.28), materials, col, rot=(0, 0, math.radians(8)))

    add_crate(
        "Crate_BackLeft_1", (-5.25, -3.70, 0.22), (0.32, 0.30, 0.22), materials, col, rot=(0, 0, math.radians(-12))
    )

    add_crate("Crate_BackLeft_2", (-5.65, -3.45, 0.63), (0.28, 0.26, 0.18), materials, col, rot=(0, 0, math.radians(4)))

    # Back-right corner.
    add_crate(
        "Crate_BackRight_0", (5.70, -3.95, 0.30), (0.48, 0.34, 0.30), materials, col, rot=(0, 0, math.radians(-10))
    )

    add_crate(
        "Crate_BackRight_1", (5.15, -3.60, 0.22), (0.30, 0.30, 0.22), materials, col, rot=(0, 0, math.radians(14))
    )

    # Front-left near bay wall.
    add_crate(
        "Crate_FrontLeft_0", (-5.95, 4.05, 0.24), (0.36, 0.30, 0.24), materials, col, rot=(0, 0, math.radians(-5))
    )

    add_crate(
        "Crate_FrontLeft_1", (-5.50, 3.60, 0.18), (0.24, 0.22, 0.18), materials, col, rot=(0, 0, math.radians(11))
    )

    # Front-right near bay wall.
    add_crate("Crate_FrontRight_0", (5.95, 4.00, 0.24), (0.36, 0.28, 0.24), materials, col, rot=(0, 0, math.radians(9)))

    add_crate(
        "Crate_FrontRight_1", (5.45, 3.62, 0.18), (0.24, 0.22, 0.18), materials, col, rot=(0, 0, math.radians(-14))
    )

    # Small side crate by left wall.
    add_crate("Crate_LeftWall_0", (-6.05, -0.30, 0.20), (0.28, 0.24, 0.20), materials, col, rot=(0, 0, math.radians(6)))

    # Small side crate by right wall.
    add_crate("Crate_RightWall_0", (6.05, 0.55, 0.20), (0.28, 0.24, 0.20), materials, col, rot=(0, 0, math.radians(-8)))


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main():
    random.seed(RANDOM_SEED)

    col = make_collection("BayFloorDetail")
    materials = build_detail_materials()

    build_small_rocks(materials, col)
    build_corner_crates(materials, col)

    print("✅ Bay floor detail add-on complete!")
    print("   Added small Martian rocks, pebbles, and corner crates.")
    print("   Dirt patches were removed entirely.")
    print("   Main rover parking area was kept mostly clear.")


if __name__ == "__main__":
    main()
