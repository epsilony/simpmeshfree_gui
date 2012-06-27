from jpype import JArray,java,JPackage,JClass,JInt
from simpmeshfree_gui.jvm_utils import start_jvm,iter_Iterable
from simpmeshfree_gui.plot2d import *
from simpmeshfree_gui.tools import JDArr_List_2_np,JTDList_List_2_np
from simpmeshfree_gui.demo.PostProcessor_demo_tool import *
import numpy as np
import math
import matplotlib.pyplot as plt
        
if __name__=='__main__':
    start_jvm(debug_port=8998)
    QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    TimoshenkoBeam=JClass('net.epsilony.simpmeshfree.model2d.TimoshenkoExactBeam2D')
    PostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
    CommonUtils=JPackage('net').epsilony.simpmeshfree.utils.CommonUtils
    Monitors=JPackage('net').epsilony.simpmeshfree.model.WeakformProcessorMonitors
    
    iterativeSolver=False
    isSimpAsm=False
    core_num=1;
    monitors=java.util.ArrayList()
    monitors.add(Monitors.recorder())
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
    
    ndsExactRes=exact_displacements(tBeam,nds)
    
    smpCoords=sample_Coords(tBeam.width,tBeam.height)
    
    smpExactDisps=exact_displacements(tBeam,smpCoords)
    smpDispTDLists=postProcessor.displacements(smpCoords,None,1)
    smpDisps=JTDList_List_2_np(smpDispTDLists.subList(0,2)).transpose()
    
    smpStrainTDList=PostProcessor.strain2D(smpDispTDLists,2)
    smpStrain=JTDList_List_2_np(smpStrainTDList).transpose()
    smpExactStrain=exact_strain(tBeam, smpCoords)
    
    smpStressTDList=PostProcessor.stress2D(smpDispTDLists,2,conLaw)
    smpStress=JTDList_List_2_np(smpStressTDList).transpose()
    smpExactStress=exact_stress(tBeam,smpCoords)
    
    (fig_disp,ax_disp,output_xs_disp,output_ys_disp,output_labels_disp)=plot_on_line(tBeam,postProcessor)
    (fig_strain,ax_strain,output_xs_strain,output_ys_strain,output_labels_strain)=plot_on_line(tBeam,postProcessor,x=tBeam.width/2.0,y=None,val_type='strain')
    (fig_stress,ax_stress,output_xs_stress,output_ys_stress,output_labels_stress)=plot_on_line(tBeam,postProcessor,x=tBeam.width/2.0,y=None,val_type='stress',conLaw=conLaw)