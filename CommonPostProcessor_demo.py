from jpype import JArray,java,JPackage,JClass,JInt
from simpmeshfree_gui.jvm_utils import start_jvm,iter_Iterable
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
    for coord in iter_Iterable(coords):
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
    ndsRes=processor.getNodesValue()
    sz=ndsRes.size()/2
    result=np.ndarray((sz,2))
    for i in xrange(sz):
        result[i]=(ndsRes.get(i*2),ndsRes.get(i*2+1))
    return result

def run_processor(iterativeSolver=False):
    start_jvm(debug_port=8998)
    WU=JClass('net.epsilony.simpmeshfree.model2d.test.WeakformProcessor2DDemoUtils')
    pipe=WU.newPipe()
    processor=WU.timoshenkoBeam(pipe,iterativeSolver)    
    processor.process()
    processor.solveEquation()
    return (processor,pipe)

def problem_record_Lists(pb):
    QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    qp=QuadraturePoint()
    JIntArray=JArray(JInt)  
    outNum=JIntArray([0])
    volIter=pb.volumeIterator(outNum)
    volCoords=java.util.ArrayList(outNum[0])
    while(volIter.next(qp)):
        volCoords.add(Node(qp.coordinate))
    
    diriIter=pb.dirichletIterator(outNum)
    diriCoords=java.util.ArrayList(outNum[0])
    diriBnds=java.util.ArrayList(outNum[0])
    
    while(diriIter.next(qp)):
        diriCoords.add(Node(qp.coordinate))
        diriBnds.add(qp.boundary)
        
    neumIter=pb.neumannIterator(outNum)
    neumCoords=java.util.ArrayList(outNum[0])
    neumBnds=java.util.ArrayList(outNum[0])
    while(neumIter.next(qp)):
        neumCoords.add(Node(qp.coordinate))
        neumBnds.add(qp.boundary);
    
    return (volCoords,diriCoords,diriBnds,neumCoords,neumBnds)

def sample_Coords(width,height,step=0.5,bndTrans=0.01):
    Coordinate = JPackage('net').epsilony.utils.geom.Coordinate
    numCol=math.ceil(width/step)+1
    numRow=math.ceil(height/step)+1
    xs=np.linspace(bndTrans,width-bndTrans,numCol)
    ys=np.linspace(height/2.0-bndTrans,-height/2.0+bndTrans,numRow)
    crds=java.util.ArrayList(len(xs)*len(ys))
    for y in ys:
        for x in xs:
            crds.add(Coordinate(x,y))
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
    Coordinate=JClass('net.epsilony.utils.geom.Coordinate')
    for i in xrange(len(xs)):
        coords.add(Coordinate(xs[i],ys[i]))
    if val_type=='displacement':
        exactDisps=_exact_value(tBeam, coords, val_type)
        disps=JTDList_List_2_np(postProcessor.displacements(coords,None,1)).transpose()
        output_ys_1=exactDisps
        output_ys_2=disps
        output_labels=('exact u','exact v','exact u_x','exact u_y','exact v_x','exact v_y','u','v','u_x','u_y','v_x','v_y')
    elif val_type=='stress':
        exactStress=_exact_value(tBeam,coords,val_type)
        disps_JTDList=postProcessor.displacements(coords,None,1)
        CommonPostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
        stresses=JTDList_List_2_np(CommonPostProcessor.stress2D(disps_JTDList,2,conLaw)).transpose()
        output_ys_1=exactStress
        output_ys_2=stresses
        output_labels=('exact stress_xx','exact stress_yy','exact stress_xy','stress_xx','stress_yy','stress_xy')
    elif val_type=='strain':
        exactStrain=_exact_value(tBeam,coords,val_type)
        disps_JTDList=postProcessor.displacements(coords,None,1)
        CommonPostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
        strains=JTDList_List_2_np(CommonPostProcessor.strain2D(disps_JTDList,2)).transpose()
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
        
if __name__=='__main__':
    use_iterative_solver=True;
    (processor,pipe)=run_processor(use_iterative_solver)
    QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
    Node=JClass('net.epsilony.simpmeshfree.model.Node')
    TimoshenkoBeam=JClass('net.epsilony.simpmeshfree.model2d.TimoshenkoExactBeam2D')
    PostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
    CommonUtils=JPackage('net').epsilony.simpmeshfree.utils.CommonUtils
    conLaw=CommonUtils.toDenseMatrix64F(pipe.conLaw)   
    
    qp=QuadraturePoint()

    workPb=pipe.workProblem
    tBeam=workPb.tBeam 
    nds=pipe.geomUtils.allNodes
    ndsVal=nodesValue(processor)
    postProcessor=PostProcessor(processor.shapeFunFactory.factory(),processor.getNodesValue())    
    (volCoords,diriCoords,diriBnds,neumCoords,neumBnds)=problem_record_Lists(workPb)
    
    ndsExactRes=exact_displacements(tBeam,nds)
    
    smpCoords=sample_Coords(tBeam.width,tBeam.height)
    
    smpExactDisps=exact_displacements(tBeam,smpCoords)
    smpDispTDLists=postProcessor.displacements(smpCoords,None,1)
    smpDisps=JTDList_List_2_np(smpDispTDLists.subList(0,2)).transpose()
    
    smpStrainTDList=PostProcessor.strain2D(smpDispTDLists,2)
    smpStrain=JTDList_List_2_np(smpStrainTDList).transpose()
    smpExactStrain=exact_strain(tBeam, smpCoords)
    
    smpStressTDList=PostProcessor.stress2D(smpDispTDLists,2,conLaw)
    smpStress=JTDList_List_2_np(smpStressTDList).transpose()
    smpExactStress=exact_stress(tBeam,smpCoords)
    
    (fig_disp,ax_disp,output_xs_disp,output_ys_disp,output_labels_disp)=plot_on_line(tBeam,postProcessor)
    (fig_strain,ax_strain,output_xs_strain,output_ys_strain,output_labels_strain)=plot_on_line(tBeam,postProcessor,x=tBeam.width/2.0,y=None,val_type='strain')
    (fig_stress,ax_stress,output_xs_stress,output_ys_stress,output_labels_stress)=plot_on_line(tBeam,postProcessor,x=tBeam.width/2.0,y=None,val_type='stress',conLaw=conLaw)
