"""GNUmed configuration handling.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmCfg2.py,v $
__version__ = "$Revision: 1.16 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL"


import logging, sys, codecs, re as regex, shutil, os


if __name__ == "__main__":
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBorg


_log = logging.getLogger('gm.cfg')
_log.info(__version__)
#==================================================================
# helper functions
#==================================================================
def __set_opt_in_INI_file(src=None, sink=None, group=None, option=None, value=None):

	group_seen = False
	option_seen = False
	in_list = False

	for line in src:

		# after option already ?
		if option_seen:
			sink.write(line)
			continue

		# start of list ?
		if regex.match('(?P<list_name>.+)(\s|\t)*=(\s|\t)*\$(?P=list_name)\$', line) is not None:
			in_list = True
			sink.write(line)
			continue

		# end of list ?
		if regex.match('\$.+\$.*', line) is not None:
			in_list = False
			sink.write(line)
			continue

		# our group ?
		if line.strip() == u'[%s]' % group:
			group_seen = True
			sink.write(line)
			continue

		# another group ?
		if regex.match('\[.+\].*', line) is not None:
			# next group but option not seen yet ?
			if group_seen and not option_seen:
				sink.write(u'%s = %s\n\n\n' % (option, value))
				option_seen = True
			sink.write(line)
			continue

		# our option ?
		if regex.match('%s(\s|\t)*=' % option, line) is not None:
			if group_seen:
				sink.write(u'%s = %s\n' % (option, value))
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
	sink.write(u'%s = %s\n' % (option, value))
#==================================================================
def __set_list_in_INI_file(src=None, sink=None, group=None, option=None, value=None):

	group_seen = False
	option_seen = False
	in_list = False

	for line in src:

		# found option but still in (old) list ?
		if option_seen and in_list:
			# end of (old) list ?
			if regex.match('\$.+\$.*', line) is not None:
				in_list = False
				sink.write(line)
				continue
			continue

		# after option already and not in (old) list anymore ?
		if option_seen and not in_list:
			sink.write(line)
			continue

		# start of list ?
		match = regex.match('(?P<list_name>.+)(\s|\t)*=(\s|\t)*\$(?P=list_name)\$', line)
		if match is not None:
			in_list = True
			# our list ?
			if group_seen and (match.group('list_name') == option):
				option_seen = True
				sink.write(line)
				sink.write('\n'.join(value))
				sink.write('\n')
				continue
			sink.write(line)
			continue

		# end of list ?
		if regex.match('\$.+\$.*', line) is not None:
			in_list = False
			sink.write(line)
			continue

		# our group ?
		if line.strip() == u'[%s]' % group:
			group_seen = True
			sink.write(line)
			continue

		# another group ?
		if regex.match('\[%s\].*' % group, line) is not None:
			# next group but option not seen yet ?
			if group_seen and not option_seen:
				option_seen = True
				sink.write('%s = $%s$\n' % (option, option))
				sink.write('\n'.join(value))
				sink.write('\n')
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
	sink.write('%s = $%s$\n' % (option, option))
	sink.write('\n'.join(value))
	sink.write('\n')
	sink.write('$%s$\n' % option)
#==================================================================
def set_option_in_INI_file(filename=None, group=None, option=None, value=None, encoding='utf8'):

	_log.debug('setting option "%s" to "%s" in group [%s]', option, value, group)
	_log.debug('file: %s (%s)', filename, encoding)

	src = codecs.open(filename = filename, mode = 'rU', encoding = encoding)
	# FIXME: add "." right before the *name* part of filename - this
	# FIXME: requires proper parsing (think of /home/lala/ -> ./home/lala vs /home/lala/gnumed/.gnumed.conf)
	sink_name = '%s.gmCfg2.new.conf' % filename
	sink = codecs.open(filename = sink_name, mode = 'wb', encoding = encoding)

	# is value a list ?
	if isinstance(value, type([])):
		__set_list_in_INI_file(src, sink, group, option, value)
	else:
		__set_opt_in_INI_file(src, sink, group, option, value)

	sink.close()
	src.close()

	shutil.copy2(sink_name, filename)
	os.remove(sink_name)
#==================================================================
def parse_INI_stream(stream=None):
	"""Parse an iterable for INI-style data.

	Returns a dict by sections containing a dict of values per section.
	"""
	_log.debug(u'parsing INI-style data stream [%s]' % stream)

	data = {}
	current_group = None
	current_option = None
	current_option_path = None
	inside_list = False
	line_idx = 0

	for line in stream:
		line = line.replace(u'\015', u'').replace(u'\012', u'').strip()
		line_idx += 1

		if inside_list:
			if line == u'$%s$' % current_option:		# end of list
				inside_list = False
				continue
			data[current_option_path].append(line)
			continue

		# noise
		if line == u'' or line.startswith(u'#') or line.startswith(u';'):
			continue

		# group
		if line.startswith(u'['):
			if not line.endswith(u']'):
				_log.error(u'group line does not end in "]", aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')
			group = line.strip(u'[]').strip()
			if group == u'':
				_log.error(u'group name is empty, aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')
			current_group = group
			continue

		# option
		if current_group is None:
			_log.warning('option found before first group, ignoring')
			_log.error(line)
			continue

		name, remainder = regex.split('\s*[=:]\s*', line, maxsplit = 1)
		if name == u'':
			_log.error('option name empty, aborting')
			_log.error(line)
			raise ValueError('INI-stream parsing error')

		if remainder.strip() == u'':
			if (u'=' not in line) and (u':' not in line):
				_log.error('missing name/value separator (= or :), aborting')
				_log.error(line)
				raise ValueError('INI-stream parsing error')

		current_option = name
		current_option_path = '%s::%s' % (current_group, current_option)
		if data.has_key(current_option_path):
			_log.warning(u'duplicate option [%s]', current_option_path)

		value = remainder.split(u'#', 1)[0].strip()

		# start of list ?
		if value == '$%s$' % current_option:
			inside_list = True
			data[current_option_path] = []
			continue

		data[current_option_path] = value

	if inside_list:
		_log.panic('unclosed list $%s$ detected at end of config stream [%s]', current_option, stream)
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

		returns NONE when there's no value for an option
		"""
		if source_order is None:
			source_order = [(u'internal', u'return')]
		results = []
		for source, policy in source_order:
			if group is None:
				group = source
			option_path = u'%s::%s' % (group, option)
			try: source_data = self.__cfg_data[source]
			except KeyError:
				_log.error('invalid config source [%s]', source)
				_log.debug('currently known sources: %s', self.__cfg_data.keys())
				#raise
				continue

			try: value = source_data[option_path]
			except KeyError:
				_log.debug('option [%s] not in group [%s] in source [%s]', option, group, source)
				continue
			_log.debug(u'option [%s] found in source [%s]', option_path, source)

			if policy == u'return':
				return value

			results.append(value)

		if len(results) == 0:
			return None

		return results
	#--------------------------------------------------
	def add_stream_source(self, source=None, stream=None):

		try:
			data = parse_INI_stream(stream = stream)
		except ValueError:
			_log.exception('error parsing source <%s> from [%s]', source, stream)
			raise

		if self.__cfg_data.has_key(source):
			_log.warning('overriding source <%s> with [%s]', source, stream)

		self.__cfg_data[source] = data
	#--------------------------------------------------
	def add_file_source(self, source=None, file=None, encoding='utf8'):
		"""Add a source (a file) to the instance."""

		_log.info('file source "%s": %s (%s)', source, file, encoding)

		cfg_file = None
		if file is not None:
			try:
				cfg_file = codecs.open(filename = file, mode = 'rU', encoding = encoding)
			except IOError:
				_log.error('cannot open [%s], keeping as dummy source', file)

		if cfg_file is None:
			file = None
			if self.__cfg_data.has_key(source):
				_log.warning('overriding source <%s> with dummy', source)
			self.__cfg_data[source] = {}
		else:
			self.add_stream_source(source = source, stream = cfg_file)
			cfg_file.close()

		self.source_files[source] = file
	#--------------------------------------------------
	def add_cli(self, short_options=u'', long_options=None):
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

		opts, remainder = getopt.gnu_getopt (
			sys.argv[1:],
			short_options,
			long_options
		)

		data = {}
		for opt, val in opts:
			if val == u'':
				data[u'%s::%s' % (u'cli', opt)] = True
			else:
				data[u'%s::%s' % (u'cli', opt)] = val

		self.__cfg_data[u'cli'] = data
	#--------------------------------------------------
	def reload_file_source(self, file=None, encoding='utf8'):
		if file not in self.source_files.values():
			return

		for src, fname in self.source_files.iteritems():
			if fname == file:
				self.add_file_source(source = src, file = fname, encoding = encoding)
				break
	#--------------------------------------------------
	def set_option(self, option=None, value=None, group=None, source=None):
		"""Set a particular option to a particular value.

		Note that this does NOT PERSIST the option anywhere !
		"""
		if None in [option, value]:
			raise ValueError('neither <option> nor <value> can be None')
		if source is None:
			source = u'internal'
			try:
				self.__cfg_data[source]
			except KeyError:
				self.__cfg_data[source] = {}
		if group is None:
			group = source
		option_path = u'%s::%s' % (group, option)
		self.__cfg_data[source][option_path] = value
