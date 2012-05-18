import simpmeshfree_gui.triangle as triangle
import simpmeshfree_gui.samples as samples
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
def handle_close(evt):
    print evt.x, evt.y

if __name__ == '__main__':
#    in_io=samples.gen_triangulateio_in();
#    out_io=triangle.Triangulateio();   
#    triangle.triangulate("zpqa13D",in_io,out_io)
    
    out_io = samples.gen_triangulateio_out(quality_area=13)
    plt.ioff()
    fig = plt.figure(1)
    ax = fig.add_subplot(111, aspect='equal')
    colors = ['grey', 'black', 'red', 'blue', 'orange', 'purple']
    for i in xrange(out_io.numberofsegments):
        pts = out_io.pointlist
        sgs = out_io.segmentlist
        ax.plot([pts[sgs[i * 2] * 2], pts[sgs[i * 2 + 1] * 2]], [pts[sgs[i * 2] * 2 + 1], pts[sgs[i * 2 + 1] * 2 + 1]], color=colors[out_io.segmentmarkerlist[i]])
    fig.canvas.mpl_connect('close_event', handle_close)
    fig.show()
    
    paths_ = triangle.gen_paths(out_io)
    
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111, aspect='equal')
    for mark in paths_:
        ax2.add_patch(PathPatch(paths_[mark], fill=False, lw=2, color=colors[mark]))
    ax2.autoscale()
    fig2.canvas.mpl_connect('close_event', handle_close)
    fig2.show()
    
    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(111, aspect='equal')
    ax3.add_patch(PathPatch(samples.gen_compound_path(quality_area=13), lw=1, color='yellow', alpha=0.5))
    ax3.autoscale()
    fig3.canvas.mpl_connect('close_event', handle_close)
    fig3.show()
    plt.show()

    
