import socket

def send_to_maya(command):
    """Send a Python command to Maya via Command Port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 6000))
    s.sendall(f'python("{command}")'.encode())
    result = s.recv(4096).decode()
    s.close()
    return result

# Test commands
cmds = [
    'import maya.cmds as cmds; print("Maya connected!")',
    '1+1',
    'len(cmds.ls(type="mesh"))',
    'cmds.objExists("energy_core")',
]

for cmd in cmds:
    print(f">>> {cmd}")
    print(send_to_maya(cmd))
    print()
