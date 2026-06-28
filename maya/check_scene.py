import socket

def send_rcv(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 6000))
    s.sendall(cmd.encode('utf-8'))
    import time
    time.sleep(0.3)
    s.settimeout(3)
    try:
        r = s.recv(4096)
        return r.decode('utf-8', errors='replace')
    except socket.timeout:
        return "(timeout)"
    finally:
        s.close()

# Use python() without print - it returns the expression result
print("MEL echo:", repr(send_rcv('echo "Hello from outside"')))
print("Python eval:", repr(send_rcv('python("1+1")')))
print("Mesh count:", repr(send_rcv('python("len(cmds.ls(type=\\\'mesh\\\'))")')))
print("Has energy_core:", repr(send_rcv('python("cmds.objExists(\\\'energy_core\\\')")')))
