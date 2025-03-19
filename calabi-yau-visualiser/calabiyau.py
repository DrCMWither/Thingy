'''
    inspired by https://observablehq.com/@sw1227/calabi-yau-manifold-3d
'''

from functools import cache
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def coordinate(x, y, n, k1, k2, a):
    z1 = np.exp(2j * math.pi * k1 / n) * np.cos(x + 1j * y) ** (2 / n)
    z2 = np.exp(2j * math.pi * k2 / n) * np.sin(x + 1j * y) ** (2 / n)
    return np.real(z1), np.real(z2), np.real(z1) * math.cos(a) + np.imag(z2) * math.sin(a)

def normal_rect(p1, p2, p3, p4):
    return [p1, p2, p3, p4, p1]

@cache
def calabi_yau(n, a):
    dx = math.pi / 15
    dy = math.pi / 15
    meshes = []
    for k in np.ndindex((n, n)):
        for x in np.arange(0, math.pi / 2, dx):
            for y in np.arange(-math.pi / 2, math.pi /  2, dy):
                data = [(x, y),
                        (x + dx, y),
                        (x + dx, y + dy),
                        (x, y + dy),
                ]
                vertices = [coordinate(*d, n, k[0], k[1], a) for d in data]
                meshes.append(normal_rect(*vertices))
    return meshes

def update(frame, fig, ax, n, a_min, a_max):
    a = a_min + (frame / FPS) * (a_max - a_min)

    meshes = calabi_yau(n, a)

    X, Y, Z = [], [], []
    for mesh in meshes:
        x, y, z = zip(*mesh)
        X.extend(x)
        Y.extend(y)
        Z.extend(z)

    X = np.array(X).reshape(-1, 4)
    Y = np.array(Y).reshape(-1, 4)
    Z = np.array(Z).reshape(-1, 4)

    ax.clear()
    ax.plot_wireframe(X, Y, Z, color = 'black', linewidth = 0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_zlim(-2.5, 2.5)
    ax.set_title(f'n = {n}, a = {a:.2f}')
    return fig, ax

n = 4
a_min = 0
a_max = 12 * math.pi / 6
FPS = 120

fig = plt.figure(figsize = (10, 6))
ax = fig.add_subplot(111, projection = '3d')

# from NTTS
def event_handler_decorator(event_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def handle_event(event):
                func(*args, **kwargs, event=event)
            fig = plt.gcf()
            fig.canvas.mpl_connect(event_type, handle_event)
            func(*args)
        return wrapper
    return decorator

animation = FuncAnimation(fig, update, fargs = (fig, ax, n, a_min, a_max), frames = FPS * 3, interval= 1000 / FPS)

@event_handler_decorator('close_event')
def plt_show_wrapper(event=None):
    print('不求向上，自甘中下。\n发自我的手机')

plt.show()
plt_show_wrapper()


