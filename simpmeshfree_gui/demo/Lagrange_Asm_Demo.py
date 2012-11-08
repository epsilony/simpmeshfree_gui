from jpype import *
from simpmeshfree_gui import jvm_utils as ju
from simpmeshfree_gui.plot2d import *
from simpmeshfree_gui.tools import JDArr_List_2_np,JTDList_List_2_np
import numpy as np
import math
import matplotlib.pyplot as plt
import sys
from simpmeshfree_gui.demo.PostProcessor_demo_tool import *
        
if __name__=='__main__':
    ben_debug=False
    for arg in sys.argv:
        if arg.find('no_debug')>-1:
            ben_debug=True
    debug_port=8998
    if(ben_debug):
        debug_port=None
    ju.start_jvm(debug_port=debug_port)
    
    iterativeSolver=False
    isSimpAsm=False
    core_num=1;
    monitors=java.util.ArrayList()
    monitors.add(ju.WeakformProcessorMonitors.recorder())
    monitors.add(ju.WeakformProcessorMonitors.simpLogger())
    monitor=ju.WeakformProcessorMonitors.compact(monitors)
    
    (processor,pipe)=run_processor(iterativeSolver=iterativeSolver,isSimpAsm=isSimpAsm,core_num=core_num,monitor=monitor)

    qp=ju.QuadraturePoint()
    conLaw=ju.CommonUtils.toDenseMatrix64F(pipe.conLaw)   
    workPb=pipe.workProblem
    tBeam=workPb.tBeam 
    nds=pipe.geomUtils.allNodes
    ndsVal=nodesValue(processor)
    postProcessor=ju.CommonPostProcessor(processor.genShapeFunctionPacker(),processor.getNodesValue())    
    (volCoords,diriCoords,diriBnds,neumCoords,neumBnds)=problem_record_Lists(workPb)
    
    ndsExactRes=exact_displacements(tBeam,nds)  
    
    res=plot_on_line(tBeam,postProcessor,x=0.01)
    
    fig=plt.figure()
    titles=['u','v']
    for i in xrange(2):
        ax=fig.add_subplot(211+i)
        ax.plot(res[2],res[3][:,0],label='exact')
        ax.plot(res[2],res[3][:,6],'+',label='numerical')
        ax.set_title(titles[i])
        ax.legend()
    fig.show()
        
        
    
    
    