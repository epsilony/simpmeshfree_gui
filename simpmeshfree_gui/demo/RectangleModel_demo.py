# coding: utf-8
from simpmeshfree_gui.jvm_utils import start_jvm

from jpype import JClass
from simpmeshfree_gui.plot2d import GeomUtilsPainter, gen_net_path
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch

if __name__ == "__main__":
    start_jvm(debug_port=8998)
    RectangleModel = JClass('net.epsilony.simpmeshfree.model2d.RectangleModel')
    r_m = RectangleModel(100.0, 20.0, 5.0, 10.0)
    GeomUtils = JClass('net.epsilony.simpmeshfree.model.GeomUtils')
    gu = GeomUtils(r_m.boundaries(), r_m.spaceNodes(), 2)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    gu_p = GeomUtilsPainter(ax, gu)
    gu_p.plot()
    quads = r_m.quadrangles()
    pth = gen_net_path(quads)
    ax.add_patch(PathPatch(pth, color='red', fill=False, alpha=0.3))
    pth = gen_net_path(r_m.triangles())
    ax.add_patch(PathPatch(pth, color='red', fill=False, alpha=0.9, lw=2))
    ax.autoscale()
    gu_p.draw()
    
    fig.show()

