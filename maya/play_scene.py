import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6000))

# Go to frame 1 and play
s.sendall('python("cmds.currentTime(1)")'.encode('utf-8'))
import time; time.sleep(0.1)
r = s.recv(1024)
print("Go to frame 1:", r.decode())

# Start playback
s.sendall('python("cmds.play(forward=True)")'.encode('utf-8'))
time.sleep(0.1)
r = s.recv(1024)
print("Play:", r.decode())

s.close()
print("\nScene is playing! Check your Maya viewport.")
