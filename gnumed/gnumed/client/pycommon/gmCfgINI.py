"""GNUmed INI style configuration handling.

Am Thu, May 22, 2025 at 11:45:31PM -0400 schrieb Grant Edwards via Python-list:

There is sort of a traditional set of locations where
applications look to find a config file:

  $HOME/
  $HOME/.config/
  $HOME/.config/<appname>/
  /etc/
  /etc/<appname>/
  /usr/local/etc/
  /usr/local/etc/<appname>/
  <location specified by command line argument>
  <location specified by ENV variable>

The last two overried all of the others.

Config files that reside in $HOME/ usually start with a dot. Often
they end in 'rc'.  Config files in other directories usually don't
start with a dot.

There's usually an <appname> directory only when an app needs multiple
config files. If an app only has one config file, tradition is that
you don't need a directory for it.

Many applications will parse two config files: a global one from /etc
or /usr/local/ and a user-one from somewhere under $HOME.
"""
#==================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL"


import logging
import sys
import re as regex
import shutil
import tempfile


if __name__ == "__main__":
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBorg


_log = logging.getLogger('gm.cfg')
#==================================================================
# helper functions
#==================================================================
def __set_opt_in_INI_file(src=None, sink=None, group=None, option=None, value=None):

	group_seen = False
	option_seen = False

	for line in src:

		# after option already ?
		if option_seen:
			sink.write(line)
			continue

		# start of list ?
		if regex.match(r'(?P<list_name>.+)(\s|\t)*=(\s|\t)*\$(?P=list_name)\$', line) is not None:
			sink.write(line)
			continue

		# end of list ?
		if regex.match(r'\$.+\$.*', line) is not None:
			sink.write(line)
			continue

		# our group ?
		if line.strip() == '[%s]' % group:
			group_seen = True
			sink.write(line)
			continue

		# another group ?
		if regex.match(r'\[.+\].*', line) is not None:
			# next group but option not seen yet ?
			if group_seen and not option_seen:
				sink.write('%s = %s\n\n\n' % (option, value))
				option_seen = True
			sink.write(line)
			continue

		# our option ?
		if regex.match(r'%s(\s|\t)*=' % option, line) is not None:
			if group_seen:
				sink.write('%s = %s\n' % (option, value))
				option_seen = True
				continue
			sink.write(line)
			continue

		# something else (comment, empty line, or other option)
		sink.write(line)

	# all done ?
	if option_seen:
		return

	# need to add group ?
	if not group_seen:
		sink.write('[%s]\n' % group)

	# We either just added the group or it was the last group
	# but did not contain the option. It must have been the
	# last group then or else the following group would have
	# triggered the option writeout.
	sink.write('%s = %s\n' % (option, value))

#==================================================================
def __set_list_in_INI_file(src=None, sink=None, group=None, option=None, value=None):

	our_group_seen = False
	inside_our_group = False
	our_list_seen = False
	inside_our_list = False

	# loop until group found or src empty
	for line in src:

		if inside_our_list:			# can only be true if already inside our group
			# new list has been written already
			# so now at end of our (old) list ?
			if regex.match(r'\$%s\$' % option, line.strip()) is not None:
				inside_our_list = False
				continue
			# skip old list entries
			continue

		if inside_our_group:
			# our option ?
			if regex.match(r'%s(\s|\t)*=(\s|\t)*\$%s\$' % (option, option), line.strip()) is not None:
				sink.write(line)										# list header
				sink.write('\n'.join(value))
				sink.write('\n')
				sink.write('$%s$\n' % option)							# list footer
				our_list_seen = True
				inside_our_list = True
				continue

			# next group (= end of our group) ?
			if regex.match(r'\[.+\]', line.strip()) is not None:
				# our list already handled ?  (if so must already be finished)
				if not our_list_seen:
					# no, so need to add our list to the group before ...
					sink.write('%s = $%s$\n' % (option, option))		# list header
					sink.write('\n'.join(value))
					sink.write('\n')
					sink.write('$%s$\n' % option)						# list footer
					our_list_seen = True
					inside_our_list = False
				# ... starting the next group
				sink.write(line)				# next group header
				inside_our_group = False
				continue

			# other lines inside our group
			sink.write(line)
			continue

		# our group ?
		if line.strip() == '[%s]' % group:
			our_group_seen = True
			inside_our_group = True
			sink.write(line)						# group header
			continue

		sink.write(line)

	# looped over all lines but did not find our group, so add group
	if not our_group_seen:
		sink.write('[%s]\n' % group)

	if not our_list_seen:
		# We either just added the group or it was the last group
		# but did not contain the option. It must have been the
		# last group then or else the group following it would have
		# triggered the option writeout.
		sink.write('%s = $%s$\n' % (option, option))
		sink.write('\n'.join(value))
		sink.write('\n')
		sink.write('$%s$\n' % option)

