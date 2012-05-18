from collections import deque
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle
from simpmeshfree_gui.jvm_utils import iter_Iterable
import numpy as np
from jpype import java, JClass

def merge_paths(*args):
    len_vs = 0
    len_cs = 0
    for path in args:
        len_vs += path.vertices.shape[0]
        len_cs += path.codes.shape[0]
    vertices = np.ndarray((len_vs, 2), dtype=np.double)
    codes = np.ndarray((len_cs,), dtype=Path.code_type)
    len_vs = 0
    len_cs = 0
    for path in args:
        vertices[len_vs:len_vs + path.vertices.shape[0], :] = path.vertices[:, :]
        codes[len_cs:len_cs + path.codes.shape[0]] = path.codes[:]
        len_vs += path.vertices.shape[0]
        len_cs += path.codes.shape[0]
    return Path(vertices, codes)

def gen_boundary_path(bndList):
    nds_link = {}
    for i in xrange(bndList.size()):
        bnd = bndList.get(i)
        start = bnd.start
        end = bnd.end
        if start in nds_link:
            nds_link[start][1] = end
        else:
            nds_link[start] = [None, end]
        if end in nds_link:
            nds_link[end][0] = start
        else:
            nds_link[end] = [start, None]
    
    nds_num = len(nds_link)
    nodes = deque()
    codes = deque()
    while len(nds_link) > 0 :
        nds = deque()
        cds = deque()
        start_nd = nds_link.iterkeys().next()
        lnk = nds_link[start_nd]
        nds.append(start_nd)
        cds.append(Path.LINETO)
        if lnk[1] is not None:
            sort = 1
        else:
            sort = 0
        next_nd = lnk[sort]
        while next_nd is not None:
            nds.append(next_nd)
            cds.append(Path.LINETO)
            if next_nd.getId() == start_nd.getId():
                break;
            if len(cds) > nds_num + 1:
                raise Exception('Wrong path input, there may be sub rings in a path')
            next_nd = nds_link[next_nd][sort]
        
        if next_nd is None:
            sort2 = 1 - sort
            next_nd = lnk[sort2]
            while next_nd is not None:
                nds.appendleft(next_nd)
                cds.appendleft(Path.LINETO)
                if len(cds) > nds_num + 1:
                    raise Exception('Wrong path input, there may be sub rings in a path')
                next_nd = nds_link[next_nd][sort2]
        
        if sort != 1:
            nds.reverse()
            cds.reverse()
        cds[0] = Path.MOVETO
        nds_iter = iter(nds)
        if next_nd is not None:
            cds[-1] = Path.CLOSEPOLY
            nds_iter.next()
        for nd in nds_iter:
            nds_link.pop(nd)
        
        nodes.extend(nds)
        codes.extend(cds)
        
        
    points = np.ndarray((len(nodes), 2), dtype=np.double)
    i = 0
    for nd in nodes:
        points[i][:] = (nd.x, nd.y)
        i += 1
    return Path(points, codes)

def get_x_y(nodeList):
    x = deque()
    y = deque()
    for nd in iter_Iterable(nodeList):
        x.append(nd.x)
        y.append(nd.y)
    return (x, y)

class _Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __cmp__(self, other):
        if not isinstance(other, type(self)):
            return -1
        if self.x < other.x:
            return -1
        elif self.x > other.x:
            return 1
        elif self.y < other.y:
            return -1
        elif self.y > other.y:
            return 1
        else:
            return 0
        
    
    def __hash__(self):
        return int(self.x * self.y)
    

def gen_net_path(itemList):
    pt_lnk = {}
    points = deque()
    Triangle = JClass('net.epsilony.utils.geom.Triangle')
    Quadrangle = JClass('net.epsilony.utils.geom.Quadrangle')
    for item in iter_Iterable(itemList):
        if isinstance(item, Triangle):
            tri = item
            pts = (_Point(tri.c1.x, tri.c1.y),
                 _Point(tri.c2.x, tri.c2.y),
                 _Point(tri.c3.x, tri.c3.y))
            pts_len = 3;
        elif isinstance(item, Quadrangle):
            quad = item
            pts = (_Point(quad.x1, quad.y1),
                 _Point(quad.x2, quad.y2),
                 _Point(quad.x3, quad.y3),
                 _Point(quad.x4, quad.y4))
            pts_len = 4;
        for i in xrange(pts_len):
            (p_start, p_end) = (pts[i], pts[(i + 1) % pts_len])
            if p_start > p_end:
                t = p_end;
                p_end = p_start
                p_start = t
            if not p_start in pt_lnk:
                pt_lnk[p_start] = set()
            pt_lnk[p_start].add(p_end)
    for start_pt in pt_lnk:
        for end_pt in pt_lnk[start_pt]:
            points.extend((start_pt.x, start_pt.y))
            points.extend((end_pt.x, end_pt.y))
    vertices = np.array(points, dtype=np.double).reshape((len(points) / 2, 2))
    codes = np.ndarray((len(points) / 2,), dtype=Path.code_type)
    codes[::2] = Path.MOVETO
    codes[1::2] = Path.LINETO
    return Path(vertices, codes)

