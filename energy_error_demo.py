from jpype import JArray,java,JPackage,JClass,JInt
from simpmeshfree_gui.jvm_utils import start_jvm,iter_Iterable
from simpmeshfree_gui.plot2d import *
from simpmeshfree_gui.tools import JDArr_List_2_np,JTDList_List_2_np
import numpy as np
import math
import matplotlib.pyplot as plt
import sys
from simpmeshfree_gui.demo.PostProcessor_demo_tool import *
def get_k_size(assemblier):
    mat=assemblier.mainMatrix
    k_size=mat.numRows()-assemblier.dirichletNdsSize*2
    return k_size

def get_mat_k(assemblier):
    mat=assemblier.mainMatrix
    k_size=get_k_size(assemblier)
    
    mat_k=np.ndarray((k_size,k_size))
    for me in iter_Iterable(mat):
        row=me.row()
        col=me.column()
        if me.row()<k_size and me.column()<k_size:
            val=me.get()
            mat_k[row,col]=val
            mat_k[col,row]=val
    return mat_k

if __name__=='__main__':
    ben_debug=False
    for arg in sys.argv:
        if arg.find('no_debug')>-1:
            ben_debug=True
    debug_port=8998
    if(ben_debug):
        debug_port=None
    start_jvm(debug_port=debug_port)
    QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
    Node=JClass('net.epsilony.utils.geom.Node')
    TimoshenkoBeam=JClass('net.epsilony.simpmeshfree.model2d.TimoshenkoExactBeam2D')
    PostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
    CommonUtils=JPackage('net').epsilony.simpmeshfree.utils.CommonUtils
    Monitors=JPackage('net').epsilony.simpmeshfree.model.WeakformProcessorMonitors
    
    iterativeSolver=False
    isSimpAsm=False
    core_num=1;
    monitors=java.util.ArrayList()
    #monitors.add(Monitors.recorder())
    monitors.add(Monitors.simpLogger())
    monitor=Monitors.compact(monitors)
    
    (processor,pipe)=run_processor(iterativeSolver=iterativeSolver,isSimpAsm=isSimpAsm,core_num=core_num,monitor=monitor)

    qp=QuadraturePoint()
    conLaw=CommonUtils.toDenseMatrix64F(pipe.conLaw)   
    workPb=pipe.workProblem
    tBeam=workPb.tBeam 
    nds=pipe.geomUtils.allNodes
    ndsVal=nodesValue(processor)
    postProcessor=PostProcessor(processor.shapeFunFactory.factory(),processor.getNodesValue())    
    (volCoords,diriCoords,diriBnds,neumCoords,neumBnds)=problem_record_Lists(workPb)
    
    assemblier=processor.assemblier
    mat=assemblier.mainMatrix
    vec=assemblier.mainVector
    mat_k=get_mat_k(assemblier)
    k_size=get_k_size(assemblier)
    f=np.array([vec.get(i) for i in xrange(k_size)])
    ndsVals=processor.getNodesValue()
    u=np.array([ndsVals.get(i) for i in xrange(k_size)])
    
    
