import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

ANIM_INTERVAL = 50

#interval controls speed. Higher interval - lower speed.
def animate_data_as_line(data, fig, xmin=-10,ymin=-10, xmax=10, ymax=10, anim_interval=ANIM_INTERVAL):
    def update_line(num, data, line):
        line.set_data(data[..., :num])
        return line,
    l, = plt.plot([], [], 'r-')
    plt.xlim(xmin,xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel('x')
    plt.title('test')
    print("ani start")
    #interval controls animation speed.
    line_ani = animation.FuncAnimation(fig, update_line, fargs=(data, l),
                                       interval=anim_interval, blit=True)
    print("ani done")

    return line_ani

def animate_data_as_grid(data, fig, ax, xmin=-10, ymin=-10, xmax=10, ymax=10, anim_interval=ANIM_INTERVAL):

    x_size = y_size = data.shape[0]
    num_timesteps = data.shape[1]

    #TODO Enable a mode where the plot slides from 0 and up,
    #TODO Strange diagonal artifacts...
    def animate(i):
        if i > y_size:
            cax.set_array(data[:, i-y_size:i].flatten())
        else:
            #filling initial fields with zero.
            data_array = np.zeros((x_size, y_size))
            data_array[:,  y_size-i:] = data[:, :i]
            cax.set_array(data_array.flatten())

    x = np.linspace(xmin, xmax, x_size+1) #1 for each neuron.
    y = np.linspace(ymin, ymax, y_size+1) # making the plot square - doesn't have to be.


    #fig, ax = plt.subplots(figsize=(5, 3))

    cax = ax.pcolormesh(x, y, data[:, :y_size],
                        vmin=-1, vmax=1, cmap='Blues')
    fig.colorbar(cax)
    anim = animation.FuncAnimation(
        fig, animate, interval=anim_interval, frames=(num_timesteps-y_size))

    return anim #TODO Study how to return a plot from python to jupyter

#Loading and plotting LSTM model data.

import random
import numpy as np
import tensorflow as tf
import musical_mdn
import matplotlib.pyplot as plt
import pandas as pd

musical_mdn.MODEL_DIR = "/home/kaiolae/tf_models/mdn-experiments/"
print(musical_mdn.MODEL_DIR)
## Evaluation Test:
## Predict 10000 Datapoints.
net = musical_mdn.TinyJamNet2D(mode = musical_mdn.NET_MODE_RUN, n_hidden_units = 128, n_mixtures = 10, batch_size = 1, sequence_length = 1)

first_touch = np.array([(0.01 + (np.random.rand()-0.5)*0.005), (np.random.rand()-0.5)*20])
print("Test Input:",first_touch)
with tf.Session() as sess:
    perf = net.generate_performance(first_touch,500,sess,True)
print("Test Output:")
perf_df = pd.DataFrame({'t':perf.T[0], 'x':perf.T[1]})
perf_df['time'] = perf_df.t.cumsum()
#plt.show(perf_df.plot('time','x',kind='scatter'))
plt.plot(perf_df.time, perf_df.x, '.r-')
plt.show()
print(perf_df.describe())
## Investigate Output


data_to_animate=np.array([perf_df[:].time, perf_df[:].x])
#data_to_animate = np.random.rand(2, 25)

#Animating LSTM output
fig1 = plt.figure()
plt.title("Output")
anim = animate_data_as_line(data_to_animate,fig1)
print("output-data: ", data_to_animate.shape)

#Animating LSTM internal state
fig2, ax2 = plt.subplots()
plt.title("Memory State")
anim2 = animate_data_as_grid(np.squeeze(net.state_history_c).T, fig2, ax2)
print("memory-data: ", np.squeeze(net.state_history_c).T.shape)

#Animating LSTM internal state
fig3, ax3 = plt.subplots()
plt.title("Activation State")
anim2 = animate_data_as_grid(np.squeeze(net.state_history_h).T, fig3, ax3)
print("activation-data: ",np.squeeze(net.state_history_h).T.shape)

plt.draw()
plt.show()

'''
def make_many_animations(line_animation_data=None, grid_animation_data=None):
    numsubplots = 0
    if line_animation_data!=None:
        numsubplots+=line_animation_data.shape[0]
    if grid_animation_data!=None:
        numsubplots+=grid_animation_data.shape[0]

    print("Subplt")
    fig, ax_array = plt.subplots(numsubplots, sharex=True)
    print("Subplt done")
    subplotcounter = 0
    for data in line_animation_data:
        print(data)
        animate_data_as_line(data, fig)
        subplotcounter+=1

    for data in grid_animation_data:
        animate_data_as_line(data, fig)
        subplotcounter+=1

    plt.draw()
    plt.show()
'''
#200 timesteps of neuron activations.
'''random_data = np.random.randn(90,2000)
random_data2 = np.random.randn(90,2000)

random_data_line =  np.random.rand(2, 25)
#print(random_data.shape)
fig,ax=plt.subplots()
fig3,ax3=plt.subplots()
fig2=plt.figure()
animator = animate_data_as_grid(random_data,fig, ax)
animator3 = animate_data_as_grid(random_data2,fig3, ax3)
animator2 = animate_data_as_line(random_data_line, fig2)
#make_many_animations(np.array([random_data_line]),np.array([random_data,random_data2]))
plt.draw()
plt.show()'''


#data = np.random.rand(2, 25)
#ani=animate_data_as_line(data)
#plt.show()

"""
============
Oscilloscope -> live animation
============

Emulates an oscilloscope.

import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Scope(object):
    def __init__(self, ax, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(-.1, 1.1)
        self.ax.set_xlim(0, self.maxt)

    def update(self, y):
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax.figure.canvas.draw()

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        return self.line,


def emitter(p=0.03):
    'return a random value with probability p, else 0'
    while True:
        v = np.random.rand(1)
        if v > p:
            yield 0.
        else:
            yield np.random.rand(1)

fig, ax = plt.subplots()
scope = Scope(ax)

# pass a generator in "emitter" to produce data for the update func
ani = animation.FuncAnimation(fig, scope.update, emitter, interval=10,
                              blit=True)


plt.show()
"""

'''
fig2 = plt.figure()

x = np.arange(-9, 10)
y = np.arange(-9, 10).reshape(-1, 1)
base = np.hypot(x, y)
ims = []
for add in np.arange(15):
    ims.append((plt.pcolor(x, y, base + add, norm=plt.Normalize(0, 30)),))

im_ani = animation.ArtistAnimation(fig2, ims, interval=50, repeat_delay=3000,
                                   blit=True)
#im_ani.save('im.mp4', metadata={'artist':'Guido'})

plt.show()'''

'''The imshow code:
plt.imshow(np.squeeze(net.state_history_c).T)
plt.show()
'''

'''
To get the animation as ipython notebook:

%matplotlib inline
from IPython.display import HTML
import analyze_lstm_activations as analyzer
data_to_animate=np.array([perf_df[:].time, perf_df[:].x])
#data_to_animate = np.random.rand(2, 25)
print("data is ", data_to_animate.shape)
anim = analyzer.animate_data_as_line(data_to_animate)
HTML(anim.to_html5_video())
'''