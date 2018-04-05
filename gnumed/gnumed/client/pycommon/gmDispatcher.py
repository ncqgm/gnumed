__doc__ = """GNUmed client internal signal handling.

# this code has been written by Patrick O'Brien <pobrien@orbtech.com>
# downloaded from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/87056
"""
import types
import sys
import weakref
import traceback
import logging


known_signals = [
	u'current_encounter_modified',	# the current encounter was modified externally
	u'current_encounter_switched',	# *another* encounter became the current one
	u'pre_patient_unselection',
	u'post_patient_selection',
	u'patient_locked',
	u'patient_unlocked',
	u'import_document_from_file',
	u'import_document_from_files',
	u'statustext',					# args: msg=message, beep=whether to beep or not
	u'display_widget',				# args: name=name of widget, other=widget specific (see receivers)
	u'plugin_loaded',				# args: name=name of plugin
	u'application_closing',
	u'request_user_attention',
	u'clin_item_updated',			# sent by SOAP importer
	u'register_pre_exit_callback',	# args: callback = function to call
	u'focus_patient_search',		# set focus to patient search box
]

_log = logging.getLogger('gm.messaging')

connections = {}
senders = {}

_boundMethods = weakref.WeakKeyDictionary()
#=====================================================================
class _Any:
	pass

Any = _Any()

known_signals.append(Any)
#=====================================================================
class DispatcherError(Exception):
	def __init__(self, args=None):
		self.args = args

#=====================================================================
# external API
#---------------------------------------------------------------------
__execute_in_main_thread = None

def set_main_thread_caller(caller):
	if not callable(caller):
		raise TypeError('caller [%s] is not callable' % caller)
	global __execute_in_main_thread
	__execute_in_main_thread = caller

#=====================================================================
def connect(receiver=None, signal=Any, sender=Any, weak=1):
	"""Connect receiver to sender for signal.

	If sender is Any, receiver will receive signal from any sender.
	If signal is Any, receiver will receive any signal from sender.
	If sender is None, receiver will receive signal from anonymous.
	If signal is Any and sender is None, receiver will receive any signal from anonymous.
	If signal is Any and sender is Any, receiver will receive any signal from any sender.
	If weak is true, weak references will be used.

	ADDITIONAL gnumed specific documentation:

	this dispatcher is not designed with a gui single threaded event loop in mind.

	when connecting to a receiver that may eventually make calls to gui objects such as wxWindows objects, it is highly recommended that any such calls be wrapped in wxCallAfter() e.g.

	def receiveSignal(self, **args):
		self._callsThatDoNotTriggerGuiUpdates()
		self.data = processArgs(args)
		wxCallAfter( self._callsThatTriggerGuiUpdates() )

	since it is likely data change occurs before the signalling, it would probably look more simply like:

	def receiveSignal(self, **args):
		wxCallAfter(self._updateUI() )

	def _updateUI(self):
		# your code that reads data

	Especially if the widget can get a reference to updated data through
	a global reference, such as via gmCurrentPatient.
"""
	if receiver is None:
		raise ValueError('gmDispatcher.connect(): must define <receiver>')

	if signal not in known_signals:
		_log.warning('unknown signal [%(sig)s]', {'sig': signal})

	if signal is not Any:
		signal = str(signal)

	if weak:
		receiver = safeRef(receiver)
	senderkey = id(sender)
	signals = {}
	if senderkey in connections:
		signals = connections[senderkey]
	else:
		connections[senderkey] = signals
		# Keep track of senders for cleanup.
		if sender not in (None, Any):
			def remove(object, senderkey=senderkey):
				_removeSender(senderkey=senderkey)
			# Skip objects that can not be weakly referenced, which means
			# they won't be automatically cleaned up, but that's too bad.
			try:
				weakSender = weakref.ref(sender, remove)
				senders[senderkey] = weakSender
			except:
				pass
	receivers = []
	if signal in signals:
		receivers = signals[signal]
	else:
		signals[signal] = receivers
	try: receivers.remove(receiver)
	except ValueError: pass
	receivers.append(receiver)
#---------------------------------------------------------------------
def disconnect(receiver, signal=Any, sender=Any, weak=1):
	"""Disconnect receiver from sender for signal.

	Disconnecting is not required. The use of disconnect is the same as for
	connect, only in reverse. Think of it as undoing a previous connection."""
	if signal not in known_signals:
		_log.warning('unknown signal [%(sig)s]', {'sig': signal})

	if signal is not Any:
		signal = str(signal)
	if weak: receiver = safeRef(receiver)
	senderkey = id(sender)
	try:
		receivers = connections[senderkey][signal]
	except KeyError:
		_log.warning('no receivers for signal %(sig)s from sender %(sender)s', {'sig': repr(signal), 'sender': sender})
		print('DISPATCHER ERROR: no receivers for signal %s from sender %s' % (repr(signal), sender))
		return
	try:
		receivers.remove(receiver)
	except ValueError:
		_log.warning('receiver [%(rx)s] not connected to signal [%(sig)s] from [%(sender)s]', {'rx': receiver, 'sig': repr(signal), 'sender': sender})
		print("DISPATCHER ERROR: receiver [%s] not connected to signal [%s] from [%s]" % (receiver, repr(signal), sender))
	_cleanupConnections(senderkey, signal)
