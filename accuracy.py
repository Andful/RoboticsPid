'''
This script requires the following modules to be installed:
- numpy
- matplotlib (should also install numpy)
- pyserial
'''

# miscellaneous imports
import numpy as np
import serial
import argparse
import time
from collections import deque
import socket
import sys

# matplotlib for plotting the servo positions
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")
style.use('fivethirtyeight')

# tkinter for UI components
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
else:
    import tkinter as tk
    from tkinter import *

default_port = ''
if sys.platform == 'linux' or sys.platform == 'linux2':
    default_port = '/dev/ttyUSB0'
elif sys.platform == 'win32':
    default_port = 'COM4'

# creating parser and adding arguments
parser = argparse.ArgumentParser(description='Plots serial data from a microcontroller and can be used to send commands for a CPG implementation given that the correct input parsing is implemented on the controller')
parser.add_argument('-b', '--buf', dest='buf', default=100, help='Number of buffered (displayed) values. The default is 100.')
parser.add_argument('-i', '--interval', dest='interval', default=1, help='Interval at which data is sent from the microcontroller (in ms, should be known from the implementation on the controller). Only used to update the figures\' x-axis and store the interval if the data is saved to a file.')
parser.add_argument('-p', '--port', dest='port', default=default_port, help=('Serial port to use for communication with the microcontroller.' + (' The default is ' + default_port + '.' if default_port else '')))
parser.add_argument('-r', '--baud-rate', dest='baud_rate', default=115200, help='Baud rate for the serial connection. The default is 9600.')
parser.add_argument('-s', '--save', dest='save', default=False, nargs='?', help='Filepath to save all measured values to (only y-values). NOTE: this may take up a lot of memory when the program is running for a long time.')
parser.add_argument('-t', '--target', dest='target', default=512, help='Initial target value. The default is 512.')

# parsing arguments
args = parser.parse_args()
buf = int(args.buf)
interval = int(args.interval)
port = args.port
baud_rate = int(args.baud_rate)
save = args.save
target = int(args.target)

# initialising serial connection
ser = serial.Serial(port, baud_rate)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)

# initialising the figure and range of the axes
fig = plt.figure()
axis = plt.axes(xlim=(0, buf), ylim=(-50, 1075))
axis.set_xticklabels(range(0, buf * interval + 1, int(buf * interval / 5)))
axis.tick_params(labelsize=14)

# initialising x- and y-values for the plot
x_val = np.linspace(0, (buf - 1), num=buf)
y_val = deque([0.0] * buf)

# initialising the line used for plotting the motoros position
graph_line, = axis.plot([], [])
graph_line.set_xdata(x_val)
graph_line.set_ydata(y_val)

# initialising the line showing the current target value
target_line, = axis.plot([], [])
target_line.set_linestyle('dashed')
target_val = [target] * buf
target_line.set_xdata(x_val)
target_line.set_ydata(target_val)

# to be used for storing all y data, which can then be written to a file
full_y_data = []

# tkinter GUI setup
root = tk.Tk()
root.wm_title('PID Plotter')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# quit methods for tkinter window
def quit():
    root.quit()
    root.destroy()

def quit_by_key(v):
    root.quit()

root.protocol("WM_DELETE_WINDOW", quit)
root.bind('<Control-w>', quit_by_key)

frame = tk.Frame(root)
frame.pack(side=tk.BOTTOM)

# creating the input elements for the target value
target_label = tk.Label(frame, text="Target: ")
target_label.grid(row=0, column=0)
target_entry = tk.Entry(frame)
target_entry.grid(row=0, column=1)
def get_target_val(v):
    cmd_val = int(target_entry.get())
    ser.write('target '.encode() + str(cmd_val).encode() + '\n'.encode())
    target_val = [cmd_val] * buf
    target_line.set_ydata(target_val)
target_entry.bind('<Return>', get_target_val)