#==================================================================
# main
#==================================================================
if __name__ == "__main__":

	logging.basicConfig(level = logging.DEBUG)
	#-----------------------------------------
	def test_gmCfgData():
		cfg = gmCfgData()
		cfg.add_cli(short_options=u'h?', long_options=[u'help', u'conf-file='])
		cfg.set_option('internal option', True)
		print cfg.get(option = '--help', source_order = [('cli', 'return')])
		print cfg.get(option = '-?', source_order = [('cli', 'return')])
		fname = cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
		if fname is not None:
			cfg.add_file_source(source = 'explicit', file = fname)
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
			group = u'test group',
			option = u'test list',
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
			group = u'test group',
			option = u'test option',
			value = u'for real (new)'
		)
	#-----------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		test_gmCfgData()
		#test_set_list_opt()
		#test_set_opt()

#==================================================================
# $Log: gmCfg2.py,v $
# Revision 1.16  2008-08-31 14:51:42  ncq
# - properly handle explicit file=None for dummy sources
#
# Revision 1.15  2008/08/03 20:03:11  ncq
# - do not simply add "." before the entire path of the dummy
#   conf file when setting option - it should go right before the name part
#
# Revision 1.14  2008/07/17 21:30:01  ncq
# - detect unterminated list option
#
# Revision 1.13  2008/07/16 10:36:25  ncq
# - fix two bugs in INI parsing
# - better logging, some cleanup
# - .reload_file_source
#
# Revision 1.12  2008/07/07 11:33:57  ncq
# - a bit of cleanup
#
# Revision 1.11  2008/05/21 13:58:50  ncq
# - factor out add_stream_source from add_file_source
#
# Revision 1.10  2008/03/09 20:15:29  ncq
# - don't fail on non-existing sources
# - cleanup
# - better docs
#
# Revision 1.9  2008/01/27 21:09:38  ncq
# - set_option_in_INI_file() and tests
#
# Revision 1.8  2008/01/11 16:10:35  ncq
# - better logging
#
# Revision 1.7  2008/01/07 14:12:33  ncq
# - add some documentation to add_cli()
#
# Revision 1.6  2007/12/26 22:43:28  ncq
# - source order needs policy
#
# Revision 1.5  2007/12/26 21:50:45  ncq
# - missing continue
# - better test suite
#
# Revision 1.4  2007/12/26 21:11:11  ncq
# - need codecs
#
# Revision 1.3  2007/12/26 20:47:22  ncq
# - need to create internal source if doesn't exist
#
# Revision 1.2  2007/12/26 20:18:03  ncq
# - fix test suite
#
# Revision 1.1  2007/12/23 11:53:13  ncq
# - a much improved cfg options interface
#   - no database handling yet
#
#