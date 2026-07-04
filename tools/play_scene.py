import socket

def send_to_maya(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 6000))
    s.sendall(f'python("{command}")'.encode())
    result = s.recv(4096).decode()
    s.close()
    return result

# Set to first frame and play
cmds = [
    'import maya.cmds as cmds',
    'cmds.currentTime(1)',
    'cmds.play(forward=True)',
]

for cmd in cmds:
    print(f">>> {cmd}")
    print(send_to_maya(cmd))
