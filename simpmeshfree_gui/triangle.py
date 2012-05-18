# -*- coding: utf-8 -*-
"""
Created on Sun May  6 16:27:30 2012

@author: epsilon
"""

##TODO: refactor this file , divide the triangle io and sample model
##Hint: The sample model is a class , and has the function of get_path()
##get_line_segments() triangled_instance(quality_angle,quality_area)
##Hint: The triangle io must be wrapped in a function trianglulate(switch,in_io,out_io

from collections import deque
import numpy as np
from matplotlib.path import Path
from ctypes import Structure, POINTER, CDLL, c_double, c_int, c_char_p, pointer
import simpmeshfree_gui.tools as tools

class Triangulateio(Structure):
    _fields_ = [
        ("pointlist", POINTER(c_double)),
        ("pointattributelist", POINTER(c_double)),
        ("pointmarkerlist", POINTER(c_int)),
        ("numberofpoints", c_int),
        ("numberofpointattributes", c_int),
        
        ("trianglelist", POINTER(c_int)),
        ("triangleattributelist", POINTER(c_double)),
        ("trianglearealist", POINTER(c_double)),
        ("neighborlist", POINTER(c_int)),
        ("numberoftriangles", c_int),
        ("numberofcorners", c_int),
        ("numberoftriangleattributes", c_int),
        
        ("segmentlist", POINTER(c_int)),
        ("segmentmarkerlist", POINTER(c_int)),
        ("numberofsegments", c_int),
        
        ("holelist", POINTER(c_double)),
        ("numberofholes", c_int),
        
        ("regionlist", POINTER(c_double)),
        ("numberofregions", c_int),
        
        ("edgelist", POINTER(c_int)),
        ("edgemarkerlist", POINTER(c_int)),
        ("normlist", POINTER(c_double)),
        ("numberofedges", c_int),
    ]

def gen_paths(tri_io):
    segment_rings = {}
    for i in xrange(tri_io.numberofsegments):
        mark = tri_io.segmentmarkerlist[i]
        if not segment_rings.has_key(mark):
            segment_rings[mark] = deque()
        segment_rings[mark].append((tri_io.segmentlist[i * 2], tri_io.segmentlist[i * 2 + 1]))
    
    paths_ = {}
    for mark in segment_rings:
        ring = segment_rings[mark]
        pts_link = {}
        for seg in ring:
            idx_1 = seg[0]
            idx_2 = seg[1]
            if pts_link.has_key(idx_1):
                pts_link[idx_1][1] = idx_2
            else:
                pts_link[idx_1] = [idx_2, None]
            if pts_link.has_key(idx_2):
                pts_link[idx_2][1] = idx_1
            else:
                pts_link[idx_2] = [idx_1, None]
        points_id = deque()
        paths_[mark] = points_id
        fst = (pts_link.iterkeys()).next()
        pt_pred = fst
        pt = pts_link[fst][0]
        points_id.append(fst)
        while(True):
            points_id.append(pt)    
            pts = pts_link[pt]
            if pt_pred == pts[1]:
                pt_pred = pt
                pt = pts[0]
            else:
                pt_pred = pt
                pt = pts[1]
            if pt == fst:
                break
            if len(points_id) > tri_io.numberofsegments:
                print 'error'      #<<<+++++ throw something here!
        points_id.append(fst)
        points = deque()
        for idx in points_id:
            points.append(tri_io.pointlist[idx * 2])
            points.append(tri_io.pointlist[idx * 2 + 1])
        codes = np.ones(len(points_id)) * Path.LINETO
        codes[0] = Path.MOVETO
        codes[-1] = Path.CLOSEPOLY
        paths_[mark] = Path(np.array(points, dtype='float').reshape((len(points_id), 2)), codes)
    return paths_

def gen_compound_path(tri_io, ccw_demands):
    paths = gen_paths(tri_io)

    for mark in paths:
        path = paths[mark]

        ccw_dmnd = ccw_demands[mark]
        if ccw_dmnd == 0:
            continue
        ccw = tools.path_ccw(path)
        if ccw == 0 :
            continue
        if ccw_dmnd * ccw < 0:
            paths[mark] = tools.reverse_path(path)
    codes = deque()
    vertices = deque()
    for value in paths.itervalues():
        codes.extend(value.codes)
        vertices.extend(value.vertices)
    return Path(vertices, codes)

def triangulate(switches, in_io, out_io):
    libtriangle = CDLL("libtriangle.so")
    libtriangle.triangulate(c_char_p(switches), pointer(in_io), pointer(out_io))        

def gen_switches(quality_area=None, quality_angle=None, verbose=False):
    switches = 'zepDn'
    if not verbose:
        switches += 'Q'
    if not None is quality_angle:
        switches += 'q' + str(quality_angle)
    else:
        switches += 'q'
    if not None is quality_area:
        switches += 'a' + str(quality_area)
    return switches

#def trifree(out_io):
#    libtriangle=CDLL("libtriangle.so")
#    libtriangle.trifree(pointer(out_io))
    
    
