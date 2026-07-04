---
name: "maya-api-doc"
description: "Overview skill for Maya Python command documentation (maya.cmds). Provides shared data structure documentation, category taxonomy, and proper reading methods for all Maya version-specific skills (2020/2022/2025). Invoke when user asks about Maya commands, maya.cmds usage, or needs guidance on how to access the API documentation data."
---

# Maya Python Command Documentation Overview

This skill serves as the **central guide** for all Maya API documentation skills in this project. It describes the shared data structure, category taxonomy, and proper methods for reading the JSON data files.

---

## Companion Skills

| Skill Name | Purpose |
|------------|---------|
| `maya-control-modes` | Execute Maya commands externally via standalone mode (mayapy) or Command Port mode |

**How they work together**:
- This overview skill (`maya-api-doc`) helps you **find and understand** Maya commands
- `maya-control-modes` skill helps you **execute** those commands in actual Maya instances
- Project's [tools/](../../../tools/) directory provides ready-to-use Command Port scripts that implement the patterns from `maya-control-modes`

---

## ⚠️ CRITICAL WARNING: Do NOT Read Entire JSON Files

**DO NOT** use `Read` to open the entire `maya_commands_python.json` file. These files are **very large** (multiple MBs) and will cause context overflow.

**ALWAYS** use:
- **Grep** to search for specific commands, keywords, or categories
- **Read with `offset`/`limit`** to read only small portions of the files

---

## Available Skills by Maya Version

| Skill Name | Version | Total Commands | Data Path |
|------------|---------|----------------|-----------|
| `maya-2020-api-doc` | Maya 2020 | 1499 | `.trae/skills/maya-2020-api-doc/data/` |
| `maya-2022-api-doc` | Maya 2022 | 1503 | `.trae/skills/maya-2022-api-doc/data/` |
| `maya-2025-api-doc` | Maya 2025 | 1521 | `.trae/skills/maya-2025-api-doc/data/` |

**How to select a version:**
- If user specifies a version (e.g., "Maya 2022 commands"), use the corresponding skill
- If user doesn't specify, use `maya-2025-api-doc` (most recent)
- Command syntax is mostly identical across versions; differences are minimal

---

## Data Structure Reference

All version-specific skills share the same data structure.

### 1. index.json

**Purpose**: Maps command names to their category, subcategory, and script type.

**Location**: `<skill-path>/data/index.json`

**Structure**:
```json
{
  "addAttr": {
    "category": "General",
    "subcategory": "Node Attributes",
    "isMelScript": false
  },
  "curveRGBColor": {
    "categories": [
      { "category": "General", "subcategory": "Display Parameters" },
      { "category": "Animation", "subcategory": "Creating Animation and Manipulating Keyframes" }
    ],
    "isMelScript": true
  }
}
```

**Key Fields**:
- `category`: Top-level category (see table below)
- `subcategory`: Specific subcategory within the category
- `categories`: Some commands belong to multiple categories (array of category objects)
- `isMelScript`: `true` if the command is a MEL script, `false` if it's a built-in C++ command

### 2. maya_commands_python.json

**Purpose**: Contains full command documentation with descriptions and Python examples.

**Location**: `<skill-path>/data/maya_commands_python.json`

**Structure**:
```json
{
  "meta": {
    "source": "https://help.autodesk.com/cloudhelp/2022/CHS/Maya-Tech-Docs",
    "version": "Maya 2022",
    "total": 1503,
    "success": 1190,
    "withDescription": 1184,
    "withExamples": 1182,
    "errors": 313
  },
  "commands": [
    {
      "name": "addAttr",
      "description": "This command is used to add a dynamic attribute...",
      "examples": "import maya.cmds as cmds\n\ncmds.sphere(name='earth')\ncmds.addAttr(longName='mass', defaultValue=1.0)",
      "url": "https://help.autodesk.com/cloudhelp/2022/CHS/Maya-Tech-Docs/CommandsPython/addAttr.html"
    },
    {
      "name": "abs",
      "description": "",
      "examples": "",
      "error": "HTTP 404"
    }
  ]
}
```

**Key Fields**:
- `name`: Command name (used with `cmds.name()`)
- `description`: Extracted from the "Synopsis" section of official docs
- `examples`: Verbatim Python code examples from official docs
- `url`: Link to the official Autodesk documentation
- `error`: "HTTP 404" if the Python documentation page doesn't exist

---

## Category Taxonomy

### Full Category Tree

