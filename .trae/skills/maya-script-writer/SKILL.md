---
name: "maya-script-writer"
description: "Provides templates and patterns for writing Maya Python scripts (maya.cmds) for common automation tasks. Invoke when user wants to generate Maya scripts, needs Maya Python code examples, or asks how to automate modeling/animation/rendering/file operations in Maya."
---

# Maya Script Writer

This skill provides ready-to-use Python script templates for common Maya automation tasks. It helps users write efficient, production-ready Maya scripts without starting from scratch.

## Companion Skills

| Skill Name | Purpose |
|------------|---------|
| `maya-api-doc` | Look up specific command syntax, parameters, and examples |
| `maya-control-modes` | Execute scripts via Standalone (mayapy) or Command Port |
| `maya-2025-api-doc` / `maya-2022-api-doc` / `maya-2020-api-doc` | Version-specific command documentation |

**How they work together:**
- This skill (`maya-script-writer`) helps you **write the script**
- `maya-api-doc` skills help you **look up command details**
- `maya-control-modes` skill helps you **run the script** externally
- Project's [tools/](../../../tools/) directory provides ready-to-use Command Port scripts

---

## Quick Reference: Common Operations

| Task | Key Commands |
|------|-------------|
| Create objects | `polyCube`, `polySphere`, `polyCylinder`, `circle`, `curve` |
| Transform | `move`, `rotate`, `scale`, `setAttr` (for transforms) |
| Select | `select`, `ls`, `filterExpand` |
| Edit | `polySplit`, `polyExtrude`, `polyBevel`, `delete` |
| File I/O | `file` (open/save/import/export/reference), `fileDialog` |
| Animation | `setKeyframe`, `currentTime`, `play`, `keyframe` |
| Rendering | `render`, `mayapy`, `renderSettings` |
| UI | `window`, `button`, `text`, `layout`, `showWindow` |

---

## Template: Basic Script Structure

```python
# -*- coding: utf-8 -*-
"""
Script: <script_name>
Purpose: <what this script does>
Usage:  Run in Maya Script Editor or via mayapy
"""

import maya.cmds as cmds
import maya.mel as mel


def main():
    """Main entry point."""
    # === Your code here ===
    pass


if __name__ == "__main__":
    main()
```

---

## Template: Standalone (mayapy) Script

Use for batch/automation/CI tasks without Maya GUI:

```python
# -*- coding: utf-8 -*-
import maya.standalone
maya.standalone.initialize(name="python")

import maya.cmds as cmds
import os


def main():
    # Create a simple scene
    cmds.polyCube(name="MyCube")
    cmds.polySphere(name="MySphere")
    cmds.move(5, 0, 0, "MySphere")

    # Save
    output_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "output.ma")
    cmds.file(rename=output_path)
    cmds.file(save=True, type="mayaAscii")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
    maya.standalone.uninitialize()
```

---

## Template: Command Port Script

Use to control a running Maya GUI instance remotely:

```python
import socket


def maya_cmd(command):
    """Send a Python command to Maya via Command Port and return the result."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7001))
    s.sendall(f'python("{command}")'.encode())
    result = s.recv(4096).decode()
    s.close()
    return result


def send_script(script_path):
    """Send a full .py file to Maya for execution."""
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    code = code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7001))
    s.sendall(f'python("{code}")'.encode())
    s.close()


# Example usage
if __name__ == "__main__":
    result = maya_cmd("import maya.cmds as cmds; cmds.polySphere(name='Demo')")
    print(result)
```

---

## Common Task Patterns

### 1. Create and Transform Objects

```python
import maya.cmds as cmds

# Create objects
cube = cmds.polyCube(name="MyCube")[0]
sphere = cmds.polySphere(name="MySphere")[0]

# Transform
cmds.move(0, 5, 0, cube)       # Move up by 5 units
cmds.rotate(0, 45, 0, sphere)  # Rotate 45° on Y axis
cmds.scale(2, 2, 2, cube)      # Scale uniformly by 2x

# Parenting
cmds.parent(sphere, cube)

# Group
group = cmds.group(cube, sphere, name="MyGroup")
```

### 2. Scene Query and Inspection

```python
import maya.cmds as cmds

# List all objects
all_objects = cmds.ls()
print(f"Total objects: {len(all_objects)}")

# List by type
meshes = cmds.ls(type="mesh")
joints = cmds.ls(type="joint")
cameras = cmds.ls(type="camera")

# List selected objects
selected = cmds.ls(selection=True)

# Get transform of an object
pos = cmds.xform("MyCube", query=True, translation=True, worldSpace=True)
rot = cmds.xform("MyCube", query=True, rotation=True, worldSpace=True)
scale = cmds.xform("MyCube", query=True, scale=True, worldSpace=True)

# Check if object exists
if cmds.objExists("MyCube"):
    print("MyCube exists")

# Get object children
children = cmds.listRelatives("MyGroup", children=True) or []
for child in children:
    print(f"  Child: {child}")
```

