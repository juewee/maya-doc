import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6000))

# Send python command to execute the script
cmd = 'python("exec(open(\'C:/temp/maya_anim.py\').read())")'
s.sendall(cmd.encode('utf-8'))

r = s.recv(4096)
print('Maya:', r.decode())
s.close()
