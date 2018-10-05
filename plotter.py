import socket
import matplotlib.pyplot as plt
from itertools import cycle
UDP_IP = "localhost"
UDP_PORT = 10000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

p = [0] * 100
i = [0] * 100
d = [0] * 100

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
p_line, = ax.plot(list(range(len(p))),p, 'r-')
i_line, = ax.plot(list(range(len(i))),i, 'g-')
d_line, = ax.plot(list(range(len(d))),d, 'b-')

for k in cycle(range(100)):
    data, addr = sock.recvfrom(256) # buffer size is 1024 bytes
    line = data.decode('ASCII')
    line = line[len("output:\t"):]


    p_str, i_str, d_str = line.split('\t')[1:]
    p.append(float(p_str[len("proportion="):]))
    i.append(float(i_str[len("integral="):]))
    d.append(float(d_str[len("derivative="):]))

    p = p[1:]
    i = i[1:]
    d = d[1:]

    if k == 0:
        print(line.split('\t'))
        p_line.set_ydata(p)
        i_line.set_ydata(i)
        d_line.set_ydata(d)

        fig.canvas.draw()
        fig.canvas.flush_events()