### 3. Polygon Modeling Operations

```python
import maya.cmds as cmds

# Create base mesh
cube = cmds.polyCube(name="Model")[0]

# Subdivide
cmds.polySubdivideFacet(cube, divisions=3)

# Extrude faces
cmds.select(f"{cube}.f[5]")  # Select top face
cmds.polyExtrudeFacet(translate=(0, 2, 0))

# Bevel edges
cmds.select(f"{cube}.e[0:3]")  # Select first 4 edges
cmds.polyBevel(offset=0.2, segments=3)

# Smooth mesh
cmds.polySmooth(cube, divisions=2)

# Boolean operations
cube2 = cmds.polyCube(name="Cutter", width=0.5)[0]
cmds.move(0, 0.5, 0, cube2)
cmds.polyCBoolOp(cube, cube2, operation=1)  # 0=union, 1=difference, 2=intersection
```

### 4. Animation and Keyframes

```python
import maya.cmds as cmds

# Set timeline range
cmds.playbackOptions(min=1, max=120)
cmds.currentTime(1)

# Create animated object
sphere = cmds.polySphere(name="BouncingBall")[0]

# Animate position with keyframes
cmds.setKeyframe(sphere, attribute="translateY", value=0, time=1)
cmds.setKeyframe(sphere, attribute="translateY", value=10, time=15)
cmds.setKeyframe(sphere, attribute="translateY", value=0, time=30)

# Set rotation keys
cmds.setKeyframe(sphere, attribute="rotateY", value=0, time=1)
cmds.setKeyframe(sphere, attribute="rotateY", value=360, time=30)

# Auto-keyframe (set keys automatically when changing attributes)
cmds.autoKeyframe(state=True)

# Copy/paste keys
cmds.copyKey(sphere, attribute="translateY", time=(1, 30))
cmds.pasteKey(sphere, time=30)

# Graph editor smooth tangent
cmds.keyTangent(sphere, attribute="translateY", inTangentType="spline", outTangentType="spline")
```

### 5. File Operations

```python
import maya.cmds as cmds
import os

# --- Save ---
# Save as .ma (ASCII)
cmds.file(rename="C:/projects/scene.ma")
cmds.file(save=True, type="mayaAscii")

# Save as .mb (binary)
cmds.file(rename="C:/projects/scene.mb")
cmds.file(save=True, type="mayaBinary")

# --- Open ---
cmds.file("C:/projects/scene.ma", open=True, force=True)

# --- Import ---
cmds.file("C:/projects/asset.ma", importReference=True)

# --- Export Selection ---
cmds.select("MyGroup", replace=True)
cmds.file("C:/projects/exported.ma", type="mayaAscii", exportSelected=True)

# --- Reference ---
cmds.file("C:/projects/reference.ma", reference=True, namespace="REF")

# --- Get current scene path ---
current = cmds.file(query=True, sceneName=True)
print(f"Current scene: {current}")
```

### 6. Working with Attributes

```python
import maya.cmds as cmds

sphere = cmds.polySphere(name="AttrDemo")[0]

# Add custom attribute
cmds.addAttr(sphere, longName="myFloat", defaultValue=0.5, min=0, max=1)
cmds.addAttr(sphere, longName="myEnum", attributeType="enum", enumName="Off:Low:Medium:High")

# Set attribute values
cmds.setAttr(f"{sphere}.myFloat", 0.8)
cmds.setAttr(f"{sphere}.myEnum", 2)  # "Medium"

# Get attribute values
val = cmds.getAttr(f"{sphere}.myFloat")
enum_val = cmds.getAttr(f"{sphere}.myEnum")
print(f"myFloat = {val}, myEnum = {enum_val}")

# Connect attributes
cmds.connectAttr(f"{sphere}.myFloat", f"{sphere}.scaleX")

# List all attributes
attrs = cmds.listAttr(sphere, userDefined=True) or []
print(f"User attributes: {attrs}")
```

### 7. Material and Shading