class GeomUtilsPainter(object):
    def __init__(self, axes, geomUtils):
        self.axes = axes
        self.geomUtils = geomUtils
        
        self.bnd_patch = None
        self.bnd_patch_setting = {'edgecolor':'black', 'facecolor':'#EFEFEF', 'animated':False, 'alpha':0.8, 'zorder':0, 'animated':False}
        
        self.bnd_nds_clt = None
        self.bnd_nds_clt_setting = {'s':8, 'edgecolor':'black', 'facecolor':'white', 'alpha':0.9, 'zorder':0.5, 'animated':False}
        
        self.space_nds_clt = None
        self.space_nds_clt_setting = {'s':8, 'edgecolor':'black', 'facecolor':'grey', 'zorder':0.5, 'animated':False}
    
    def clear(self):
        ax = self.axes
        if self.bnd_patch is not None:
            ax.patches.remove(self.bnd_patch)
            self.bnd_patch = None
        if self.bnd_nds_clt is not None:
            ax.collections.remove(self.bnd_nds_clt)
            self.bnd_nds_clt = None
        if self.space_nds_clt is not None:
            ax.collections.remove(self.space_nds_clt)
            self.space_nds_clt = None

    def draw(self):
        self.axes.figure.canvas.draw()
    
    def plot(self):
        self.clear()
        ax = self.axes
        geomUtils = self.geomUtils
        bndList = geomUtils.boundaries
        spaceNodes = geomUtils.spaceNodes
        bndNodes = geomUtils.allNodes.subList(0, geomUtils.bndNodeNum)
        
        path = gen_boundary_path(bndList)
        self.bnd_patch = PathPatch(path, **(self.bnd_patch_setting))
        ax.add_patch(self.bnd_patch)
        
        (x, y) = get_x_y(spaceNodes)
        self.space_nds_clt = ax.scatter(x, y, **(self.space_nds_clt_setting))
        
        (x, y) = get_x_y(bndNodes)
        self.bnd_nds_clt = ax.scatter(x, y, **(self.bnd_nds_clt_setting))
        