#---------------------------------------------------------------------
def send(signal=None, sender=None, **kwds):
	"""Send signal from sender to all connected receivers.

	Return a list of tuple pairs [(receiver, response), ... ].
	If sender is None, signal is sent anonymously.
	"""
	signal = str(signal)
	senderkey = id(sender)
	anykey = id(Any)
	# Get receivers that receive *this* signal from *this* sender.
	receivers = []
	try: receivers.extend(connections[senderkey][signal])
	except KeyError: pass
	# Add receivers that receive *any* signal from *this* sender.
	anyreceivers = []
	try: anyreceivers = connections[senderkey][Any]
	except KeyError: pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)
	# Add receivers that receive *this* signal from *any* sender.
	anyreceivers = []
	try: anyreceivers = connections[anykey][signal]
	except KeyError: pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)
	# Add receivers that receive *any* signal from *any* sender.
	anyreceivers = []
	try: anyreceivers = connections[anykey][Any]
	except KeyError: pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)
	# Call each receiver with whatever arguments it can accept.
	# Return a list of tuple pairs [(receiver, response), ... ].
	responses = []
	for receiver in receivers:
		if (type(receiver) is weakref.ReferenceType) or (isinstance(receiver, BoundMethodWeakref)):
			# Dereference the weak reference.
			receiver = receiver()
			if receiver is None:
				# This receiver is dead, so skip it.
				continue
		try:
			response = _call(receiver, signal=signal, sender=sender, **kwds)
			responses += [(receiver, response)]
		except:
			# this seems such a fundamental error that it appears
			# reasonable to print directly to the console
			typ, val, tb = sys.exc_info()
			_log.critical('%(t)s, <%(v)s>', {'t': typ, 'v': val})
			_log.critical('calling <%(rx)s> failed', {'rx': str(receiver)})
			traceback.print_tb(tb)
	return responses
#---------------------------------------------------------------------
def safeRef(object):
	"""Return a *safe* weak reference to a callable object."""
	if hasattr(object, 'im_self'):
		if object.im_self is not None:
			# Turn a bound method into a BoundMethodWeakref instance.
			# Keep track of these instances for lookup by disconnect().
			selfkey = object.im_self
			funckey = object.im_func
			if selfkey not in _boundMethods:
				_boundMethods[selfkey] = weakref.WeakKeyDictionary()
			if funckey not in _boundMethods[selfkey]:
				_boundMethods[selfkey][funckey] = \
				BoundMethodWeakref(boundMethod=object)
			return _boundMethods[selfkey][funckey]
	return weakref.ref(object, _removeReceiver)
#=====================================================================
class BoundMethodWeakref:
	"""BoundMethodWeakref class."""

	def __init__(self, boundMethod):
		"""Return a weak-reference-like instance for a bound method."""
		self.isDead = 0
		def remove(object, self=self):
			"""Set self.isDead to true when method or instance is destroyed."""
			self.isDead = 1
			_removeReceiver(receiver=self)
		self.weakSelf = weakref.ref(boundMethod.im_self, remove)
		self.weakFunc = weakref.ref(boundMethod.im_func, remove)
	#------------------------------------------------------------------
	def __repr__(self):
		"""Return the closest representation."""
		return repr(self.weakFunc)
	#------------------------------------------------------------------
	def __call__(self):
		"""Return a strong reference to the bound method."""

		if self.isDead:
			return None

		obj = self.weakSelf()
		method = self.weakFunc().__name__
		if not obj:
			self.isDead = 1
			_removeReceiver(receiver=self)
			return None
		try:
			return getattr(obj, method)
		except RuntimeError:
			self.isDead = 1
			_removeReceiver(receiver=self)
			return None

#=====================================================================
# internal API
#---------------------------------------------------------------------
def _call(receiver, **kwds):
	"""Call receiver with only arguments it can accept."""
	if type(receiver) is types.InstanceType:
		# receiver is a class instance; assume it is callable.
		# Reassign receiver to the actual method that will be called.
		receiver = receiver.__call__
	if hasattr(receiver, 'im_func'):
		# receiver is a method. Drop the first argument, usually 'self'.
		fc = receiver.im_func.func_code
		acceptable_args = fc.co_varnames[1:fc.co_argcount]
	elif hasattr(receiver, 'func_code'):
		# receiver is a function.
		fc = receiver.func_code
		acceptable_args = fc.co_varnames[0:fc.co_argcount]
	else:
		_log.error('<%(rx)s> must be instance, method or function', {'rx': str(receiver)})
		print('DISPATCHER ERROR: _call(): <%s> must be instance, method or function' % str(receiver))
	if not (fc.co_flags & 8):
		# fc does not have a **kwds type parameter, therefore 
		# remove unacceptable arguments.
		for arg in kwds.keys():
			if arg not in acceptable_args:
				del kwds[arg]

	if __execute_in_main_thread is None:
		print('DISPATCHER problem: no main-thread executor available')
		return receiver(**kwds)

	# if a cross-thread executor is set
	return __execute_in_main_thread(receiver, **kwds)
#---------------------------------------------------------------------
def _removeReceiver(receiver):
	"""Remove receiver from connections."""
	for senderkey in connections.keys():
		for signal in connections[senderkey].keys():
			receivers = connections[senderkey][signal]
			try:
				receivers.remove(receiver)
			except:
				pass
			_cleanupConnections(senderkey, signal)
#---------------------------------------------------------------------
def _cleanupConnections(senderkey, signal):
	"""Delete any empty signals for senderkey. Delete senderkey if empty."""
	receivers = connections[senderkey][signal]
	if not receivers:
		# No more connected receivers. Therefore, remove the signal.
		signals = connections[senderkey]
		del signals[signal]
		if not signals:
			# No more signal connections. Therefore, remove the sender.
			_removeSender(senderkey)
#---------------------------------------------------------------------
def _removeSender(senderkey):
	"""Remove senderkey from connections."""
	del connections[senderkey]
	# Senderkey will only be in senders dictionary if sender 
	# could be weakly referenced.
	try: del senders[senderkey]
	except: pass

#=====================================================================
