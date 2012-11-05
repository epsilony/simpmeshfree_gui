# -*- coding: utf-8 -*-

'''
Created on 2012-5-25

@author: epsilon
'''
from simpmeshfree_gui.jvm_utils import *
from jpype import *
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import numpy as np
if __name__ == '__main__':
    start_jvm(debug_port=8998)
    BTU=JPackage('net').epsilony.simpmeshfree.model.test.BoundaryUtilsTestUtils
    Node=JPackage('net').epsilony.utils.geom.Node
    center=Node(12.45,-20.8)
    rad=9.0
    theta=np.pi*2.1/3
    distances=[rad,rad-1,rad+1]
    colors=['red','green','black']
    lines=[np.array(BTU.genLine2DPerpendicularTo(center,theta,d,-rad,-rad/2)) for d in distances]
    fig=plt.figure()
    ax=fig.add_subplot(111)
    idx=0
    for line in lines:
        ax.plot((line[0],line[2]),(line[1],line[3]),color=colors[idx])
        idx+=1
    ax.add_patch(Circle((center.x,center.y),radius=rad))
    fig.canvas.draw()
    ax.set_aspect('equal')
    ax.autoscale()
    fig.show()