from matplotlib.path import Path
import numpy as np
from jpype import JClass, JDouble
from collections import deque
from simpmeshfree_gui.jvm_utils import iter_Iterable

def path_ccw(pth, err=1e-6):
    path_iter = pth.iter_segments()
    pt_fst = path_iter.next()[0]
    pt1 = pt_fst[0]
    pt2 = path_iter.next()[0]
    ccw_sum = 0
    for seg in path_iter:
        pt3 = seg[0]
        if seg[1] == Path.CLOSEPOLY:
            pt3 = pt_fst
        v12 = pt2 - pt1
        v23 = pt3 - pt2
        cross = np.cross(v12, v23)
        uni_cross = cross / (np.dot(v12, v12) * np.dot(v23, v23)) ** 0.5
        if np.abs(uni_cross) > err:
            ccw_sum += np.sign(uni_cross)
        pt1 = pt2
        pt2 = pt3
    return ccw_sum

def reverse_path(pth):
    v = pth.vertices
    c = pth.codes
    new_v = v[::-1]
    new_c = c[::-1]
    if new_c[0] == Path.CLOSEPOLY:
        new_c[0] = Path.MOVETO
        new_v[0] = v[0]
    if new_c[-1] == Path.MOVETO:
        new_c[-1] = Path.CLOSEPOLY
    return Path(new_v, new_c)

def path_to_LineBoundary(pth):
    Node = JClass('net.epsilony.utils.geom.Node')
    LineBoundary = JClass('net.epsilony.simpmeshfree.model.LineBoundary')
    lines = deque()
    for segment in pth.iter_segments():
        if segment[1] == Path.MOVETO:
            start_node = Node(JDouble(segment[0][0]), JDouble(segment[0][1]))
            poly_start_node = start_node;
            continue
        elif segment[1] == Path.CLOSEPOLY:
            end_node = poly_start_node
        else:
            end_node = Node(JDouble(segment[0][-2]), JDouble(segment[0][-1]))
        lines.append(LineBoundary(start_node, end_node))
        start_node = end_node
    return lines

def print_np_array(arr):
    shape=arr.shape;
    print '{'
    for i in xrange(shape[0]):
        print '{',
        for j in xrange(shape[1]):
            print arr[i][j],
            if j != shape[1]-1:
                print ',',
            elif i!=shape[0]-1:
                print '},'
            else:
                print '}',
    print '}'

def JDArr_List_2_np(ds):
    result=np.ndarray((ds.size(),len(ds.get(0))))
    i=0
    for d in iter_Iterable(ds):
        result[i]=d
        i+=1
    return result;

def JTDList_List_2_np(tds):
    res=np.ndarray((tds.size(),tds.get(0).size()))
    for i in xrange(tds.size()):
        res[i]=np.array(tds.get(i).toArray())
    return res

def JTDList_Array_2_np(tds):
    res=np.ndarray((len(tds),tds[0].size()))
    for i in xrange(len(tds)):
        res[i]=np.array(tds[i].toArray())
    return res

def Coordinate_2_np_array(coord):
    return np.array([coord.x,coord.y,coord.z])