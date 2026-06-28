---
name: "maya-2025-api-doc"
description: "Provides Maya 2025 Python command documentation (maya.cmds). Includes 1521 commands with descriptions, Python examples, and category index. Invoke when user asks about Maya 2025 commands, Maya API, Maya Python scripting, maya.cmds usage, or needs code examples for Maya 2025 automation."
---

# Maya 2025 Python Command Documentation

This skill provides access to scraped Maya 2025 command documentation. All data is sourced from the official Autodesk Maya 2025 Chinese documentation.

## Data Files

```
.trae/skills/maya-2025-api-doc/data/
├── index.json                  # Command name -> category mapping
└── maya_commands_python.json   # Full command docs with descriptions & examples
```

**IMPORTANT**: Never read the entire `maya_commands_python.json` in one call. Use **Grep** to find specific commands, or **Read** with `offset`/`limit` to read only relevant portions.

## Data Structures

### index.json
Maps command name to its category and subcategory:
```json
{
  "addAttr": {
    "category": "General",
    "subcategory": "Node Attributes",
    "isMelScript": false
  }
}
```

### maya_commands_python.json
```json
{
  "meta": { "source": "...", "version": "Maya 2025", "total": 1521, ... },
  "commands": [
    {
      "name": "addAttr",
      "description": "This command is used to add a dynamic attribute...",
      "examples": "import maya.cmds as cmds\n\ncmds.sphere(name='earth')...",
      "url": "https://help.autodesk.com/.../addAttr.html"
    }
  ]
}
```

## Data Quality

| Metric | Value |
|--------|-------|
| Total commands | 1521 |
| Successfully scraped | 1205 |
| With description | 1199 |
| With Python examples | 1197 |
| HTTP 404 (no Python page) | 316 |

Some commands (316 out of 1521) have no Python-specific documentation page (HTTP 404). These commands may still be callable via `maya.cmds` but lack dedicated Python examples.

## How to Use

### 1. Look up a specific command
When user asks about a specific command (e.g., "How does cmds.addAttr work?"):
```
Grep: pattern="\"addAttr\"" in maya_commands_python.json, output_mode="content" with -A 30
```
This returns the command's name, description, Python examples, and URL.

### 2. List commands by category
When user asks about a category (e.g., "What animation commands exist?"):
```
Step 1: Grep index.json for the subcategory name (e.g., "Constraints" or "Skinning")
Step 2: Extract matching command names
Step 3: Grep maya_commands_python.json for those specific command names
```

### 3. Search commands by keyword
When user asks about a topic (e.g., "commands related to skinning"):
```
Grep: pattern="skinning|skin|bind" in maya_commands_python.json
```

### 4. Provide code examples
Extract the `examples` field from the command entry. These are ready-to-use Python snippets using `maya.cmds`.

## Important Notes

- All commands are accessed via `import maya.cmds as cmds` in Python
- Commands that are MEL-only scripts (marked `isMelScript: true` in index.json) are scripts, not built-in C++ commands
- The `description` field is extracted from the "Synopsis" section of the official documentation
- The `examples` field contains verbatim Python code examples from the official docs
- Descriptions are truncated at 1500 characters, examples at 3000 characters