# creating the input elements for kp (proportional gain)
kp_label = tk.Label(frame, text="kp: ")
kp_label.grid(row=1, column=0)
kp_entry = tk.Entry(frame)
kp_entry.grid(row=1, column=1)
def get_kp_val(v):
    cmd_val = float(kp_entry.get())
    ser.write('kp '.encode() + str(cmd_val).encode() + '\n'.encode())
kp_entry.bind('<Return>', get_kp_val)

# creating the input elements for ki (integral gain)
ki_label = tk.Label(frame, text="ki: ")
ki_label.grid(row=2, column=0)
ki_entry = tk.Entry(frame)
ki_entry.grid(row=2, column=1)
def get_ki_val(v):
    cmd_val = float(ki_entry.get())
    ser.write('ki '.encode() + str(cmd_val).encode() + '\n'.encode())
ki_entry.bind('<Return>', get_ki_val)

# creating the input elements for kd (derivative gain)
kd_label = tk.Label(frame, text="kd: ")
kd_label.grid(row=3, column=0)
kd_entry = tk.Entry(frame)
kd_entry.grid(row=3, column=1)
def get_kd_val(v):
    cmd_val = float(kd_entry.get())
    ser.write('kd '.encode() + str(cmd_val).encode() + '\n'.encode())
kd_entry.bind('<Return>', get_kd_val)

acc_label = tk.Label(frame, text="acc: ")
acc_label.grid(row=0, column=2)
acc_entry = tk.Entry(frame)
acc_entry.grid(row=0, column=3)
def get_acc_val(v):
    cmd_val = float(acc_entry.get())
    ser.write('acc '.encode() + str(cmd_val).encode() + '\n'.encode())
acc_entry.bind('<Return>', get_acc_val)

is_200 = False
def callback():
    global is_200
    is_200 = not is_200
    if is_200:
        cmd_val = 200
    else:
        cmd_val = 800
        
    ser.write('target '.encode() + str(cmd_val).encode() + '\n'.encode())
    target_val = [cmd_val] * buf
    target_line.set_ydata(target_val)
    
    get_kp_val(0)
    get_ki_val(0)
    get_kd_val(0)
    get_acc_val(0)

change_position = tk.Button(frame,text='change',command=callback)
change_position.grid(row=2, column=3)

# creating a label to show the current target
target_label = tk.Label(frame, text='init', font=(None, 15))
target_label.grid(row=4, column=1)

# animation method called by FuncAnimation, updated every couple milliseconds
def animate(v):
    line = ''
    while ser.in_waiting > 0:
        try:
            line = ser.readline()
            if line.decode('ASCII').startswith('output:'):
                sock.sendto(line, server_address)
                continue
            number = line.strip().decode('ASCII')
            val = int(number)

            # update y datastartswith(
            if len(y_val) < buf:
                y_val.appendleft(val)
            else:
                y_val.pop()
                y_val.appendleft(val)

            # update graphics
            graph_line.set_ydata(y_val)
            target_label.config(text=number)

            # if the values should be saved add them to the full_y_data list
            if save or save == None:
                full_y_data.append(val)
        except (KeyboardInterrupt, ValueError, UnicodeDecodeError, serial.serialutil.SerialException) as e:
            print('FAILED TO READ DATA, INSTEAD GOT:')
            try:
                if line:
                    print(line.strip().decode(), end='\n\n')
            except Exception as e:
                pass

# initialising the function animation
ani = animation.FuncAnimation(fig, animate, interval=25)

# displaying the GUI
try:
    plt.gca().invert_xaxis()
    root.mainloop()
except:
    print('A display error occured.')

# closing serial line after program has been closed
ser.flush()
ser.close()

# save the file if the -s flag is used
if save or save == None:
    filename = ''
    if isinstance(save, str):
        filename = save
    else:
        filename = 'pid_data__'
        filename = filename + time.strftime("%Y-%m-%d__%H-%M-%S")
    with open(filename, 'w') as file:
        if interval:
            file.write('i: ' + str(interval) + '\n')
        for y in full_y_data:
            file.write(str(y) + '\n')
        print('Saved to file \"' + filename + '\".')
