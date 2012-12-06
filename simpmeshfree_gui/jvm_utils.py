# -*- coding: utf-8 -*-
from jpype import startJVM, getDefaultJVMPath, isJVMStarted,JPackage,JClass
import os
from multiprocessing import Process, Queue, Lock
from collections import deque

Node,BoundaryUtilsTestUtils,QuadraturePoint, \
	TimoshenkoExactBeam2D,CommonPostProcessor,  \
	CommonUtils,WeakformProcessorMonitors,Coordinate, \
	WeakformProcessor2DDemoUtils,QuadPixcellAtomSample, \
	QuadPixcellAtomSample,QuadPixcellRectangleSample,QuadPixcellManager, \
	LocationAdaptiveFilter,Triangle,Quadrangle,UniformTensionInfinitePlateSample, \
	SampleLSF,SampleC1LSF,SampleC2LSF=[None for i in xrange(20)]


def import_classes():
	if not isJVMStarted():
		print "Jvm has not been started! No class is imported!"
		return
	global Node,BoundaryUtilsTestUtils,QuadraturePoint,TimoshenkoExactBeam2D,CommonPostProcessor
	global CommonUtils,WeakformProcessorMonitors,Coordinate,WeakformProcessor2DDemoUtils
	global QuadPixcellAtomSample,QuadPixcellRectangleSample,QuadPixcellManager
	global LocationAdaptiveFilter,Triangle,Quadrangle,UniformTensionInfinitePlateSample
	global SampleLSF,SampleC1LSF,SampleC2LSF
	Node=JPackage('net').epsilony.utils.geom.Node
	BoundaryUtilsTestUtils=JPackage('net').epsilony.simpmeshfree.model.test.BoundaryUtilsTestUtils
	QuadraturePoint=JClass('net.epsilony.simpmeshfree.utils.QuadraturePoint')
	TimoshenkoExactBeam2D=JClass('net.epsilony.simpmeshfree.model2d.TimoshenkoExactBeam2D')
	CommonPostProcessor=JClass('net.epsilony.simpmeshfree.model.CommonPostProcessor')
	CommonUtils=JPackage('net').epsilony.spfun.CommonUtils
	WeakformProcessorMonitors=JPackage('net').epsilony.simpmeshfree.model.WeakformProcessorMonitors
	Coordinate = JPackage('net').epsilony.utils.geom.Coordinate
	WeakformProcessor2DDemoUtils=JClass('net.epsilony.simpmeshfree.model2d.test.WeakformProcessor2DDemoUtils')
	QuadPixcellAtomSample=JPackage('net').epsilony.simpmeshfree.adpt2d.sample.QuadPixcellAtomSample
	QuadPixcellRectangleSample=JPackage('net').epsilony.simpmeshfree.adpt2d.sample.QuadPixcellRectangleSample
	QuadPixcellManager=JPackage('net').epsilony.simpmeshfree.adpt2d.QuadPixcellManager
	LocationAdaptiveFilter=JPackage('net').epsilony.simpmeshfree.adpt2d.sample.LocationAdaptiveFilter
	Triangle = JClass('net.epsilony.utils.geom.Triangle')
	Quadrangle = JClass('net.epsilony.utils.geom.Quadrangle')
	UniformTensionInfinitePlateSample=JPackage('net').epsilony.simpmeshfree.model2d.test.UniformTensionInfinitePlateSample
	SampleLSF=JClass('net.epsilony.levelset.functions.SampleLSF')
	SampleC1LSF=JClass('net.epsilony.levelset.functions.SampleC1LSF')
	SampleC2LSF=JClass('net.epsilony.levelset.functions.SampleC2LSF')

def start_jvm(debug_port=None):
	if isJVMStarted():
		print "JVM has been started!"
		if debug_port is not None:
			print("Warning the debug_port setting: " + 
				str(debug_port) + " may not be activate, if it hasn't been activate before")
		return
	jvm_path = getDefaultJVMPath()
	simpmeshfree_path = os.getenv("SIMP_MESHFREE_PATH")
	switches = []
	if simpmeshfree_path is None:
		import simpmeshfree_gui
		#switches.append('-Djava.class.path=/home/epsilon/SimpMeshfree/dist/SimpMeshfree.jar:/home/epsilon/SimpMeshfree/libs/JavaUtils/dist/EpsilonYUtil.jar')
		lib_path='-Djava.class.path='+simpmeshfree_gui.__path__[0]+'/../../SimpMeshfree/dist/SimpMeshfree.jar'
		print "lib_path is ",lib_path
		switches.append(lib_path)
#	switches.append('net.epsilony.utils.geom.Coordinate')
	if debug_port is not None:
		switches.extend(["-Xdebug", "-Xrunjdwp:transport=dt_socket,address=" + str(debug_port) + ",server=y,suspend=n"])
	startJVM(jvm_path, *switches)
	import_classes()
	

def _deque_from_Iterator(iterator):
	res = deque()
	while iterator.hasNext():
		res.append(iterator.next())
	return res

def deque_from_Iterable(iterable):
	return _deque_from_Iterator(iterable.iterator())

def list_from_Iterable(iterable):
	return list(deque_from_Iterable)

class _iterator_from_Iterable(object):
	def __init__(self, iterable):
		self.iterable = iterable
	
	def __iter__(self):
		self.iterator = self.iterable.iterator()
		return self
	
	def next(self): 	  #@ReservedAssignment
		if self.iterator.hasNext():
			return self.iterator.next()
		else:
			raise StopIteration()

def iter_Iterable(iterable):
	return _iterator_from_Iterable(iterable)

class JvmTask(object):
	def __init__(self, fun, args=None):
		self.fun = fun
		self.args = args
	
	def run(self):
		if self.args is None:
			return self.fun()
		return self.fun(*(self.args))

class JvmProcess(Process):
	def __init__(self, debug_port=None):
		Process.__init__(self)
		self.task_queue = Queue()
		self.result_queue = Queue()
		self.debug_port = debug_port
		self.lock = Lock()
		
		
	def stop(self):
		self.put_task(None)
		self.join()
	
	def put_task(self, task):
		self.task_queue.put(task)
	
	def put_function(self, func, args=None):
		self.put_task(JvmTask(func, args))
	
	def is_result_empty(self):
		return self.result_queue.empty()
	
	def get_result(self, block=True, timeout=None):
		with self.lock:
			print 'acc lock in get'
			res = self.res
		return res
#		return self.result_queue.get(block, timeout)
	
	def run(self):
		start_jvm(self.debug_port)
		while True:
			task = self.task_queue.get()
			if task is None:
				print 'exit process %s' % (self.name,), " "
				break;
			res = task.run()
			self.result_queue.put(res)
			
			
