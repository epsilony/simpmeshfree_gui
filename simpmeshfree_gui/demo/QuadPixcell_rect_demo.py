from matplotlib import pyplot as plt
import numpy as np
from jpype import JPackage
from simpmeshfree_gui.jvm_utils import start_jvm
from simpmeshfree_gui.pixcell_painter import *

def refine_and_plot(manager,ax1,ax2):
    refined=manager.refine(False)
    ax1.clear()
    ax2.clear()
    QuadPixcells_plot(manager.pxes,ax1,shrink=0)
    QuadPixcells_plot(refined,ax2,shrink=0)
    
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(ax2.get_ylim())
    fig.canvas.draw()

def merge_and_plot(manager,ax1,ax2):
    merged=manager.merge(False)
    ax1.clear()
    ax2.clear()
    QuadPixcells_plot(manager.pxes,ax1,shrink=0)
    QuadPixcells_plot(merged,ax2,shrink=0)
    
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(ax2.get_ylim())
    fig.canvas.draw()


if __name__=='__main__':
    start_jvm(debug_port=8998)
    J_sample_cls=JPackage('net').epsilony.simpmeshfree.adpt2d.sample.QuadPixcellRectangleSample
    QuadPixcellManager=JPackage('net').epsilony.simpmeshfree.adpt2d.QuadPixcellManager
    LocationAdaptiveFilter=JPackage('net').epsilony.simpmeshfree.adpt2d.sample.LocationAdaptiveFilter
    fig=plt.figure()
    ax1=fig.add_subplot(121,aspect='equal')
    ax2=fig.add_subplot(122,aspect='equal')
    (x0,y0,w,h,scale)=(2.0,1.0,15.0,10.0,5.0)
    pxes=J_sample_cls.genPixcells(x0,y0,w,h,scale)
    
    #QuadPixcells_plot(pxes,ax1)
    
    fig.show()
    
    af=LocationAdaptiveFilter()
    af.addRefinePt(7.1,5.1)
    af.addMergeRect(x0-0.1,y0-0.1,w+0.2,h+0.2)
    manager=QuadPixcellManager(pxes,af)
    
#    m_a_12=(manager,ax1,ax2)
    
    ti=7
    for i in range(ti-1):
        manager.refine(False)
    refine_and_plot(manager, ax1, ax2)

    fig2=plt.figure()
    ax21=fig2.add_subplot(121,aspect='equal')
    ax22=fig2.add_subplot(122,aspect='equal')
    
    merge_and_plot(manager,ax21,ax22)
    fig2.show()
    
    
    fig3=plt.figure()
    ax31=fig3.add_subplot(221,aspect='equal')
    #ax32=fig3.add_subplot(222,aspect='equal')
    ax33=fig3.add_subplot(223,aspect='equal')
    ax34=fig3.add_subplot(224,aspect='equal')
    pxes3=J_sample_cls.genPixcells(x0,y0,w,h,scale)
    manager3=QuadPixcellManager(pxes3,af)
    QuadPixcells_plot(pxes3,ax31)
    for i in range(ti):
        manager3.refine(False)
    for i in range(ti-1):
        manager3.merge(False)
    merge_and_plot(manager3,ax33,ax34)
    fig3.show()
    