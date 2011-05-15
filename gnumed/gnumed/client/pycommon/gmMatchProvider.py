"""Base classes for match providers.

They are used by business objects to give
phrasewheels the ability to guess phrases.

Copyright (C) GNUMed developers
license: GPL
"""
__version__ = "$Revision: 1.34 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>, S.J.Tan <sjtan@bigpond.com>"

# std lib
import string, types, time, sys, re as regex, logging


# GNUmed
from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.ui')
_log.info(__version__)


default_ignored_chars = "[?!.'\\(){}\[\]<>~#*$%^_]+" + '"'
default_word_separators = '[- \t=+&:@]+'
#============================================================
class cMatchProvider(object):
	"""Base class for match providing objects.

	Match sources might be:
	- database tables
	- flat files
	- previous input
	- config files
	- in-memory list created on the fly
	"""
	print_queries = False
	#--------------------------------------------------------
	def __init__(self):
		self.setThresholds()

		self._context_vals = {}
		self.__ignored_chars = regex.compile(default_ignored_chars)
		# used to normalize word boundaries:
		self.__word_separators = regex.compile(default_word_separators)
	#--------------------------------------------------------
	# actions
	#--------------------------------------------------------
	def getMatches(self, aFragment = None):
		"""Return matches according to aFragment and matching thresholds.

		FIXME: design decision: we dont worry about data source changes
			   during the lifetime of a MatchProvider
		FIXME: append _("*get all items*") on truncation
		"""
		# sanity check
		if aFragment is None:
			raise ValueError, 'Cannot find matches without a fragment.'

		# user explicitly wants all matches
		if aFragment == u'*':
			return self.getAllMatches()

		# case insensitivity
		tmpFragment = aFragment.lower()
		# remove ignored chars
		if self.__ignored_chars is not None:
			tmpFragment = self.__ignored_chars.sub('', tmpFragment)
		# normalize word separators
		if self.__word_separators is not None:
			tmpFragment = u' '.join(self.__word_separators.split(tmpFragment))
		# length in number of significant characters only
		lngFragment = len(tmpFragment)

		# order is important !
		if lngFragment >= self.__threshold_substring:
			return self.getMatchesBySubstr(tmpFragment)
		elif lngFragment >= self.__threshold_word:
			return self.getMatchesByWord(tmpFragment)
		elif lngFragment >= self.__threshold_phrase:
			return self.getMatchesByPhrase(tmpFragment)
		else:
			return (False, [])
	#--------------------------------------------------------
	def getAllMatches(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		raise NotImplementedError
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		raise NotImplementedError
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		raise NotImplementedError
	#--------------------------------------------------------
	# configuration
	#--------------------------------------------------------
	def setThresholds(self, aPhrase = 1, aWord = 3, aSubstring = 5):
		"""Set match location thresholds.

		- the fragment passed to getMatches() must contain at least this many
		  characters before it triggers a match search at:
		  1) phrase_start - start of phrase (first word)
		  2) word_start - start of any word within phrase
		  3) in_word - _inside_ any word within phrase
		"""
		# sanity checks
		if aSubstring < aWord:
			_log.error('Setting substring threshold (%s) lower than word-start threshold (%s) does not make sense. Retaining original thresholds (%s:%s, respectively).' % (aSubstring, aWord, self.__threshold_substring, self.__threshold_word))
			return False
		if aWord < aPhrase:
			_log.error('Setting word-start threshold (%s) lower than phrase-start threshold (%s) does not make sense. Retaining original thresholds (%s:%s, respectively).' % (aSubstring, aWord, self.__threshold_word, self.__threshold_phrase))
			return False

		# now actually reassign thresholds
		self.__threshold_phrase	= aPhrase
		self.__threshold_word	= aWord
		self.__threshold_substring	= aSubstring

		return True
	#--------------------------------------------------------
	def _set_word_separators(self, word_separators=None):
		if word_separators is None:
			self.__word_separators = None
		else:
			self.__word_separators = regex.compile(word_separators)

	def _get_word_separators(self):
		if self.__word_separators is None:
			return None
		return self.__word_separators.pattern

	word_separators = property(_get_word_separators, _set_word_separators)
	#--------------------------------------------------------
	def _set_ignored_chars(self, ignored_chars=None):
		if ignored_chars is None:
			self.__ignored_chars = None
		else:
			self.__ignored_chars = regex.compile(ignored_chars)

	def _get_ignored_chars(self):
		if self.__ignored_chars is None:
			return None
		return self.__ignored_chars.pattern

	ignored_chars = property(_get_ignored_chars, _set_ignored_chars)
	#--------------------------------------------------------
	def set_context (self, context=None, val=None):
		"""Set value to provide context information	for matches.

		The matching code may ignore it depending on its exact
		implementation. Names and values of the context depend
		on what is being matched.

		<context> -- the *placeholder* key *inside* the context
					 definition, not the context *definition* key
		"""
		if context is None:
			return False
		self._context_vals[context] = val
		return True
	#--------------------------------------------------------
	def unset_context(self, context=None):
		try:
			del self._context_vals[context]
		except KeyError:
			pass
#------------------------------------------------------------
# usable instances
#------------------------------------------------------------
class cMatchProvider_FixedList(cMatchProvider):
	"""Match provider where all possible options can be held
	   in a reasonably sized, pre-allocated list.
	"""
	def __init__(self, aSeq = None):
		"""aSeq must be a list of dicts. Each dict must have the keys (data, label, weight)
		"""
		if not type(aSeq) in [types.ListType, types.TupleType]:
			_log.error('fixed list match provider argument must be a list or tuple of dicts')
			raise TypeError('fixed list match provider argument must be a list or tuple of dicts')

		self.__items = aSeq
		cMatchProvider.__init__(self)
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		matches = []
		# look for matches
		for item in self.__items:
			# at start of phrase, that is
			if string.find(string.lower(item['label']), aFragment) == 0:
				matches.append(item)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_items)
		return (True, matches)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		matches = []
		# look for matches
		for item in self.__items:
			pos = string.find(string.lower(item['label']), aFragment)
			# found at start of phrase
			if pos == 0:
				matches.append(item)
			# found as a true substring
			elif pos > 0:
				# but use only if substring is at start of a word
				if (item['label'])[pos-1] == ' ':
					matches.append(item)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_items)
		return (True, matches)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		matches = []
		# look for matches
		for item in self.__items:
			if string.find(string.lower(item['label']), aFragment) != -1:
				matches.append(item)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_items)
		return (True, matches)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		matches = self.__items
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_items)
		return (True, matches)
	#--------------------------------------------------------
	def set_items(self, items):
		"""items must be a list of dicts. Each dict must have the keys (data, label, weight)"""
		self.__items = items
	#--------------------------------------------------------
	def __cmp_items(self, item1, item2):
		"""Compare items based on weight."""
		if item1['weight'] == item2['weight']:
			return 0

		# do it the wrong way round to do sorting/reversing at once
		if item1['weight'] < item2['weight']:
			return 1
		if item1['weight'] > item2['weight']:
			return -1
