import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('png')   # тип хранения изображения (Векторная)


def get_vector(v1:[int, int, int], v2:[int, int, int]):
    p2 = np.array(v1) #blue vector
    p1 = np.array([0, 0, 0])
    p3 = np.array(v2)
    file = 'вектора.png'
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(np.linspace(p1[0], p2[0], 2), np.linspace(p1[1], p2[1], 2), np.linspace(p1[2], p2[2], 2), )
    ax.plot(np.linspace(p1[0], p3[0], 2), np.linspace(p1[1], p3[1], 2), np.linspace(p1[2], p3[2], 2), )
    fig.savefig(file)
    return file