#==================================================================
def set_option_in_INI_file(filename=None, group=None, option=None, value=None, encoding='utf8'):

	_log.debug('setting option "%s" to "%s" in group [%s]', option, value, group)
	_log.debug('file: %s (%s)', filename, encoding)

	sink = tempfile.NamedTemporaryFile(suffix = '.cfg', delete = True)
	sink_name = sink.name
	sink.close()	# close it so it gets deleted so we can safely open it again
	src = open(filename, mode = 'rt', encoding = encoding)
	sink = open(sink_name, mode = 'wt', encoding = encoding)

	# is value a list ?
	if isinstance(value, type([])):
		__set_list_in_INI_file(src, sink, group, option, value)
	else:
		__set_opt_in_INI_file(src, sink, group, option, value)

	sink.close()
	src.close()

	shutil.copy2(sink_name, filename)

#==================================================================
def parse_INI_stream(stream=None, encoding=None):
	"""Parse an iterable for INI-style data.

	Returns a dict by sections containing a dict of values per section.
	"""
	_log.debug('parsing INI-style data stream [%s] using [%s]', stream, encoding)

	if encoding is None:
		encoding = 'utf8'

	data = {}
	current_group = None
	current_option = None
	current_option_path = None
	inside_list = False
	line_idx = 0

	for line in stream:
		if type(line) is bytes:
			line = line.decode(encoding)
		line = line.replace('\015', '').replace('\012', '').strip()
		line_idx += 1

		if inside_list:
			if line == '$%s$' % current_option:		# end of list
				inside_list = False
				continue
			data[current_option_path].append(line)
			continue

		# noise
		if line == '' or line.startswith('#') or line.startswith(';'):
			continue

		# group
		if line.startswith('['):
			if not line.endswith(']'):
				_log.error('group line does not end in "]", aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')
			group = line.strip('[]').strip()
			if group == '':
				_log.error('group name is empty, aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')
			current_group = group
			continue

		# option
		if current_group is None:
			_log.warning('option found before first group, ignoring')
			_log.error(line)
			continue

		name, remainder = regex.split(r'\s*[=:]\s*', line, maxsplit = 1)
		if name == '':
			_log.error('option name empty, aborting')
			_log.error(line)
			raise ValueError('INI-stream parsing error')

		if remainder.strip() == '':
			if ('=' not in line) and (':' not in line):
				_log.error('missing name/value separator (= or :), aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')

		current_option = name
		current_option_path = '%s::%s' % (current_group, current_option)
		if current_option_path in data:
			_log.warning('duplicate option [%s]', current_option_path)

		value = remainder.split('#', 1)[0].strip()

		# start of list ?
		if value == '$%s$' % current_option:
			inside_list = True
			data[current_option_path] = []
			continue

		data[current_option_path] = value

	if inside_list:
		_log.critical('unclosed list $%s$ detected at end of config stream [%s]', current_option, stream)
		raise SyntaxError('end of config stream but still in list')

	return data
