from jpype import JArray,java,JInt
from simpmeshfree_gui import jvm_utils as ju
from simpmeshfree_gui.plot2d import *
from simpmeshfree_gui.tools import JDArr_List_2_np,JTDList_List_2_np
import numpy as np
import math
import matplotlib.pyplot as plt

def _exact_value(tBeam,coords,val_type):
    fun_map={'stress':(tBeam.getStress,(None,),3),'strain':(tBeam.getStrain,(None,),3),'displacement':(tBeam.getDisplacement,(None,1),6)}
    (fun,args,numCol)=fun_map[val_type]
    result=np.ndarray((coords.size(),numCol))
    i=0
    for coord in ju.iter_Iterable(coords):
        result[i]=fun(coord.x,coord.y,*args)
        i+=1
    return result

def exact_displacements(tBeam, coords):
    return _exact_value(tBeam, coords, 'displacement')

def exact_stress(tBeam,coords):
    return _exact_value(tBeam,coords,'stress')

def exact_strain(tBeam,coords):
    return _exact_value(tBeam,coords,'strain')

def nodesValue(processer):
    ndsRes=processer.getNodesValue()
    sz=ndsRes.size()/2
    result=np.ndarray((sz,2))
    for i in xrange(sz):
        result[i]=(ndsRes.get(i*2),ndsRes.get(i*2+1))
    return result

def run_processor(iterativeSolver=False,isSimpAsm=True,core_num=None,monitor=None):
    
    WU=ju.WeakformProcessor2DDemoUtils
    pipe=WU.newPipe()
    processor=WU.timoshenkoBeam(pipe,iterativeSolver,isSimpAsm)
    if(monitor is not None):
        processor.setMonitor(monitor)
    if(core_num is None):  
        processor.process()
    else:
        processor.process(core_num);
    processor.solveEquation()
    return (processor,pipe)

def problem_record_Lists(pb):
   
    qp=ju.QuadraturePoint()

    volIter=pb.volumeIterator()
    volCoords=java.util.ArrayList(volIter.sumNum)
    while(volIter.next(qp)):
        volCoords.add(ju.Node(qp.coordinate))
    
    diriIter=pb.dirichletIterator()
    diriCoords=java.util.ArrayList(diriIter.sumNum)
    diriBnds=java.util.ArrayList(diriIter.sumNum)
    
    while(diriIter.next(qp)):
        diriCoords.add(ju.Node(qp.coordinate))
        diriBnds.add(qp.boundary)
        
    neumIter=pb.neumannIterator()
    neumCoords=java.util.ArrayList(neumIter.sumNum)
    neumBnds=java.util.ArrayList(neumIter.sumNum)
    while(neumIter.next(qp)):
        neumCoords.add(ju.Node(qp.coordinate))
        neumBnds.add(qp.boundary);
    
    return (volCoords,diriCoords,diriBnds,neumCoords,neumBnds)

def sample_Coords(width,height,step=0.5,bndTrans=0.01):
    
    numCol=math.ceil(width/step)+1
    numRow=math.ceil(height/step)+1
    xs=np.linspace(bndTrans,width-bndTrans,numCol)
    ys=np.linspace(height/2.0-bndTrans,-height/2.0+bndTrans,numRow)
    crds=java.util.ArrayList(len(xs)*len(ys))
    for y in ys:
        for x in xs:
            crds.add(ju.Coordinate(x,y))
    return crds

def plot_on_line(tBeam,postProcessor,x=None,y=0,val_type='displacement',step=0.1,margin=0.01,conLaw=None):
    width=tBeam.width
    height=tBeam.height
    if x is not None:
        numRow=math.ceil(height/step)+1
        ys=np.linspace(-height/2+margin, height/2-margin,numRow)
        xs=np.ones_like(ys)*x
        output_xs=ys
    elif y is not None:
        numCol=math.ceil(width/step)+1
        xs=np.linspace(margin,width-margin,numCol)
        ys=np.ones_like(xs)*y
        output_xs=xs
    else:
        raise ValueError('One of x of y must be set!')
    coords=java.util.ArrayList(len(xs))
    
    for i in xrange(len(xs)):
        coords.add(ju.Coordinate(xs[i],ys[i]))
    if val_type=='displacement':
        exactDisps=_exact_value(tBeam, coords, val_type)
        disps=JTDList_List_2_np(postProcessor.displacements(coords,None,1)).transpose()
        output_ys_1=exactDisps
        output_ys_2=disps
        output_labels=('exact u','exact v','exact u_x','exact u_y','exact v_x','exact v_y','u','v','u_x','u_y','v_x','v_y')
    elif val_type=='stress':
        exactStress=_exact_value(tBeam,coords,val_type)
        disps_JTDList=postProcessor.displacements(coords,None,1)
        stresses=JTDList_List_2_np(ju.CommonPostProcessor.stress2D(disps_JTDList,2,conLaw)).transpose()
        output_ys_1=exactStress
        output_ys_2=stresses
        output_labels=('exact stress_xx','exact stress_yy','exact stress_xy','stress_xx','stress_yy','stress_xy')
    elif val_type=='strain':
        exactStrain=_exact_value(tBeam,coords,val_type)
        disps_JTDList=postProcessor.displacements(coords,None,1)
        strains=JTDList_List_2_np(ju.CommonPostProcessor.strain2D(disps_JTDList,2)).transpose()
        output_ys_1=exactStrain
        output_ys_2=strains
        output_labels=('exact strain_xx','exact strain_yy','exact strain_xy','strain_xx','strain_yy','strain_xy')
    output_ys=np.ndarray((output_ys_1.shape[0],output_ys_1.shape[1]+output_ys_2.shape[1]))
    output_ys[:,:output_ys_1.shape[1]]=output_ys_1[:,:]
    output_ys[:,output_ys_1.shape[1]:output_ys_1.shape[1]+output_ys_2.shape[1]]=output_ys_2[:,:]  
    fig=plt.figure()
    ax=fig.add_subplot(111)
    for i in xrange(output_ys.shape[1]):
        ax.plot(output_xs,output_ys[:,i],label=output_labels[i])
    ax.legend()
    fig.canvas.draw()
    fig.show()
    return (fig,ax,output_xs,output_ys,output_labels)