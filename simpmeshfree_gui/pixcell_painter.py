'''
Created on 2012-9-24

@author: epsilon
'''
from matplotlib.lines import Line2D
import numpy as np
from simpmeshfree_gui.jvm_utils import *
from jpype import *
from matplotlib.patches import Circle

def QuadPixcell_node_shrink_pos(pixcell,shrink=0.3):
    xs=[]
    ys=[]
    for nd in pixcell.nodes:
        xs.append(nd.x)
        ys.append(nd.y)
    #shrink the nodes link lines inside ward
    for i in xrange(4):
        v=np.array((xs[(i+2) % 4]-xs[i],ys[(i+2)%4]-ys[i]))
        v=v/(np.dot(v,v)**0.5)*shrink
        xs[i]+=v[0]
        ys[i]+=v[1]
    return (xs,ys)


def QuadPixcell_node_link_pos(pixcell,shrink=0.3):
    (xs,ys)=QuadPixcell_node_shrink_pos(pixcell,shrink);
    xs.append(xs[0])
    ys.append(ys[0])
    return (xs,ys)

def QuadPixcell_neighbour_links(pixcell,shrink=0.3):
    (oxs,oys)=QuadPixcell_node_shrink_pos(pixcell,shrink)
    xs=[]
    ys=[]
    for i in xrange(4):
        v=np.array((oxs[(i+1)%4]-oxs[i],oys[(i+1)%4]-oys[i]))
        v=v*0.25
        xs.append(oxs[i]+v[0])
        ys.append(oys[i]+v[1])
    cxs=[]
    cys=[]
    for nb in pixcell.neighbours:
        if nb is None:
            cxs.append(None)
            cys.append(None)
            continue
        cx=0
        cy=0
        for nd in nb.nodes:
            cx+=nd.x
            cy+=nd.y
        cx/=4.0
        cy/=4.0
        cxs.append(cx)
        cys.append(cy)
    result=[]
    for i in xrange(4):
        if cxs[i] is None:
            continue
        result.append(([xs[i],cxs[i]],[ys[i],cys[i]]))
    return result
    
def QuadPixcells_nodes_pos(pxes):
    result=set()
    for px in pxes:
        for nd in px.nodes:
            result.add((nd.x,nd.y))
    return result

def QuadPixcell_plot(px,ax,shrink=0.3):
    (xs,ys)=QuadPixcell_node_link_pos(px,shrink)
    ax.plot(xs,ys)
    xsys=QuadPixcell_neighbour_links(px,shrink)
    for t in xsys:
        ax.plot(t[0],t[1])

def QuadPixcells_plot(pxes,ax,shrink=0.3,show_nds=False):
    for px in pxes:
        QuadPixcell_plot(px,ax,shrink)

    if(show_nds):
        nds_pos=QuadPixcells_nodes_pos(pxes)
        for pos in nds_pos:
            ax.add_artist(Circle(pos,radius=shrink*0.9,color='black',fill=False))
    ax.autoscale_view()