class SupportDomainPainter(object):
    def __init__(self, axes, geomUtils):
        self.geomUtils = geomUtils
        self.axes = axes
        self.bnds_patch = None
        self.center_pt_clt = None
        self.space_nds_clt = None
        self.bnds_nds_clt = None
        self.domain_nds_clt = None
        self.circle = None
        self.visible_status_patch_b1 = None
        self.visible_status_patch_b2 = None
        
        self.bnds_patch_setting = {'color':'brown', 'fill':False, 'lw':2}#, 'animated':True}
        self.space_nds_setting = {'s':20, 'facecolor':'blue', 'edgecolor':'red', 'zorder':2}#, 'animated':True}
        self.bnds_nds_setting = {'s':20, 'facecolor':'blue', 'edgecolor':'yellow', 'zorder':2}#, 'animated':True}
        self.center_pt_setting = {'s':20, 'marker':'+', 'c':'red', 'zorder':3}#, 'animated':True}
        self.circle_setting = {'color':'orange', 'fill':False, 'alpha':0.5, 'zorder':1}#, 'animated':True}
        self.domain_nds_setting = {'s':10, 'marker':'7', 'c':'pink', 'zorder':2.5}
        self.visible_status_patch_b1_setting = {'color':'blue', 'lw':2, 'zorder':2, 'alpha':0.5}
        self.visible_status_patch_b2_setting = {'color':'blue', 'lw':3, 'zorder':2, 'alpha':0.4}
        
        TIntArrayList = JClass('gnu.trove.list.array.TIntArrayList')
        self.nodeBlockNums = TIntArrayList(100)
        self.nodeBlockBndIdx = TIntArrayList(100)
        
    
    def clear(self):
        if self.bnds_patch is not None:
            self.axes.patches.remove(self.bnds_patch)
            self.bnds_patch = None
        if self.center_pt_clt is not None:
            self.axes.collections.remove(self.center_pt_clt)
            self.center_pt_clt = None
        if self.space_nds_clt is not None:
            self.axes.collections.remove(self.space_nds_clt)
            self.space_nds_clt = None
        if self.bnds_nds_clt is not None:
            self.axes.collections.remove(self.bnds_nds_clt)
            self.bnds_nds_clt = None
        if self.circle is not None:
            self.axes.patches.remove(self.circle)
            self.circle = None
        if self.domain_nds_clt is not None:
            self.axes.collections.remove(self.domain_nds_clt)
            self.domain_nds_clt = None
        if self.visible_status_patch_b1 is not None:
            self.axes.patches.remove(self.visible_status_patch_b1)
            self.visible_status_patch_b1 = None
        if self.visible_status_patch_b2 is not None:
            self.axes.patches.remove(self.visible_status_patch_b2)
            self.visible_status_patch_b2 = None
    
    def draw(self):
        self.axes.figure.canvas.draw()
    
    def plot(self, centerCoord, radius=None, spaceNodes=None, bndList=None):
        ax = self.axes
        self.clear()
        
        self.center_pt_clt = ax.scatter(centerCoord.x, centerCoord.y, **(self.center_pt_setting))
        
        domainNodes = None
        if radius is None:
            domainNodes = java.util.LinkedList()
            radius = self.geomUtils.domain(centerCoord, domainNodes)
        self.circle = Circle((centerCoord.x, centerCoord.y), radius, **(self.circle_setting))
        ax.add_patch(self.circle)
        if domainNodes is not None:
            (x, y) = get_x_y(domainNodes)
            self.domain_nds_clt = ax.scatter(x, y, **(self.domain_nds_setting))
        
        if bndList is None:
            bndList = self.geomUtils.searchBoundary(centerCoord, radius, None)
        path = gen_boundary_path(bndList)
        self.bnds_patch = PathPatch(path, **(self.bnds_patch_setting))
        ax.add_patch(self.bnds_patch)
        bndNodes = self.geomUtils.getBndsNodes(bndList, None)
        (x, y) = get_x_y(bndNodes)
        self.bnds_nds_clt = ax.scatter(x, y, **(self.bnds_nds_setting))
        
        if spaceNodes is None:
            spaceNodes = self.geomUtils.searchSpaceNodes(centerCoord, radius, None)
        (x, y) = get_x_y(spaceNodes)
        self.space_nds_clt = ax.scatter(x, y, **(self.space_nds_setting))
        
        (path1, path2) = self._gen_visibility_path(centerCoord, spaceNodes, bndList, False)
        (path1_2, path2_2) = self._gen_visibility_path(centerCoord, bndNodes, bndList, True)
        
        path1 = merge_paths(path1, path1_2)
        path2 = merge_paths(path2, path2_2)
        self.visible_status_patch_b1 = ax.add_patch(PathPatch(path1, **(self.visible_status_patch_b1_setting)))
        self.visible_status_patch_b2 = ax.add_patch(PathPatch(path2, **(self.visible_status_patch_b2_setting)))
        
    def _gen_visibility_path(self, center, nds, bnds, is_bnd_nds):
        self.geomUtils.visibleStatus(center, nds, bnds, self.nodeBlockNums, self.nodeBlockBndIdx, is_bnd_nds)
        blocked_once_nds = deque()
        blocked_once_bnds = deque()
        blocked_more_nds = deque()
        blocked_more_bnds = deque()
        for i in xrange(nds.size()):
            blockNum = self.nodeBlockNums.get(i)
            if blockNum == 1:
                blocked_once_nds.append(nds.get(i))
                bndIdx = self.nodeBlockBndIdx.get(i)
                blocked_once_bnds.append(bnds.get(bndIdx))
            elif blockNum > 1:
                blocked_more_nds.append(nds.get(i))
                bndIdx = self.nodeBlockBndIdx.get(i)
                blocked_more_bnds.append(bnds.get(bndIdx))
        path_len = 2 * len(blocked_once_nds)
        vertices = np.ndarray((path_len, 2), dtype=np.double)
        i = 0
        bnd_iter = iter(blocked_once_bnds)
        for nd in blocked_once_nds:
            vertices[i * 2, 0] = nd.x
            vertices[i * 2, 1] = nd.y
            bnd = bnd_iter.next()
            bnd_center = self.geomUtils.bndCenters.get(bnd.getId())
            vertices[i * 2 + 1, 0] = bnd_center.x
            vertices[i * 2 + 1, 1] = bnd_center.y
            i += 1
        codes = np.ndarray((path_len,), dtype=Path.code_type)
        codes[0::2] = Path.MOVETO
        codes[1::2] = Path.LINETO
        path_1 = Path(vertices, codes)
        
        path_len = 2 * len(blocked_more_nds)
        vertices = np.ndarray((path_len, 2), dtype=np.double)
        i = 0
        bnd_iter = iter(blocked_more_bnds)
        for nd in blocked_more_nds:
            vertices[i * 2, 0] = nd.x
            vertices[i * 2, 1] = nd.y
            bnd = bnd_iter.next()
            bnd_center = self.geomUtils.bndCenters.get(bnd.getId())
            vertices[i * 2 + 1, 0] = bnd_center.x
            vertices[i * 2 + 1, 1] = bnd_center.y
            i += 1
        codes = np.ndarray((path_len,), dtype=Path.code_type)
        codes[0::2] = Path.MOVETO
        codes[1::2] = Path.LINETO
        path_2 = Path(vertices, codes)
        
        return (path_1, path_2)
        