| Category | Subcategories |
|----------|---------------|
| **Animation** | Constraints, Creating Animation and Manipulating Keyframes, Joints/Handles/Skeletons, Motion Capture, Object Deformation, Skinning |
| **Effects** | Fluid Effects, Hair, Maya Fur, Paint Effects Brushes/Strokes, Particles/Forces/Simulations, nParticles/nCloth/nConstraints |
| **General** | Display Parameters, General Interest Utilities, Interactive tools, Node Attributes, Picking/Selecting |
| **Language** | Array Manipulation, MEL Math-Related Commands, MEL Scripts, MEL String-Related Commands |
| **Modeling** | Curve commands, NURBS Surfaces, Polygon Meshes, Subdivision Surfaces |
| **Rendering** | Camera Manipulation, General Rendering, Lighting, Render Layer and Pass Management |
| **System** | Device Handling, File/Image/Directory Handling, Localization Support, Miscellaneous Utilities, Plug-in Handling |
| **Windows** | Buttons/Sliders, Miscellaneous UI, Organizing UI Components, Windows |

### Category Quick Reference

**Animation** - Rigging, skinning, constraints, keyframes, IK/FK, motion capture

**Effects** - Particles, fluids, hair, fur, cloth simulation, dynamics

**General** - Core Maya operations: transforms, attributes, selection, display, basic tools

**Language** - MEL/Python language constructs: math, string manipulation, array operations

**Modeling** - NURBS, polygons, curves, subdivision surfaces, mesh editing

**Rendering** - Lights, cameras, rendering settings, render layers, passes

**System** - File I/O, plugins, devices, localization, utilities

**Windows** - UI components, windows, dialogs, controls, layouts

---

## How to Read Data: Grep Templates

### 1. Look up a specific command

**Goal**: Get detailed info for `cmds.addAttr`

```
Grep: pattern="\"addAttr\"" in <skill-path>/data/maya_commands_python.json
      output_mode="content" with -A 10
```

**Example**:
```
Grep: pattern="\"addAttr\"" in .trae/skills/maya-2022-api-doc/data/maya_commands_python.json
      output_mode="content" -A 10
```

### 2. List commands in a category

**Goal**: Find all commands related to "Skinning"

```
Step 1: Grep index.json for the subcategory
Grep: pattern="Skinning" in <skill-path>/data/index.json
      output_mode="content"

Step 2: Extract command names from results
Step 3: Grep each command in maya_commands_python.json
```

**Example**:
```
Grep: pattern="Skinning" in .trae/skills/maya-2022-api-doc/data/index.json
      output_mode="content"
```

### 3. Search by keyword

**Goal**: Find commands related to "texture" or "UV"

```
Grep: pattern="texture|uv|UV" in <skill-path>/data/maya_commands_python.json
      output_mode="content" -i
```

### 4. Check if a command exists

**Goal**: Verify if `cmds.someCommand` exists

```
Grep: pattern="\"someCommand\"" in <skill-path>/data/index.json
      output_mode="content"
```

### 5. Get command category

**Goal**: Find which category `cmds.polySphere` belongs to

```
Grep: pattern="\"polySphere\"" in <skill-path>/data/index.json
      output_mode="content" -A 3
```

---

## Best Practices for AI

1. **Always use Grep first** - It's the fastest way to find specific commands
2. **Specify version path** - Include the full path in Grep commands
3. **Limit output with -A** - Use `-A 5` or `-A 10` to avoid overwhelming context
4. **Use -i for case-insensitive** - Useful for keyword searches
5. **Check index.json first** - It's smaller and faster to search
6. **Handle HTTP 404 gracefully** - Some commands don't have Python docs; they may still work

---

## Example Workflow

**User Question**: "How do I create a polygon sphere in Maya Python?"

1. **Search for the command**:
   ```
   Grep: pattern="\"polySphere\"" in .trae/skills/maya-2025-api-doc/data/maya_commands_python.json
         output_mode="content" -A 15
   ```

2. **Extract the result**:
   - Description: "Creates a polygon sphere"
   - Examples: Python code snippets showing usage
   - URL: Link to official docs

3. **Present the information** in a clear, concise format

---

## Data Quality Notes

- Some commands (313-316 depending on version) return HTTP 404 - these are MEL-only commands without Python-specific documentation
- Descriptions are truncated at 1500 characters
- Examples are truncated at 3000 characters
- All commands are accessed via `import maya.cmds as cmds`
- MEL-only scripts (`isMelScript: true`) can still be called via `cmds` but may behave differently