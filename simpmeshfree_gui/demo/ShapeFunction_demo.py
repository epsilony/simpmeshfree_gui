import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from simpmeshfree_gui.jvm_utils import start_jvm
from jpype import JClass,java,JPackage,JInt
import numpy as np

if __name__=='__main__':
    start_jvm(debug_port=8998)
    TriSpline=JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$TriSpline')
    SimpPower=JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$SimpPower')
    Common=JClass('net.epsilony.simpmeshfree.model.DistanceFunctions$Common')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    TDoubleArrayList=JClass('gnu.trove.list.array.TDoubleArrayList')
    WeightFunctions=JClass('net.epsilony.simpmeshfree.model.WeightFunctions')
    WeightFunctionTestUtils=JPackage('net').epsilony.simpmeshfree.model2d.test.WeightFunctionTestUtils
    TU=WeightFunctionTestUtils
    LinkedList=java.util.LinkedList
    ArrayList=java.util.ArrayList
    
    (xMin,yMin,xMax,yMax,ndNum,isDist)=(0.0,0.0,1.0,1.0,80.0,False)
    centerNum=400.0
    supRad=30.0
    baseOrder=4
    weightCore=TriSpline()
    
    xys=LinkedList()
    expFun=TU.genExpFun("c")
    resNds=ArrayList()
    
    nds=TU.genNodes(xMin,yMin,xMax,yMax,ndNum,isDist)
    centers=TU.genNodes(xMin,yMin,xMax,yMax,centerNum,isDist,xys)
    xs=xys.get(0)
    ys=xys.get(1)
    xs=np.array(xs,dtype=np.double)
    ys=np.array(ys,dtype=np.double)
    (xs,ys)=np.meshgrid(xs,ys)
    zs=np.ndarray(xs.shape,dtype=np.double)
    zs_x=np.ndarray(xs.shape,dtype=np.double)
    zs_y=np.ndarray(xs.shape,dtype=np.double)
    zs_exp=np.ndarray(xs.shape,dtype=np.double)
    zs_x_exp=np.ndarray(xs.shape,dtype=np.double)
    zs_y_exp=np.ndarray(xs.shape,dtype=np.double)
    
    shapeFun=TU.genShapeFunction(supRad,nds,baseOrder,weightCore)
    shapeFun.setDiffOrder(1)
    centersIterator=centers.iterator()
    shapeFunVals=ArrayList(3)
    for i in xrange(3):
        shapeFunVals.add(TDoubleArrayList())
    shapeFunVals=shapeFunVals.toArray()
    
    sum=0
    for i in xrange(xs.shape[0]):
        for j in xrange(xs.shape[1]):
            x=xs[i,j]
            y=xs[i,j]
            center=centersIterator.next()
            sum+=1
            if sum % 100 == 0:
                print sum
            shapeFunVals=shapeFun.values(center,None,None,resNds)
            value=TU.value(shapeFunVals,resNds,expFun)
            exp_val=expFun.value(center)
            zs[i,j]=value[0]
            zs_x[i,j]=value[1]
            zs_y[i,j]=value[2]
            zs_exp[i,j]=exp_val[0]
            zs_x_exp[i,j]=exp_val[1]
            zs_y_exp[i,j]=exp_val[2]
            
    fig=plt.figure(1)
    fig2=plt.figure(2)
    zs_s=(zs,zs_x,zs_y)
    zs_exp_s=(zs_exp,zs_x_exp,zs_y_exp)
    colors=('red','green','blue')
    colors2=('pink','brown','yellow')
    ax_s=[]
    ax_s2=[]
    for i in xrange(len(zs_s)):
        ax=fig.add_subplot(1,3,i+1,projection='3d',aspect='equal')
        ax.plot_surface(xs,ys,zs_s[i],color=colors[i])
        ax.autoscale()
        ax.set_xlabel('x')
        ax_s.append(ax)
        
        ax2=fig2.add_subplot(1,3,i+1,projection='3d',aspect='equal')
        ax2.plot_surface(xs,ys,zs_exp_s[i],color=colors2[i])
        ax2.autoscale()
        ax2.set_xlabel('x')
        ax_s2.append(ax2)
    fig.canvas.draw()
    fig.show()
    fig2.canvas.draw()
    fig2.show()