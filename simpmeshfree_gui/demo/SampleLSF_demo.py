from simpmeshfree_gui import jvm_utils as ju
import numpy as np
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt

if __name__=="__main__":
    ju.start_jvm(8998)
    coord=ju.Coordinate()
    sample=ju.SampleC1LSF()
    
    sample_ext_margin=0
    s_x0=sample.x0-sample_ext_margin
    s_y0=sample.y0-sample_ext_margin
    s_w=sample.w+sample_ext_margin*2
    s_h=sample.h+sample_ext_margin*2
    
    n_w=300
    n_h=500
    
    (X,Y)=np.meshgrid(np.linspace(s_x0, s_x0+s_w,n_w), np.linspace(s_y0,s_y0+s_h,n_h))
    
    
    Z=np.zeros_like(X,dtype=np.double)
    Z_x=np.zeros_like(X,dtype=np.double)
    Z_y=np.zeros_like(X,dtype=np.double)
    
    sample.setDiffOrder(1)
    for i in xrange(X.shape[0]):
        for j in xrange(X.shape[1]):
            coord.x=X[i,j]
            coord.y=Y[i,j]
            vals=sample.values(coord,None)
            Z[i,j]=vals[0]
            Z_x[i,j]=vals[1]
            Z_y[i,j]=vals[2]
    
    fig=plt.figure()
    
    Zs=(Z,Z_x,Z_y)
    for i in xrange(1):
        ax=fig.add_subplot(1,1,i+1,aspect='equal',projection='3d')
        ax.plot_surface(X,Y,Zs[i])
        offset = np.min(Z)-0.1
        cset=ax.contour(X,Y,Zs[i],[-1,0.0,1],zdir='z',offset=offset)
    
    fig.show()
    
    
    
    