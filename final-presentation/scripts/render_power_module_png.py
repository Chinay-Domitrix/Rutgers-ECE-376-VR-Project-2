"""
Render the Rover Ready power module as a transparent three-quarter PNG.

Run from the repository root with Blender:

    blender --background --python final-presentation/scripts/render_power_module_png.py

Optional custom output path:

    blender --background --python final-presentation/scripts/render_power_module_png.py -- path/to/output.png
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any

bpy: Any = import_module("bpy")
mathutils: Any = import_module("mathutils")
Vector = mathutils.Vector

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO_ROOT / "final" / "assets" / "models" / "power_cell.glb"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "final-presentation" / "assets" / "power_module.png"
ROOT_NAME = "PowerModule_RenderRoot"


def get_output_path() -> Path:
    if "--" not in sys.argv:
        return DEFAULT_OUTPUT_PATH

    args = sys.argv[sys.argv.index("--") + 1 :]
    return Path(args[0]).resolve() if args else DEFAULT_OUTPUT_PATH


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    for block in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.lights,
        bpy.data.cameras,
    ):
        for item in (*block,):
            if item.users == 0:
                block.remove(item)


def import_power_module() -> Any:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing power module model: {MODEL_PATH}")

    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(MODEL_PATH))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    if not imported:
        raise RuntimeError(f"No objects were imported from {MODEL_PATH}")

    root = bpy.data.objects.new(ROOT_NAME, None)
    bpy.context.scene.collection.objects.link(root)

    imported_set = set(imported)
    top_level = [obj for obj in imported if obj.parent not in imported_set]
    for obj in top_level:
        world_matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
        obj.matrix_world = world_matrix

    center_on_origin(imported)
    root.rotation_euler = (0.0, 0.0, 0.0)
    return root


def center_on_origin(objects: list[Any]) -> None:
    box = get_world_box(objects)
    center = box.get_center()
    for obj in objects:
        if obj.parent is None or obj.parent.name == ROOT_NAME:
            obj.location -= center


def get_world_box(objects: list[Any]) -> Any:
    min_corner = Vector((float("inf"), float("inf"), float("inf")))
    max_corner = Vector((float("-inf"), float("-inf"), float("-inf")))

    bpy.context.view_layer.update()
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            min_corner.x = min(min_corner.x, world.x)
            min_corner.y = min(min_corner.y, world.y)
            min_corner.z = min(min_corner.z, world.z)
            max_corner.x = max(max_corner.x, world.x)
            max_corner.y = max(max_corner.y, world.y)
            max_corner.z = max(max_corner.z, world.z)

    if min_corner.x == float("inf"):
        raise RuntimeError("Imported power module has no mesh bounds.")

    return SimpleBox(min_corner, max_corner)


class SimpleBox:
    def __init__(self, min_corner: Any, max_corner: Any) -> None:
        self.min = min_corner
        self.max = max_corner

    def get_center(self) -> Any:
        return (self.min + self.max) * 0.5

    def get_size(self) -> Any:
        return self.max - self.min


def add_lighting() -> None:
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.color = (0.03, 0.035, 0.04)

    key_data = bpy.data.lights.new("PowerModule_KeyLight", type="AREA")
    key_data.energy = 460
    key_data.size = 3.4
    key = bpy.data.objects.new("PowerModule_KeyLight", key_data)
    key.location = (0.7, -3.2, 2.8)
    bpy.context.scene.collection.objects.link(key)

    fill_data = bpy.data.lights.new("PowerModule_FillLight", type="POINT")
    fill_data.energy = 70
    fill_data.shadow_soft_size = 4.0
    fill = bpy.data.objects.new("PowerModule_FillLight", fill_data)
    fill.location = (-2.6, 2.4, 1.7)
    bpy.context.scene.collection.objects.link(fill)


def add_camera(objects: list[Any]) -> None:
    bpy.context.view_layer.update()
    box = get_world_box(objects)
    center = box.get_center()
    size = box.get_size()

    camera_data = bpy.data.cameras.new("PowerModule_Camera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(size.x, size.z) * 1.55
    camera_data.lens = 70

    camera = bpy.data.objects.new("PowerModule_Camera", camera_data)
    camera.location = center + Vector((-2.4, -3.0, 1.55))
    look_at(camera, center + Vector((-0.05, 0.0, 0.08)))
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera


def look_at(obj: Any, target: Any) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_render(output_path: Path) -> None:
    scene = bpy.context.scene

    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"

    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "Medium High Contrast"
    except TypeError:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.filepath = str(output_path)


def main() -> None:
    output_path = get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clean_scene()
    import_power_module()
    module_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    add_lighting()
    add_camera(module_meshes)
    configure_render(output_path)

    bpy.ops.render.render(write_still=True)
    print(f"Rendered power module PNG: {output_path}")


if __name__ == "__main__":
    main()
