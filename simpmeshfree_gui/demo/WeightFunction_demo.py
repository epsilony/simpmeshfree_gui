import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from simpmeshfree_gui.jvm_utils import start_jvm
from jpype import JClass,java

import numpy as np

if __name__=='__main__':
    start_jvm(debug_port=8998)
    TriSpline=JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$TriSpline')
    SimpPower=JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$SimpPower')
    Common=JClass('net.epsilony.simpmeshfree.model.DistanceSquareFunctions$Common')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    WeightFunctions=JClass('net.epsilony.simpmeshfree.model.WeightFunctions')
    core_fun=TriSpline()
#    core_fun=SimpPower(2)
    
    w_fun=WeightFunctions.factory(core_fun,Common())
    w_fun.setDiffOrder(1)
    w_fun.distFun.setCenter(Node(0.0,0.0))
    xs=np.arange(-2.0,2.0,0.06)
    ys=np.arange(-2.0,2.0,0.06)
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
            i_j_index=i*xs.shape[0]+j
            
            zs[i][j]=res[0].get(i_j_index)
            zs_x[i][j]=res[1].get(i_j_index)
            zs_y[i][j]=res[2].get(i_j_index)

    fig=plt.figure()
    zs_s=(zs,zs_x,zs_y)
    colors=('red','green','blue')
    ax_s=[];
    for i in xrange(len(zs_s)):
        ax=fig.add_subplot(2,2,i+1,projection='3d',aspect='equal')
        ax.plot_surface(xs,ys,zs_s[i],color=colors[i])
        ax.autoscale()
        ax.set_xlabel('x')
        ax_s.append(ax)
    fig.canvas.draw()
    fig.show()