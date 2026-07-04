---
name: "maya-control-modes"
description: "Provides two methods to control Maya externally: (1) Headless Standalone mode via mayapy for batch/automation tasks without GUI, (2) Command Port mode for controlling a running Maya GUI instance via TCP. Invoke when user needs to run Maya scripts from outside Maya, automate batch operations, or control Maya remotely."
---

# Maya Control Modes

Two methods to control Maya externally from Python scripts, without writing code inside Maya's Script Editor.

> **配套即用脚本**：本项目的 [tools/](../../../tools/) 目录提供了 Command Port 模式的即用实现（check_scene.py、play_scene.py、send_to_maya.py），可直接运行。

## Method Comparison

| 特性 | Standalone (mayapy) | Command Port |
|------|---------------------|--------------|
| Maya GUI 需要打开? | 不需要 | 需要先打开 Maya |
| 适用场景 | 批处理、管线、CI/CD | 远程控制、热加载 |
| 通信方式 | 直接进程调用 | TCP socket |
| 速度 | 启动慢，执行快 | 即时通信 |
| 查看结果 | 保存文件后查看 | 实时在 Maya 中查看 |

---

## Method 1: Standalone / Headless Mode (mayapy)

通过 `mayapy.exe` 在无 GUI 环境下运行 Maya 脚本。所有操作都在后台完成。

### mayapy 路径

```
D:\losheep\tools\Maya\Maya2025\bin\mayapy.exe
```

### 基础模板

```python
# -*- coding: utf-8 -*-
import maya.standalone
maya.standalone.initialize(name="python")

import maya.cmds as cmds
import os

# ===== 在这里编写 Maya 操作 =====


# ===== 保存并退出 =====
maya.standalone.uninitialize()
```

### 运行方式

```powershell
& "D:\losheep\tools\Maya\Maya2025\bin\mayapy.exe" "脚本路径.py"
```

### 常用操作示例

**创建对象并保存文件：**
```python
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import os

cmds.polyCube(name="MyCube")
cmds.polySphere(name="MySphere")
cmds.move(3, 0, 0, "MySphere")

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
cmds.file(rename=os.path.join(desktop, "output.ma"))
cmds.file(save=True, type="mayaAscii")

maya.standalone.uninitialize()
```

**打开已有文件并读取大纲：**
```python
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import os

cmds.file("path/to/scene.ma", open=True, force=True)

# 列出顶层节点
for t in cmds.ls(assemblies=True):
    print(t)
    for child in (cmds.listRelatives(t, children=True, fullPath=True) or []):
        print(f"  {child}")

maya.standalone.uninitialize()
```

**批量统计节点信息：**
```python
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds

cmds.file("scene.ma", open=True, force=True)

print(f"总节点数: {len(cmds.ls())}")
print(f"Mesh 节点: {len(cmds.ls(type='mesh'))}")
print(f"材质节点: {len(cmds.ls(type='lambert'))}")

maya.standalone.uninitialize()
```

### 重要注意事项

1. **初始化只调用一次**：`maya.standalone.initialize()` 在整个脚本中只能调用一次
2. **不要用 `reload`**：`sys.modules.keys()` 中有很多 Maya 相关的模块，不要依赖 Python 的 `reload()`
3. **UI 命令不可用**：所有需要 GUI 交互的命令（如 `promptDialog`, `fileDialog` 等）在 standalone 模式下无效
4. **World 空间是空的**：standalone 模式下没有默认的 persp/top/front/side 相机
5. **插件**：如需使用插件，在 `initialize()` 之后用 `cmds.loadPlugin()` 加载

---

## Method 2: Command Port Mode

通过 TCP 端口连接到正在运行的 Maya GUI 实例，实时发送 Python 命令并获取结果。

### 步骤 1：在 Maya 中打开命令端口

在 Maya 的 Script Editor 中执行（只需执行一次）：

```python
import maya.cmds as cmds
cmds.commandPort(name=":7001", sourceType="python")
```

或者开机自动执行：将上述代码保存为 `userSetup.py` 放到 `Documents/maya/2025/scripts/` 下。

### 步骤 2：从外部 Python 发送命令

```python
import socket

def maya_cmd(command):
    """向 Maya 发送 Python 命令并返回结果"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7001))
    
    # 发送命令
    s.sendall(('python("' + command + '")').encode())
    
    # 接收结果（需要根据实际情况调整接收逻辑）
    result = s.recv(4096).decode()
    s.close()
    return result

# 创建一个球体
maya_cmd("import maya.cmds as cmds; cmds.polySphere(name='RemoteSphere')")

# 获取选中对象名称
print(maya_cmd("import maya.cmds as cmds; print(cmds.ls(selection=True))"))
```

### 步骤 3：从文件执行整个脚本

```python
import socket

def send_script_to_maya(script_path):
    """将完整脚本文件发送到 Maya 执行"""
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # 需要转义引号和换行
    code = code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7001))
    s.sendall(f'python("{code}")'.encode())
    s.close()

send_script_to_maya("path/to/my_script.py")
```

### 使用 mayapy 通过 Command Port 发送命令

```powershell
# 发送单行命令
echo 'python("cmds.polyCube()")' | nc 127.0.0.1 7001
```

### 重要注意事项

1. **Maya 必须正在运行**：Command Port 依赖 Maya GUI 实例
2. **端口冲突**：选择未被占用的端口（默认 `7001`）
3. **不安全**：Command Port 没有认证机制，不要暴露到公网
4. **结果获取**：需要自行设计结果回传机制（如输出到文件、socket 返回等）
5. **线程安全**：Maya 命令在主线程执行，外部命令会排队等待

---

## 选择哪种方式?

| 需求 | 推荐方式 |
|------|----------|
| 后台批量处理文件 | Standalone |
| CI/CD 管线自动化 | Standalone |
| 渲染农场 | Standalone |
| 实时控制 Maya 中的对象 | Command Port |
| 热加载脚本不重启 Maya | Command Port |
| 外部工具与 Maya 联动 | Command Port |
