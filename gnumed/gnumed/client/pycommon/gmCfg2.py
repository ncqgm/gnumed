"""GNUmed configuration handling.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmCfg2.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL"


import logging, sys


if __name__ == "__main__":
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBorg


_log = logging.getLogger('gm.cfg')
_log.info(__version__)
#==================================================================
# helper functions
#==================================================================
def parse_INI_stream(stream=None):
	"""Parse an iterable for INI-style data."""

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
	def get(self, group=None, option=None, source_order=None, debug=False):
		"""Get the value of a configuration option in a config file.

		<source_order> the order in which config files are searched
			a list of tuples (source, policy)
			policy:
				return: return only this value immediately
				append: append to list of potential values to return

		returns NONE when there's no value for an option
		"""
		if source_order is None:
			source_order = [u'internal']
		results = []
		for source, policy in source_order:
			if group is None:
				group = source
			option_path = u'%s::%s' % (group, option)
			try: source_data = self.__cfg_data[source]
			except KeyError:
				_log.error('invalid config source [%s]', source)
				_log.debug('currently known sources: %s' % self.__cfg_data.keys())
				raise

			try: value = source_data[option_path]
			except KeyError:
				_log.debug('option [%s] not in group [%s] in source [%s]', option, group, source)
				continue

			if debug:
				_log.debug(u'option [%s] found in source [%s]', option_path, source)

			if policy == u'return':
				return value

			results.append(value)

		if len(results) == 0:
			return None

		return results
	#--------------------------------------------------
	def add_file_source(self, source=None, file=None, encoding=None):
		"""Add a source (a file) to the instance."""
		_log.info('file source "%s": %s (%s)', source, file, encoding)

		try:
			cfg_file = codecs.open(filename = file, mode = 'rU', encoding = encoding)
		except IOError:
			_log.error('cannot open [%s], keeping as dummy source', file)
			cfg_file = None

		if cfg_file is None:
			file = None
			data = {}
		else:
			try:
				data = parse_INI_stream(stream = cfg_file)
			except ValueError:
				_log.exception('error parsing source <%s> from [%s] (%s)', source, file, encoding)
				cfg_file.close()
				raise
			cfg_file.close()

		if self.__cfg_data.has_key(source):
			_log.warning('overriding source <%s> with [%s]', source, file)

		self.__cfg_data[source] = data
		self.source_files[source] = file
	#--------------------------------------------------
	def set_option(self, option=None, value=None, group=None, source=None):
		if None in [option, value]:
			raise ValueError('neither <option> nor <value> can be None')
		if source is None:
			source = u'internal'
		if group is None:
			group = source
		option_path = u'%s::%s' % (group, option)
		self.__cfg_data[source][option_path] = value
	#--------------------------------------------------
	def add_cli(self, short_options=u'', long_options=None):

		import getopt

		if long_options is None:
			long_options = []

		opts, remainder = getopt.gnu_getopt	(
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
#==================================================================
# main
#==================================================================
if __name__ == "__main__":

	logging.basicConfig(level = logging.DEBUG)

	def test_gmCfgData():
		cfg = gmCfgData()
		cfg.add_cli(short_options=u'h?', long_options=[u'help', u'conf-file'])
		print cfg.get(option = '--help', source_order = [('cli', 'return')])
		print cfg.get(option = '-?', source_order = [('cli', 'return')])
#		print cfg.get (
#			'a group',
#			'an option',
#			[('commandline', 'return'), ('local', 'return'), ('user', 'return'), ('system', 'return')]
#		)

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		test_gmCfgData()

#==================================================================
# $Log: gmCfg2.py,v $
# Revision 1.1  2007-12-23 11:53:13  ncq
# - a much improved cfg options interface
#   - no database handling yet
#
#