#==================================================================
class gmCfgData(gmBorg.cBorg):

	def __init__(self):
		try:
			self.__cfg_data
		except AttributeError:
			self.__cfg_data = {}
			self.source_files = {}

	#--------------------------------------------------
	def get(self, group=None, option=None, source_order=None):
		"""Get the value of a configuration option in a config file.

		<source_order> the order in which config files are searched
			a list of tuples (source, policy)
			policy:
				return: return only this value immediately
				append: append to list of potential values to return
				extend: if the value per source happens to be a list
				        extend (rather than append to) the result list

		returns NONE when there's no value for an option
		"""
		if source_order is None:
			source_order = [('internal', 'return')]
		results = []
		for source, policy in source_order:
			_log.debug('searching "%s" in [%s] in %s', option, group, source)
			if group is None:
				group = source
			option_path = '%s::%s' % (group, option)
			try: source_data = self.__cfg_data[source]
			except KeyError:
				_log.error('invalid config source [%s]', source)
				_log.debug('currently known sources: %s', list(self.__cfg_data))
				continue

			try: value = source_data[option_path]
			except KeyError:
				_log.debug('option [%s] not in group [%s] in source [%s]', option, group, source)
				continue
			_log.debug('option [%s] found in source [%s]', option_path, source)

			if policy == 'return':
				return value

			if policy == 'extend':
				if isinstance(value, type([])):
					results.extend(value)
				else:
					results.append(value)
			else:
				results.append(value)

		if len(results) == 0:
			return None

		return results

	#--------------------------------------------------
	def set_option(self, option=None, value=None, group=None, source=None):
		"""Set a particular option to a particular value.

		Note that this does NOT PERSIST the option anywhere !
		"""
		if None in [option, value]:
			raise ValueError('neither <option> nor <value> can be None')
		if source is None:
			source = 'internal'
			try:
				self.__cfg_data[source]
			except KeyError:
				self.__cfg_data[source] = {}
		if group is None:
			group = source
		option_path = '%s::%s' % (group, option)
		self.__cfg_data[source][option_path] = value
	#--------------------------------------------------
	# API: source related
	#--------------------------------------------------
	def add_stream_source(self, source=None, stream=None, encoding=None):
		data = parse_INI_stream(stream = stream, encoding = encoding)
		if source in self.__cfg_data:
			_log.warning('overriding source <%s> with [%s]', source, stream)

		self.__cfg_data[source] = data
	#--------------------------------------------------
	def add_file_source(self, source=None, filename=None, encoding='utf8'):
		"""Add a source (a file) to the instance."""

		_log.info('file source "%s": %s (%s)', source, filename, encoding)

		for existing_source, existing_file in self.source_files.items():
			if existing_file == filename:
				if source != existing_source:
					_log.warning('file [%s] already known as source [%s]', filename, existing_source)
					_log.warning('adding it as source [%s] may provoke trouble', source)

		cfg_file = None
		if filename is not None:
			try:
				cfg_file = open(filename, mode = 'rt', encoding = encoding)
			except IOError:
				_log.error('cannot open [%s], keeping as dummy source', filename)

		if cfg_file is None:
			filename = None
			if source in self.__cfg_data:
				_log.warning('overriding source <%s> with dummy', source)
			self.__cfg_data[source] = {}
		else:
			self.add_stream_source(source = source, stream = cfg_file)
			cfg_file.close()

		self.source_files[source] = filename

	#--------------------------------------------------
	def remove_source(self, source):
		"""Remove a source from the instance."""

		_log.info('removing source <%s>', source)

		try:
			del self.__cfg_data[source]
		except KeyError:
			_log.warning("source <%s> doesn't exist", source)

		try:
			del self.source_files[source]
		except KeyError:
			pass

	#--------------------------------------------------
	def reload_file_source(self, filename=None, encoding='utf8'):
		if filename not in self.source_files.values():
			return

		for src, fname in self.source_files.items():
			if fname == filename:
				self.add_file_source(source = src, filename = fname, encoding = encoding)
				# don't break the loop because there could be other sources
				# with the same file (not very reasonable, I know)
				#break

	#--------------------------------------------------
	def add_cli(self, short_options='', long_options=None):
		"""Add command line parameters to config data.

		short:
			string containing one-letter options such as u'h?' for -h -?
		long:
			list of strings
			'conf-file=' -> --conf-file=<...>
			'debug' -> --debug
		"""
		_log.info('adding command line arguments')
		_log.debug('raw command line is:')
		_log.debug('%s', sys.argv)
		import getopt
		if long_options is None:
			long_options = []
		try:
			opts, remainder = getopt.gnu_getopt (
				sys.argv[1:],
				short_options,
				long_options
			)
		except getopt.GetoptError as exc:
			_log.exception('error parsing command line options')
			print('GNUmed startup: error loading command line options')
			print('GNUmed startup:', exc)
			return False

		data = {}
		for opt, val in opts:
			if val == '':
				data['%s::%s' % ('cli', opt)] = True
			else:
				data['%s::%s' % ('cli', opt)] = val
		self.__cfg_data['cli'] = data
		return True

#==================================================================
# main
#==================================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	logging.basicConfig(level = logging.DEBUG)
	#-----------------------------------------
	def test_gmCfgData():
		cfg = gmCfgData()
		cfg.add_cli(short_options='h?', long_options=['help', 'conf-file='])
		cfg.set_option('internal option', True)
		print (cfg.get(option = '--help', source_order = [('cli', 'return')]))
		print (cfg.get(option = '-?', source_order = [('cli', 'return')]))
		fname = cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
		if fname is not None:
			cfg.add_file_source(source = 'explicit', filename = fname)
	#-----------------------------------------
	def test_set_list_opt():
		src = [
			'# a comment',
			'',
			'[empty group]',
			'[second group]',
			'some option = in second group',
			'# another comment',
			'[test group]',
			'',
			'test list 	= $test list$',
			'old 1',
			'old 2',
			'$test list$',
			'# another group:',
			'[dummy group]'
		]

		__set_list_in_INI_file (
			src = src,
			sink = sys.stdout,
			group = 'test group',
			option = 'test list',
			value = list('123')
		)
	#-----------------------------------------
	def test_set_opt():
		src = [
			'# a comment',
			'[empty group]',
			'# another comment',
			'',
			'[second group]',
			'some option = in second group',
			'',
			'[trap group]',
			'trap list 	= $trap list$',
			'dummy 1',
			'test option = a trap',
			'dummy 2',
			'$trap list$',
			'',
			'[test group]',
			'test option = for real (old)',
			''
		]

		__set_opt_in_INI_file (
			src = src,
			sink = sys.stdout,
			group = 'test group',
			option = 'test option',
			value = 'for real (new)'
		)

	#-----------------------------------------
	def test_parse_ini_stream():
		data = parse_INI_stream(stream = open(sys.argv[2], 'r', encoding = 'utf8'))
		for key in data:
			print(key, data[key])
		input()
		_cfg = gmCfgData()
		_cfg.add_file_source(source = 'prefs', filename = sys.argv[2])
		print(_cfg.get('preferences', 'login', [('prefs', 'return')]))
		print(_cfg.get('preferences', 'most recently used praxis branch', [('prefs', 'return')]))

	#-----------------------------------------
	#test_gmCfgData()
	#test_set_list_opt()
	test_set_opt()
	#test_parse_ini_stream()

#==================================================================
