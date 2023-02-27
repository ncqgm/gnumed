"""GNUmed client internal signal handling.

# this code has been written by Patrick O'Brien <pobrien@orbtech.com>
# downloaded from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/87056
"""
import weakref
import logging


known_signals = [
	'current_encounter_modified',	# the current encounter was modified externally
	'current_encounter_switched',	# *another* encounter became the current one
	'pre_patient_unselection',
	'post_patient_selection',
	'patient_locked',
	'patient_unlocked',
	'import_document_from_file',
	'import_document_from_files',
	'statustext',					# args: msg=message, beep=whether to beep or not
	'display_widget',				# args: name=name of widget, other=widget specific (see receivers)
	'plugin_loaded',				# args: name=name of plugin
	'application_closing',
	'request_user_attention',
	'clin_item_updated',			# sent by SOAP importer
	'register_pre_exit_callback',	# args: callback = function to call
	'focus_patient_search',		# set focus to patient search box
]

_log = logging.getLogger('gm.messaging')

connections:dict[int, dict] = {}
senders:dict[int, weakref.ref] = {}

_boundMethods:weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
#=====================================================================
class _Any:
	pass

Any = _Any()

known_signals.append(Any)		# type: ignore

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
def connect(receiver=None, signal=Any, sender=Any, weak=0):
#def connect(receiver=None, signal=None, sender=Any, weak=0):
	"""Connect receiver to sender for signal.

	If sender is Any, receiver will receive signal from any sender.
	If signal is Any, receiver will receive any signal from sender.
	If sender is None, receiver will receive signal from anonymous.
	If signal is Any and sender is None, receiver will receive any signal from anonymous.
	If signal is Any and sender is Any, receiver will receive any signal from any sender.
	If weak is true, weak references will be used.

	ADDITIONAL gnumed specific documentation:

	this dispatcher is not designed with a gui single threaded event loop in mind.

	when connecting to a receiver that may eventually make
	calls to gui objects such as wxWindows objects, it is
	highly recommended that any such calls be wrapped in
	wxCallAfter() e.g.

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
	a global reference, such as via gmCurrentPatient."""

	if receiver is None:
		raise ValueError('gmDispatcher.connect(): must define <receiver>')

	if signal is not Any:
		signal = str(signal)

	if weak:
		receiver = safeRef(receiver)

	if sender is Any:
		_log.debug('connecting (weak=%s): <any sender> ==%s==> %s', weak, signal, receiver)
	else:
		_log.debug('connecting (weak=%s): %s ==%s==> %s', weak, sender, signal, receiver)

	sender_identity = id(sender)
	signals = {}
	if sender_identity in connections:
		signals = connections[sender_identity]
	else:
		connections[sender_identity] = signals
		# Keep track of senders for cleanup.
		if sender not in (None, Any):
			def _remove4weakref(object, sender_identity=sender_identity):
				_removeSender(sender_identity=sender_identity)
			# Skip objects that can not be weakly referenced, which means
			# they won't be automatically cleaned up, but that's too bad.
			try:
				weakSender = weakref.ref(sender, _remove4weakref)
				senders[sender_identity] = weakSender
			except Exception:
				pass
	receivers = []
	if signal in signals:
		receivers = signals[signal]
	else:
		signals[signal] = receivers
	try:
		receivers.remove(receiver)
	except ValueError:
		pass
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
	sender_identity = id(sender)
	try:
		receivers = connections[sender_identity][signal]
	except KeyError:
		_log.warning('no receivers for signal %(sig)s from sender %(sender)s', {'sig': repr(signal), 'sender': sender})
		print('DISPATCHER ERROR: no receivers for signal %s from sender %s' % (repr(signal), sender))
		return
	try:
		receivers.remove(receiver)
	except ValueError:
		_log.warning('receiver [%(rx)s] not connected to signal [%(sig)s] from [%(sender)s]', {'rx': receiver, 'sig': repr(signal), 'sender': sender})
		print("DISPATCHER ERROR: receiver [%s] not connected to signal [%s] from [%s]" % (receiver, repr(signal), sender))
	_cleanupConnections(sender_identity, signal)

