from jpype import JArray,java,JPackage,JClass,JInt
from simpmeshfree_gui.jvm_utils import start_jvm,iter_Iterable
from simpmeshfree_gui.plot2d import *
from simpmeshfree_gui.tools import JDoubleArrayList_to_np_array
import numpy as np

def exact_displacements(tBeam, coords):
    result=np.ndarray((coords.size(),2))
    i=0
    for coord in iter_Iterable(coords):
        result[i]=tBeam.getDisplacement(coord.x,coord.y,None)
        i+=1
    return result

def nodesValue(processer):
    ndsRes=processor.getNodesValue()
    sz=ndsRes.size()/2
    result=np.ndarray((sz,2))
    for i in xrange(sz):
        result[i]=(ndsRes.get(i*2),ndsRes.get(i*2+1))
    return result

if __name__=='__main__':
    start_jvm(debug_port=8998)
    QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
    WU=JClass('net.epsilony.simpmeshfree.model2d.test.WeakformProcessor2DDemoUtils')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    TimoshenkoBeam=JClass('net.epsilony.simpmeshfree.model2d.TimoshenkoExactBeam2D')
    PostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
    pipe=WU.newPipe()
    processor=WU.timoshenkoBeam(pipe)    
    JIntArray=JArray(JInt)
    qp=QuadraturePoint()
    coords=java.util.LinkedList()
    outNum=JIntArray([0])
    workPb=pipe.workProblem
    tBeam=workPb.tBeam
    volIter=workPb.volumeIterator(outNum)
    
    while(volIter.next(qp)):
        coords.add(Node(qp.coordinate))
        
    
    processor.process(1)
    processor.solveEquation()
    
    nds=pipe.geomUtils.allNodes
    ndsVal=nodesValue(processor)
    
    postProcessor=PostProcessor(processor.shapeFunFactory.factory(),processor.getNodesValue())
    ndsExactRes=exact_displacements(tBeam,nds)
    
    qpResult=JDoubleArrayList_to_np_array(postProcessor.result(coords,None))
    
    coords=java.util.LinkedList()
    bnds=java.util.LinkedList()
    diriIter=workPb.dirichletIterator(None)
    while(diriIter.next(qp)):
        coord=Node(qp.coordinate)
        bnd=qp.boundary
        coords.add(coord)
        bnds.add(bnd)
        pass
    diriRes=postProcessor.result(coords,bnds)
    diriRes=JDoubleArrayList_to_np_array(diriRes)
    diriExp=np.ndarray((coords.size(),2))
    diriIter=workPb.dirichletIterator(None)
    i=0
    while(diriIter.next(qp)):
        coord=qp.coordinate
        diriExp[i]=tBeam.getDisplacement(coord.x,coord.y,None)
        i+=1
        pass