```python
import maya.cmds as cmds

# Create objects
sphere = cmds.polySphere(name="ShadedSphere")[0]

# Create standard surface shader
shader = cmds.shadingNode("standardSurface", asShader=True, name="MyMaterial")
shaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader}SG")
cmds.connectAttr(f"{shader}.outColor", f"{shaderSG}.surfaceShader")

# Set material properties
cmds.setAttr(f"{shader}.baseColor", 1, 0.2, 0.2, type="double3")  # Red
cmds.setAttr(f"{shader}.specularRoughness", 0.3)

# Assign material to object
cmds.select(sphere)
cmds.hyperShade(assign=shader)

# Create a texture
file_node = cmds.shadingNode("file", asTexture=True, name="MyTexture")
cmds.setAttr(f"{file_node}.fileTextureName", "C:/textures/diffuse.jpg", type="string")

# Connect texture to shader
cmds.connectAttr(f"{file_node}.outColor", f"{shader}.baseColor")
```

### 8. Deformer Operations

```python
import maya.cmds as cmds

# Create geometry
sphere = cmds.polySphere(name="DeformSphere", subdivisionsX=32, subdivisionsY=24)[0]

# Apply deformers
cmds.select(sphere)

# Lattice
lattice = cmds.lattice(sphere, name="Lattice1")[0]

# Bend
bend = cmds.nonLinear(sphere, type="bend", curvature=45, name="Bend1")[0]

# Twist
twist = cmds.nonLinear(sphere, type="twist", endAngle=180, name="Twist1")[0]

# Flare
flare = cmds.nonLinear(sphere, type="flare", startFlareX=0.5, endFlareX=2.0, name="Flare1")[0]

# Cluster
cmds.select(f"{sphere}.vtx[0:10]")  # Select some vertices
cluster = cmds.cluster(name="Cluster1")[0]

# Blend shape
cube = cmds.polyCube(name="BlendTarget")[0]
cmds.polyCube(cube, edit=True, width=3, height=0.5, depth=0.5)
blendshape = cmds.blendShape(cube, sphere, name="Blend1")[0]
cmds.blendShape(blendshape, edit=True, weight=(0, 0.5))
```

### 9. UI Creation

```python
import maya.cmds as cmds


def build_ui():
    """Create a simple tool window."""
    window_name = "myToolWindow"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window = cmds.window(window_name, title="My Tool", widthHeight=(300, 200))

    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, margin=(10, 10, 10, 10))

    cmds.text(label="My Maya Tool", font="boldLabelFont")

    cmds.separator(height=10)

    cmds.button(label="Create Sphere", command=lambda x: create_sphere())
    cmds.button(label="Create Cube", command=lambda x: create_cube())
    cmds.button(label="Delete Selected", command=lambda x: delete_selected())
    cmds.button(label="Close", command=lambda x: cmds.deleteUI(window_name))

    cmds.showWindow(window)


def create_sphere():
    cmds.polySphere()

def create_cube():
    cmds.polyCube()

def delete_selected():
    cmds.delete(cmds.ls(selection=True))


build_ui()
```

### 10. Batch Processing

```python
import maya.cmds as cmds
import os


def batch_export_stl(input_dir, output_dir):
    """Open all .ma files in input_dir and export as STL."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for fname in os.listdir(input_dir):
        if not fname.endswith(".ma"):
            continue

        filepath = os.path.join(input_dir, fname)
        cmds.file(filepath, open=True, force=True)

        base = os.path.splitext(fname)[0]
        stl_path = os.path.join(output_dir, f"{base}.stl")

        cmds.file(stl_path, type="stlExport", exportSelected=False, force=True)
        print(f"Exported: {stl_path}")


def batch_rename(prefix="obj_"):
    """Rename all selected objects with a prefix."""
    for i, obj in enumerate(cmds.ls(selection=True), start=1):
        new_name = f"{prefix}{i:03d}"
        cmds.rename(obj, new_name)
        print(f"Renamed: {obj} -> {new_name}")
```

---

## Version-Specific Notes

| Maya Version | Notes |
|-------------|-------|
| **2020** | `standardSurface` not available; use `aiStandardSurface` (Arnold) or `lambert`/`blinn` |
| **2022** | Full `standardSurface` support; improved `polyRetopo` |
| **2025** | Latest API; `maya.cmds` backward compatible with minor additions |

- All versions use `import maya.cmds as cmds`
- MEL scripts work through `cmds` but may have different behavior
- Use `maya-2025-api-doc` (most recent) for command details unless user specifies otherwise

---

## Best Practices

1. **Use full attribute names** - Prefer `translateX` over `tx` for readability
2. **Check `objExists`** - Validate object existence before operating
3. **Handle empty lists** - `cmds.ls()` and `cmds.listRelatives()` can return `None`; use `or []` pattern
4. **Use `force=True`** - For file operations that might overwrite
5. **Batch with mayapy** - For processing many files, use Standalone mode (see `maya-control-modes`)
6. **Name your nodes** - Always pass `name=` parameter; Maya auto-names are fragile
7. **Error handling** - Wrap risky operations in try/except blocks