# ===========================================================
class cMatchProvider_Func(cMatchProvider):
	"""Match provider which searches matches
	   in the results of a function call.
	"""
	def __init__(self, get_candidates = None):
		"""get_candidates() must return a list of strings."""
		if get_candidates is None:
			_log.error('must define function to retrieve match candidates list')
			raise ValueError('must define function to retrieve match candidates list')

		self._get_candidates = get_candidates
		cMatchProvider.__init__(self)
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		print "getting phrase matches"
		matches = []
		candidates = self._get_candidates()
		# look for matches
		for candidate in candidates:
			# at start of phrase, that is
			if aFragment.startswith(candidate['label'].lower()):
				matches.append(candidate)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_candidates)
		return (True, matches)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		print "getting word matches"
		matches = []
		candidates = self._get_candidates()
		# look for matches
		for candidate in candidates:
			pos = candidate['label'].lower().find(aFragment)
#			pos = string.find(string.lower(candidate['label']), aFragment)
			# found as a true substring
			# but use only if substring is at start of a word
			# FIXME: use word seps
			if (pos == 0) or (candidate['label'][pos-1] == ' '):
				matches.append(candidate)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_candidates)
		return (True, matches)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		matches = []
		candidates = self._get_candidates()
		# look for matches
		for candidate in candidates:
			if candidate['label'].lower().find(aFragment) != -1:
