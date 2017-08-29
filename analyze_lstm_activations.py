import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig1 = plt.figure()

def animate_data_as_line(data):
    def update_line(num, data, line):
        line.set_data(data[..., :num])
        return line,

    l, = plt.plot([], [], 'r-')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel('x')
    plt.title('test')
    print("ani start")
    line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(data, l),
                                       interval=50, blit=True)
    print("ani done")

    return line_ani
'''
data = np.random.rand(2, 25)
animate_data_as_line(data)
'''

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
#data_to_animate=np.array([perf_df[:].time, perf_df[:].x])
data_to_animate = np.random.rand(2, 25)
print("data is ", data_to_animate.shape)
anim = analyzer.animate_data_as_line(data_to_animate)
HTML(anim.to_html5_video())
'''