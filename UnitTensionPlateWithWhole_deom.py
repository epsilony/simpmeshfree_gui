import numpy as np
from jpype import *
from simpmeshfree_gui.jvm_utils import *
from simpmeshfree_gui.QuadrangleQDPainter import *
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.patches import Circle


def coord_patch(node,radius=0.5,fill=False):
    return Circle((node.x,node.y),radius=0.5,fill=fill)

def get_ndarray(mat):
    res=np.zeros((mat.numRows(),mat.numColumns()))
    iter_=mat.iterator()
    while(iter_.hasNext()):
        t=iter_.next()
        res[t.row(),t.column()]=t.get()
    return res

if __name__=="__main__":
    start_jvm(debug_port=8998)
    UniformTensionInfinitePlateSample=JPackage('net').epsilony.simpmeshfree.model2d.test.UniformTensionInfinitePlateSample
    sample_plate=UniformTensionInfinitePlateSample.simpSample()
    process=UniformTensionInfinitePlateSample.genSampleProcessor()
    quadrangles=sample_plate.getQuadrangles()
    
    fig=plt.figure()
    ax=fig.add_subplot(111,aspect='equal')
    
    for quad in quadrangles:
        xys=getShrinkVertes(quad)
        quad_polygon=Polygon(xys,fill=False)
        ax.add_patch(quad_polygon)
        
    ax.autoscale()
    #fig.show()
    
    qds=sample_plate.getQuadratureDomains()
    
    quadPower=4;
    
    sumArea=0.0
    
    Coordinate=JPackage('net').epsilony.utils.geom.Coordinate
    coord=Coordinate()
    for qd in qds:
        qd.setPower(quadPower)
        for i in xrange(qd.size()):
            sumArea+=qd.coordinateAndWeight(i,coord)
    
    print sumArea
    
    problem=sample_plate.getWeakformProblem(3)
    diriNds=problem.dirichletNodes()
    for nd in diriNds:
        ax.add_patch(coord_patch(nd))
    ax.autoscale()
    fig.canvas.draw()

    