#			if string.find(string.lower(candidate['label']), aFragment) != -1:
				matches.append(candidate)
		# no matches found
		if len(matches) == 0:
			return (False, [])

		matches.sort(self.__cmp_candidates)
		return (True, matches)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all candidates."""
		return self._get_candidates()
	#--------------------------------------------------------
	def __cmp_candidates(self, candidate1, candidate2):
		"""naive ordering"""
		return 0
		# FIXME: do ordering
#		if candidate1 < candidate2:
#			return -1
#		if candidate1 == candidate2:
#			return 0
#		return 1

# ===========================================================
class cMatchProvider_SQL2(cMatchProvider):
	"""Match provider which searches matches
	   in possibly several database tables.

	queries:
		- a list of unicode strings
		- each string is a query
		- each string must contain: "... where <column> %(fragment_condition)s ..."
		- each string can contain in the where clause: "... %(<context_key>)s ..."
		- each query must return (data, label)

	context definitions to be used in the queries
	example: {'ctxt_country': {'where_part': 'and country = %(country)s', 'placeholder': 'country'}}
	"""
	def __init__(self, queries = None, context = None):
		if type(queries) != types.ListType:
			queries = [queries]

		self._queries = queries

		if context is None:
			self._context = {}
		else:
			self._context = context

		self._args = {}
		cMatchProvider.__init__(self)
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		fragment_condition = u"ILIKE %(fragment)s"
		self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		fragment_condition = u"~* %(fragment)s"
		aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
		self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		fragment_condition = u"ILIKE %(fragment)s"
		self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return self.getMatchesBySubstr(u'')
	#--------------------------------------------------------
	def _find_matches(self, fragment_condition):
		if self.print_queries:
			print "----------------------"
		matches = []
		for query in self._queries:
			where_fragments = {'fragment_condition': fragment_condition}

			for context_key, context_def in self._context.items():
				try:
					placeholder = context_def['placeholder']
					where_part = context_def['where_part']
					self._args[placeholder] = self._context_vals[placeholder]
					# we do have a context value for this key, so add the where condition
					where_fragments[context_key] = where_part
					if self.print_queries:
						print "ctxt ph:", placeholder
						print "ctxt where:", where_part
						print "ctxt val:", self._context_vals[placeholder]
				except KeyError:
					# we don't have a context value for this key, so skip the where condition
					where_fragments[context_key] = u''

			cmd = query % where_fragments

			if self.print_queries:
				print "class:", self.__class__.__name__
				print "ctxt:", self._context_vals
				print "args:", self._args
				print "query:", cmd

			try:
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': self._args}])
			except:
				_log.exception('[%s]: error running match provider SQL, dropping query', self.__class__.__name__)
				idx = self._queries.index(query)
				del self._queries[idx]
				break

			# no matches found: try next query
			if len(rows) == 0:
				continue

			for row in rows:
				match = {'weight': 0}

				try:
					match['data'] = row['data']
				except KeyError:
					match['data'] = row[0]

				try:
					match['list_label'] = row['list_label']
				except KeyError:
					match['list_label'] = row[1]

				try:
					match['field_label'] = row['field_label']
				except KeyError:
					match['field_label'] = match['list_label']

				try:
					match['label'] = row['label']
				except KeyError:
					match['label'] = row['list_label']

				matches.append(match)

			return (True, matches)
		# none found whatsoever
		return (False, [])
#================================================================
if __name__ == '__main__':
	pass

#================================================================
