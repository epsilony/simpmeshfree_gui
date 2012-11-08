from matplotlib import pyplot as plt
import numpy as np
from simpmeshfree_gui import jvm_utils as ju
from jpype import *
from simpmeshfree_gui.pixcell_painter import *

def ori_demo():
   
    fig = plt.figure()
    fig.show()
    for smallbit in xrange(16):
        ax = fig.add_subplot(4, 4, smallbit + 1, aspect='equal')
        samples = ju.QuadPixcellAtomSample.refineSamples(0.0, 0.0, 5.0, smallbit)
        QuadPixcells_plot(samples, ax)
    fig.canvas.draw()
    return fig

def refine_demo():
    fig2 = plt.figure()
    fig2.show()
    for smallbit in xrange(16):
        ax2 = fig2.add_subplot(4, 4, smallbit + 1, aspect='equal')
        samples2 = ju.QuadPixcellAtomSample.refineSamples(0.0, 0.0, 5.0, smallbit)
        refined = samples2[0].refine()
        samples2 = [px for px in samples2]
        samples2.extend(refined[1:4])
        QuadPixcells_plot(samples2,ax2)
    fig2.canvas.draw()
    return fig2
    
def merge_after_ref_demo():
    fig = plt.figure()
    fig.show()
    for smallbit in xrange(16):
        ax = fig.add_subplot(4, 4, smallbit + 1, aspect='equal')
        samples = ju.QuadPixcellAtomSample.refineSamples(0.0, 0.0, 5.0, smallbit)
        refined = samples[0].refine()
        samples = [px for px in samples]
        samples.extend(refined[1:4])
        merged = samples[0].merge()
        for px in merged[1:4]:
            samples.remove(px)
        QuadPixcells_plot(samples, ax)
    fig.canvas.draw()
    return fig

if __name__ == "__main__":
    ju.start_jvm(debug_port=8998)
     
    fig1 = ori_demo()
    
    fig2 = refine_demo()
    
    fig3 = merge_after_ref_demo()
    
