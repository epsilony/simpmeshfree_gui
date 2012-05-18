from jpype import startJVM, getDefaultJVMPath, isJVMStarted
import os
from multiprocessing import Process, Queue, Lock
from collections import deque

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
		switches.append('-Djava.class.path=/home/epsilon/SimpMeshfree/dist/SimpMeshfree.jar')
#	switches.append('net.epsilony.utils.geom.Coordinate')
	if debug_port is not None:
		switches.extend(["-Xdebug", "-Xrunjdwp:transport=dt_socket,address=" + str(debug_port) + ",server=y,suspend=n"])
	startJVM(jvm_path, *switches)
	

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
			
			
