import socket

def send_to_maya(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 6000))
    s.sendall(f'python("{command}")'.encode())
    result = s.recv(4096).decode()
    s.close()
    return result

# Execute an external script in Maya
script_path = r'C:/temp/maya_anim.py'
command = f'''
import importlib, sys, codecs
spec = importlib.util.spec_from_file_location("maya_anim", r"{script_path}")
mod = importlib.util.module_from_spec(spec)
sys.modules["maya_anim"] = mod
spec.loader.exec_module(mod)
'''

print(send_to_maya(command.strip()))
