# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from simpmeshfree_gui.jvm_utils import start_jvm, iter_Iterable
from jpype import JClass, java, JPackage, JInt
import numpy as np

def coord_to_array(coord):
    return np.array((coord.x, coord.y, coord.z), dtype=np.double)

def TArray_to_array(tarray):
    res = np.ndarray((len(tarray), tarray[0].size()))
    for i in xrange(len(tarray)):
        for j in xrange(tarray[0].size()):
            res[i, j] = tarray[i].get(j)
    return res

def triple_spline(rad, center, nd):
    c_arr = coord_to_array(center)
    n_arr = coord_to_array(nd)
    t = (c_arr - n_arr)
    disSq = np.dot(t, t)
    dis = disSq ** 0.5
    r = dis / (rad * 1.0)
    if(r >= 1):
        return np.array((0, 0, 0), dtype=np.double)
    if r <= 0.5:
        w = 2 / 3.0 - 4 * r ** 2 + 4 * r ** 3
        w_x = (-4 + 6 * r) * 2 * (c_arr[0] - n_arr[0]) / (rad ** 2)
        w_y = (-4 + 6 * r) * 2 * (c_arr[1] - n_arr[1]) / (rad ** 2)
    else:
        w = 4 / 3.0 - 4 * r + 4 * r ** 2 - 4 / 3.0 * r ** 3
        w_x = (-2 / r + 4 - 2 * r) * 2 * (c_arr[0] - n_arr[0]) / (rad ** 2)
        w_y = (-2 / r + 4 - 2 * r) * 2 * (c_arr[1] - n_arr[1]) / (rad ** 2)
    return np.array((w, w_x, w_y), dtype=np.double)

def filter_nodes(center, nds, rad):
    radSq = rad * rad
    res = LinkedList()
    for nd in iter_Iterable(nds):
        c_arr = coord_to_array(center)
        n_arr = coord_to_array(nd)
        disSq = np.dot(c_arr - n_arr, c_arr - n_arr)
        if(disSq <= radSq):
            res.add(nd)
    return res

if __name__ == '__main__':
    start_jvm(debug_port=8998)
    TriSpline = JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$TriSpline')
    SimpPower = JClass('net.epsilony.simpmeshfree.model.WeightFunctionCores$SimpPower')
    Common = JClass('net.epsilony.simpmeshfree.model.DistanceFunctions$Common')
    Node = JClass('net.epsilony.simpmeshfree.model.Node')
    TDoubleArrayList = JClass('gnu.trove.list.array.TDoubleArrayList')
    WeightFunctions = JClass('net.epsilony.simpmeshfree.model.WeightFunctions')
    WeightFunctionTestUtils = JPackage('net').epsilony.simpmeshfree.model2d.test.WeightFunctionTestUtils
    TU = WeightFunctionTestUtils
    PB = JPackage('net').epsilony.simpmeshfree.utils.Complete2DPolynomialBase
    LinkedList = java.util.LinkedList
    ArrayList = java.util.ArrayList
    
    (xMin, yMin, xMax, yMax, ndNum, isDist) = (0.0, 0.0, 1.0, 1.0, 80.0, False)
    centerNum = 400.0
    supRad = 0.5
    baseOrder = 3
    weightCore = TriSpline()
    poly_base_fun = PB.complete2DPolynomialBase(baseOrder)
    poly_base_fun.setDiffOrder(1)
    
    xys = LinkedList()
    expFun = TU.genExpFun("c")
    resNds = ArrayList()
    
    nds = TU.genNodes(xMin, yMin, xMax, yMax, ndNum, isDist)
    center = Node(0.5, 0.5)
    shapeFun = TU.genShapeFunction(supRad, nds, baseOrder, weightCore)
    shapeFun.setDiffOrder(1)
    shapeFunVals = shapeFun.values(center, None, None, resNds)
    shapeFunVals = TArray_to_array(shapeFunVals)
    
    ps = poly_base_fun.values(center, None)
    
    p = np.array(ps[0])
    p_x = np.array(ps[1])
    p_y = np.array(ps[2])
    
    weightFun = WeightFunctions.factory(weightCore, Common())
    weightFun.setDiffOrder(1)
    weightFun.getDistFun().setCenter(center)
    
    
    resNds_2 = filter_nodes(center, nds, supRad)
    resNds_2_xy = np.array([(nd.x, nd.y) for nd in iter_Iterable(resNds_2)])
    P = np.ndarray((p.shape[0], resNds_2.size()), dtype=np.double)
    P_x = np.zeros_like(P, dtype=np.double)
    P_y = np.zeros_like(P, dtype=np.double)
    ndIdx = 0
    for nd in resNds_2:
        ps = poly_base_fun.values(nd, None)
        P[:, ndIdx] = np.array(ps[0])
        P_x[:, ndIdx] = np.array(ps[1])
        P_y[:, ndIdx] = np.array(ps[2])
        ndIdx += 1
    
    w_vals = weightFun.values(resNds_2, supRad, None)
    w_vals = TArray_to_array(w_vals)
    
    W = np.diag(w_vals[0])
    W_x = np.diag(w_vals[1])
    W_y = np.diag(w_vals[2])
    
    A = np.matrix(P) * np.matrix(W) * np.matrix(P.transpose())
    A_x = np.matrix(P) * np.matrix(W_x) * np.matrix(P.transpose())
    A_y = np.matrix(P) * np.matrix(W_y) * np.matrix(P.transpose())
    
    B = np.matrix(P) * np.matrix(W)
    B_x = np.matrix(P) * np.matrix(W_x)
    B_y = np.matrix(P) * np.matrix(W_y)
    
    gamma = np.matrix(p) * (A ** -1)
    shapeVal2 = np.array(gamma * B)
    
    gamma_x = A ** -1 * np.matrix(p_x).transpose() - A ** -1 * A_x * gamma.transpose()
    gamma_x = gamma_x.transpose()
    shapeVal2_x = gamma_x * B + gamma * B_x
    shapeVal2_x = np.array(shapeVal2_x)
    print np.max(shapeFunVals[1] - shapeVal2_x)
    
    gamma_y = A ** -1 * np.matrix(p_y).transpose() - A ** -1 * A_y * gamma.transpose()
    gamma_y = gamma_y.transpose()
    shapeVal2_y = gamma_y * B + gamma * B_y
    shapeVal2_y = np.array(shapeVal2_y)
    print np.max(shapeFunVals[2] - shapeVal2_y)
    
    res_xy=np.array([(nd.x,nd.y) for nd in resNds])
    res_exp=np.array([expFun.value(nd)[0] for nd in resNds])

    #没有发现shapeVal2* 与 shapeFunVals的显著差别，但是仍然不能通过测试。
    #TODO：重做一遍测试。