#---------------------------------------------------------------------
def send(signal=None, sender=None, **kwds):
	"""Send signal from sender to all connected receivers.

	Return a list of tuple pairs [(receiver, response), ... ].
	If sender is None, signal is sent anonymously.
	"""
	signal = str(signal)
	sender_identity = id(sender)
	identity_of_Any = id(Any)

	# Get receivers that receive *this* signal from *this* sender.
	receivers = []
	try:
		receivers.extend(connections[sender_identity][signal])
	except KeyError:
		pass

	# Add receivers that receive *any* signal from *this* sender.
	anyreceivers = []
	try:
		anyreceivers = connections[sender_identity][Any]
	except KeyError:
		pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)

	# Add receivers that receive *this* signal from *any* sender.
	anyreceivers = []
	try:
		anyreceivers = connections[identity_of_Any][signal]
	except KeyError:
		pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)

	# Add receivers that receive *any* signal from *any* sender.
	anyreceivers = []
	try:
		anyreceivers = connections[identity_of_Any][Any]
	except KeyError:
		pass
	for receiver in anyreceivers:
		if receivers.count(receiver) == 0:
			receivers.append(receiver)

	# Call each receiver with whatever arguments it can accept.
	# Return a list of tuple pairs [(receiver, response), ... ].
	responses = []
	for receiver in receivers:
		if (type(receiver) is weakref.ReferenceType) or (isinstance(receiver, BoundMethodWeakref)):
			_log.debug('dereferencing weak_ref receiver [%s]', receiver)
			# Dereference the weak reference.
			receiver = receiver()
			_log.debug('dereferenced receiver is [%s]', receiver)
			if receiver is None:
				# This receiver is dead, so skip it.
				continue
		try:
			response = _call(receiver, signal=signal, sender=sender, **kwds)
			responses += [(receiver, response)]
		except Exception:
			_log.exception('exception calling [%s]: (signal=%s, sender=%a, **kwds=%s)', receiver, signal, sender, str(kwds))

	return responses

#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def safeRef(object):
	"""Return a *safe* weak reference to a callable object."""
	if hasattr(object, '__self__'):
		if object.__self__ is not None:
			# Turn a bound method into a BoundMethodWeakref instance.
			# Keep track of these instances for lookup by disconnect().
			selfkey = object.__self__
			funckey = object.__func__
			if selfkey not in _boundMethods:
				_boundMethods[selfkey] = weakref.WeakKeyDictionary()
			if funckey not in _boundMethods[selfkey]:
				_boundMethods[selfkey][funckey] = BoundMethodWeakref(boundMethod=object)
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
			print('BoundMethodWeakref.__init__.remove(): _removeReceiver =', _removeReceiver)
			print('BoundMethodWeakref.__init__.remove(): self =', self)
			if callable(_removeReceiver):
				_removeReceiver(receiver = self)

		self.weakSelf = weakref.ref(boundMethod.__self__, remove)
		self.weakFunc = weakref.ref(boundMethod.__func__, remove)
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
#	# not used in GNUmed
#	#if type(receiver) is types.InstanceType:
#	#if isinstance(receiver, object):
#	# if receiver is an instance -> get the "call" interface = the __init__() function
#	if type(receiver) is object:
#		# receiver is a class instance; assume it is callable.
#		# Reassign receiver to the actual method that will be called.
#		receiver = receiver.__call__

	if hasattr(receiver, '__func__'):
		# receiver is a method. Drop the first argument, usually 'self'.
		func_code_def = receiver.__func__.__code__
		acceptable_args = func_code_def.co_varnames[1:func_code_def.co_argcount]
	elif hasattr(receiver, '__code__'):
		# receiver is a function.
		func_code_def = receiver.__code__
		acceptable_args = func_code_def.co_varnames[0:func_code_def.co_argcount]
	else:
		_log.error('<%s> must be instance, method or function, but is [%s]', str(receiver), type(receiver))
		raise TypeError('DISPATCHER ERROR: _call(): <%s> must be instance, method or function, but is [%s]' % (str(receiver), type(receiver)))

	# 0x08: bit for whether func uses **kwds syntax
	if not (func_code_def.co_flags & 0x08):
		# func_code_def does not have a **kwds type parameter,
		# therefore remove unacceptable arguments.
		keys = list(kwds)
		for arg in keys:
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
	for sender_identity in connections:
		for signal in connections[sender_identity]:
			receivers = connections[sender_identity][signal]
			try:
				receivers.remove(receiver)
			except Exception:
				pass
			_cleanupConnections(sender_identity, signal)

#---------------------------------------------------------------------
def _cleanupConnections(sender_identity, signal):
	"""Delete any empty signals for sender_identity. Delete sender_identity if empty."""
	receivers = connections[sender_identity][signal]
	if not receivers:
		# No more connected receivers. Therefore, remove the signal.
		signals = connections[sender_identity]
		del signals[signal]
		if not signals:
			# No more signal connections. Therefore, remove the sender.
			_removeSender(sender_identity)
#---------------------------------------------------------------------
def _removeSender(sender_identity):
	"""Remove sender_identity from connections."""
	del connections[sender_identity]
	# sender_identity will only be in senders dictionary if sender 
	# could be weakly referenced.
	try: del senders[sender_identity]
	except Exception: pass

#=====================================================================
