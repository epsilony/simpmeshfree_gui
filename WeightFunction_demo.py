import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from simpmeshfree_gui.jvm_utils import start_jvm
from jpype import JClass,java

import numpy as np

if __name__=='__main__':
    start_jvm(debug_port=8998)
    TriSpline=JClass('net.epsilony.simpmeshfree.model.WeightFunctions$TriSpline')
    SimpPower=JClass('net.epsilony.simpmeshfree.model.WeightFunctions$SimpPower')
    Common=JClass('net.epsilony.simpmeshfree.model.DistanceFunctions$Common')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    WeightFunctions=JClass('net.epsilony.simpmeshfree.model.WeightFunctions')
    #w_fun=WeightFunctions.factory(SimpPower(2),Common())
    w_fun=WeightFunctions.factory(TriSpline(),Common())
    w_fun.setDiffOrder(1)
    w_fun.distFun.setCenter(Node(0.0,0.0))
    xs=np.arange(-2.0,2.0,0.1)
    ys=np.arange(-2.0,2.0,0.1)
    (xs,ys)=np.meshgrid(xs,ys)
    ArrayList=java.util.ArrayList
    nds=ArrayList(xs.shape[0]*xs.shape[1])
    for i in xrange(xs.shape[0]):
        for j in xrange(xs.shape[1]):
            nds.add(Node(xs[i][j],ys[i][j]))
    
    res=w_fun.values(nds,2.0,None)
    
    zs=np.ndarray(xs.shape)
    zs_x=np.ndarray(xs.shape)
    zs_y=np.ndarray(xs.shape)
    for i in xrange(xs.shape[0]):
        for j in xrange(xs.shape[1]):
            vals=res.get(i*xs.shape[0]+j)
            zs[i][j]=vals.get(0)
            zs_x[i][j]=vals.get(1)
            zs_y[i][j]=vals.get(2)

    fig=plt.figure()
    zs_s=(zs,zs_x,zs_y)
    colors=('red','green','blue')
    ax_s=[];
    for i in xrange(3):
        ax=fig.add_subplot(2,2,i+1,projection='3d',aspect='equal')
        ax.plot_surface(xs,ys,zs_s[i],color=colors[i])
        ax.autoscale()
        ax.set_xlabel('x')
        ax_s.append(ax)
    fig.canvas.draw()
    fig.show()