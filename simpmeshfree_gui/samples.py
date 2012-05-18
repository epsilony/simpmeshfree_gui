import simpmeshfree_gui.triangle as triangle
from ctypes import POINTER, cast, c_int, c_double
import simpmeshfree_gui.tools as tools
from jpype import JClass
from collections import deque
import numpy as np

class Sample1(object):
    def __init__(self):
        self.points = np.array([5, 5,
            105, 5,
            105, 65,
            5, 65,
            10, 10,
            11, 10,
            11, 60,
            10, 60,
            13, 25,
            14, 25,
            14, 60,
            13, 60,
            25, 20,
            25, 50,
            25.1, 50,
            25.1, 20,
            45, 15,
            90, 25,
            50, 30,
            100, 40,
            50, 45,
            85, 51,
            47, 50,
            75, 55,
            45, 55], dtype=np.double)
        self.segments = [0, 1,
                          1, 2,
                          2, 3,
                          3, 0,
                          4, 5,
                          5, 6,
                          6, 7,
                          7, 4,
                          8, 9,
                          9, 10,
                          10, 11,
                          11, 8,
                          12, 13,
                          13, 14,
                          14, 15,
                          15, 12,
                          16, 17,
                          17, 18,
                          18, 19,
                          19, 20,
                          20, 21,
                          21, 22,
                          22, 23,
                          23, 24,
                          24, 16]
        self.segments_marks = [1, 1, 1, 1,
                                2, 2, 2, 2,
                                3, 3, 3, 3,
                                4, 4, 4, 4,
                                5, 5, 5, 5, 5, 5, 5, 5, 5]
        self.hole_points = [10.5, 35,
                             13.5, 35,
                             25.05, 35,
                             50, 40]
        self.ccw = {1:1, 2:-1, 3:-1, 4:-1, 5:-1}
    
    def gen_segment_size_limited_instance(self, size):
        res = Sample1()
        segments = deque()
        segments_marks = deque()
        points = deque()
        points.extend(res.points)
        for i in xrange(len(self.segments_marks)):
            start_pt_id = self.segments[i * 2]
            end_pt_id = self.segments[i * 2 + 1]
            start_pt = np.array((self.points[start_pt_id * 2], self.points[start_pt_id * 2 + 1]))
            end_pt = np.array((self.points[end_pt_id * 2], self.points[end_pt_id * 2 + 1]))
            seg_len = np.dot(start_pt - end_pt, start_pt - end_pt)
            seg_len = np.sqrt(seg_len)
            seg_mark = self.segments_marks[i]
            
            if seg_len <= size:
                segments_marks.append(seg_mark)
                segments.extend((start_pt_id, end_pt_id))
                continue
            
            div_num = np.ceil(seg_len / size) + 1
            ts = np.linspace(0, 1, div_num)
            pt = start_pt * (1 - ts[1]) + end_pt * ts[1]
            points.extend(pt)
            segments.extend((start_pt_id, len(points) / 2 - 1))
            segments_marks.append(seg_mark)
            for t in ts[2:-1]:
                pt = start_pt * (1 - t) + end_pt * t
                points.extend(pt)
                segments.extend((len(points) / 2 - 2, len(points) / 2 - 1))
                segments_marks.append(seg_mark)
            segments.extend((len(points) / 2 - 1, end_pt_id))
            segments_marks.append(seg_mark)
        res.segments = list(segments)
        res.points = np.array(points, dtype=np.double)
        res.segments_marks = list(segments_marks)
        return res

def _gen_triangulateio(points, segments, segments_marks=None, hole_points=None):
    in_io = triangle.Triangulateio();
    in_io.pointlist = cast((c_double * (len(points)))(*points), POINTER(c_double))
    in_io.numberofpoints = c_int(len(points) / 2)
    in_io.segmentlist = cast((c_int * (len(segments)))(*segments), POINTER(c_int))
    if not None is segments_marks:
        in_io.segmentmarkerlist = cast((c_int * (len(segments_marks)))(*segments_marks), POINTER(c_int))
    in_io.numberofsegments = c_int(len(segments_marks))
    if not None is hole_points:
        in_io.holelist = cast((c_double * (len(hole_points)))(*hole_points), POINTER(c_double))
        in_io.numberofholes = c_int(len(hole_points) / 2)
    return in_io

class _SampleInstanceContainer(object):
    class_dict = {1:Sample1}
    
    class_instances = {}
    
    @classmethod
    def get_sample(cls, sample, size=None):
        if not cls.class_instances.has_key(sample):
            cls.class_instances[sample] = (cls.class_dict[sample])()
        if size is not None:
            cls.class_instances[sample] = cls.class_instances[sample].gen_segment_size_limited_instance(size)
        return cls.class_instances[sample]

def get_sample_instance(sample=1, size=None):
    return _SampleInstanceContainer.get_sample(sample, size)

def gen_triangulateio_in(sample=1, size=None):
    inst = get_sample_instance(sample, size);
    in_io = _gen_triangulateio(inst.points, inst.segments, inst.segments_marks, inst.hole_points)
    return in_io

def gen_compound_path(sample=1, size=None, quality_area=None, quality_angle=None, verbose=False, out_io_output=None):
    out_io = gen_triangulateio_out(sample, size, quality_area, quality_angle, verbose);
    if None is not out_io_output:
        out_io_output.append(out_io)
    ccw = get_sample_instance(sample).ccw
    return triangle.gen_compound_path(out_io, ccw)

def gen_triangulateio_out(sample=1, size=None, quality_area=None, quality_angle=None, verbose=False):
    in_io = gen_triangulateio_in(sample, size)
    out_io = triangle.Triangulateio()
    switches = triangle.gen_switches(quality_area, quality_angle, verbose);
    triangle.triangulate(switches, in_io, out_io)
    return out_io

def gen_GeomUtils(sample=1, size=None, quality_area=None, quality_angle=None, verbose=False):
    t_list = []
    comp_path = gen_compound_path(sample, size, quality_area, quality_angle, verbose, out_io_output=t_list)
    out_io = t_list[0]
    lines = tools.path_to_LineBoundary(comp_path)
    ArrayList = JClass('java.util.ArrayList')
    lineList = ArrayList(len(lines))
    for line in lines:
        lineList.add(line)
    
    Node = JClass('net.epsilony.simpmeshfree.model.Node')
    
    nodes = deque()
    for i in xrange(out_io.numberofpoints):
        if out_io.pointmarkerlist[i] != 0:
            continue
        x = out_io.pointlist[i * 2]
        y = out_io.pointlist[i * 2 + 1]
        node = Node(x, y)
        nodes.append(node)
    nodeList = ArrayList(len(nodes))
    for node in nodes:
        nodeList.add(node)
    
    GeomUtils = JClass('net.epsilony.simpmeshfree.model.GeomUtils')
    return GeomUtils(lineList, nodeList, 2)

