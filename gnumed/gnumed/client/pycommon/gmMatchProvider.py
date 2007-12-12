"""Base classes for match providers.

They are used by business objects to give
phrasewheels the ability to guess phrases.

Copyright (C) GNUMed developers
license: GPL
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmMatchProvider.py,v $
# $Id: gmMatchProvider.py,v 1.25 2007-12-12 16:17:15 ncq Exp $
__version__ = "$Revision: 1.25 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>, S.J.Tan <sjtan@bigpond.com>"

# std lib
import string, types, time, sys, re, logging


# GNUmed
import gmPG2, gmExceptions


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#============================================================
class cMatchProvider:
	"""Base class for match providing objects.

	Match sources might be:
	- database tables
	- flat files
	- previous input
	- config files
	- in-memory list created on the fly
	"""
	__threshold = {}
	default_word_separators = re.compile('[- \t=+&:@]+')
	default_ignored_chars = re.compile("[?!.'\\(){}\[\]<>~#*$%^_]+" + '"')
	#--------------------------------------------------------
	def __init__(self):
		self.enableMatching()
		self.enableLearning()
		self.setThresholds()
		self.setWordSeparators()
		self.setIgnoredChars()
		self._context_vals = {}
	#--------------------------------------------------------
	# actions
	#--------------------------------------------------------
	def getMatches(self, aFragment = None):
		"""Return matches according to aFragment and matching thresholds.

		FIXME: design decision: we dont worry about data source changes
			   during the lifetime of a MatchProvider
		FIXME: sort according to weight
		FIXME: append _("*get all items*") on truncation
		"""
		# do we return matches at all ?
		if not self.__deliverMatches:
			return (False, [])

		# sanity check
		if aFragment is None:
			raise ValueError, 'Cannot find matches without a fragment.'

		# user explicitely wants all matches
		if aFragment == "*":
			return self.getAllMatches()

		# case insensitivity
		tmpFragment = string.lower(aFragment)
		# remove ignored chars
		tmpFragment = self.ignored_chars.sub('', tmpFragment)
		# normalize word separators
		tmpFragment = string.join(self.word_separators.split(tmpFragment), ' ')
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
		pass
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		pass
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		pass
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		pass
	#--------------------------------------------------------
	def increaseScore(self, anItem):
		"""Increase the score/weighting for a particular item due to it being used."""
		pass
	#--------------------------------------------------------
	def learn(self, anItem, aContext):
		"""Add this item to the match source so we can find it next time around.

		- aContext can be used to denote the context where to use this item for matching
		- it is typically used to select a context sensitive item list during matching
		"""
		pass
	#--------------------------------------------------------
	def forget(self, anItem, aContext):
		"""Remove this item from the match source if possible."""
		pass
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
			return (1==0)
		if aWord < aPhrase:
			_log.error('Setting word-start threshold (%s) lower than phrase-start threshold (%s) does not make sense. Retaining original thresholds (%s:%s, respectively).' % (aSubstring, aWord, self.__threshold_word, self.__threshold_phrase))
			return (1==0)

		# now actually reassign thresholds
		self.__threshold_phrase	= aPhrase
		self.__threshold_word	= aWord
		self.__threshold_substring	= aSubstring

		return True
	#--------------------------------------------------------
	def setWordSeparators(self, separators = None):
		if separators is None:
			self.word_separators = cMatchProvider.default_word_separators
			return 1
		if separators == "":
			_log.error('Not defining any word separators does not make sense ! Keeping previous setting.')
			return None
		try:
			self.word_separators = re.compile(separators)
		except:
			_log.exception('cannot compile word separators regex >>>%s<<<, keeping previous setting' % separators)
			return None
		return True
	#--------------------------------------------------------
	def setIgnoredChars(self, ignored_chars = None):
		if ignored_chars is None:
			self.ignored_chars = cMatchProvider.default_ignored_chars
			return 1
		try:
			self.ignored_chars = re.compile(ignored_chars)
		except:
			_log.exception('cannot compile ignored_chars regex >>>%s<<<, keeping previous setting' % ignored_chars)
			return None
		return True
	#--------------------------------------------------------
	def disableMatching(self):
		"""Don't search for matches.

		Useful if a slow network database link is detected, for example.
		"""
		self.__deliverMatches = False
	#--------------------------------------------------------
	def enableMatching(self):
		self.__deliverMatches = True
	#--------------------------------------------------------
	def disableLearning(self):
		"""Immediately stop learning new items."""
		self.__learnNewItems = False
	#--------------------------------------------------------
	def enableLearning(self):
		"""Immediately start learning new items."""
		self.__learnNewItems = True
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
			raise gmExceptions.ConstructorError

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
	def setItems(self, items):
		"""items must be a list of dicts. Each dict must have the keys (data, label, weight)"""
		self.__items = items
	#--------------------------------------------------------
	def __cmp_items(self, item1, item2):
		"""Compare items based on weight."""
		# do it the wrong way round to do sorting/reversing at once
		if item1['weight'] < item2['weight']:
			return 1
		elif item1['weight'] > item2['weight']:
			return -1
		else:
			return 0
# ===========================================================
class cMatchProvider_Func(cMatchProvider):
	"""Match provider which searches matches
	   in the results of a function call.
	"""
	def __init__(self, get_candidates = None):
		"""get_candidates() must return a list of strings."""
		if get_candidates is None:
			_log.error('must define function to retrieve match candidates list')
			raise gmException.ConstructorError, 'must define match candidates function'
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
	"""
	def __init__(self, queries = None, context = None):
		if type(queries) != types.ListType:
			queries = [queries]

		# queries: a list of unicode strings
		# each string is a query
		# each string must contain: "... where <column> %(fragment_condition)s ..."
		# each string can contain in the where clause: "... %(<context_key>)s ..."
		self._queries = queries

		# context definitions to be used in the queries
		# example: {'ctxt_country': {'where_part': 'and country=%(country)', 'placeholder': 'country'}}
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
		fragment_condition = u"ilike %(fragment)s"
		self._args['fragment'] = u"%s%%" % aFragment
		return self.__find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		fragment_condition = u"~* %(fragment)s"
		aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
		self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)
		return self.__find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		fragment_condition = u"ilike %(fragment)s"
		self._args['fragment'] = u"%%%s%%" % aFragment
		return self.__find_matches(fragment_condition)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return self.getMatchesBySubstr('')
	#--------------------------------------------------------
	def __find_matches(self, fragment_condition):
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
				except KeyError:
					# we don't have a context value for this key, so skip the where condition
					where_fragments[context_key] = u''

			cmd = query % where_fragments

			try:
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': self._args}])
			except:
				_log.exception('Error running match provider SQL, dropping query.')
				idx = self._queries.index(query)
				del self._queries[idx]
				break

			# no matches found: try next query
			if len(rows) == 0:
				continue

			for row in rows:
				matches.append({'data': row[0], 'label': row[1], 'weight': 0})

			return (True, matches)
		# none found whatsoever
		return (False, [])
#================================================================
if __name__ == '__main__':
	pass

#================================================================
# $Log: gmMatchProvider.py,v $
# Revision 1.25  2007-12-12 16:17:15  ncq
# - better logger names
#
# Revision 1.24  2007/12/11 14:31:11  ncq
# - use std logging
#
# Revision 1.23  2007/12/02 20:59:13  ncq
# - drop failing queries
#
# Revision 1.22  2007/07/03 15:57:24  ncq
# - use gmPG2.sanitize_pg_regex()
# - ignore failing match retrieval queries such
#   that we don't freak out in the phrasewheel
#
# Revision 1.21  2007/01/07 23:02:11  ncq
# - more documentation on context
#
# Revision 1.20  2006/11/06 09:59:42  ncq
# - when allowing non-list strings to turn into query list do not
#   str() them or else we may lose unicodity
# - more u''ing
#
# Revision 1.19  2006/11/05 16:07:31  ncq
# - *_SQL2 now really handles context values, tested, too
# - some u''-ification
# - don't sort items in *_SQL2, rely on in-query ORDER BY instead
#
# Revision 1.18  2006/10/24 13:18:29  ncq
# - switch to gmPG2
# - remove cMatchProvider_SQL()
#
# Revision 1.17  2006/05/25 22:13:30  ncq
# - robustify set_context()
#
# Revision 1.16  2006/05/01 18:46:05  ncq
# - cleanup
#
# Revision 1.15  2005/06/14 18:54:40  ncq
# - don't sort in SQL2 matcher - queries should ORDER BY
#
# Revision 1.14  2005/06/12 21:20:55  ncq
# - make SQL2 match provider more robust regarding query list
#
# Revision 1.13  2005/06/12 21:16:55  ncq
# - make SQL2 match provider accept a query list
#
# Revision 1.12  2005/06/10 17:07:34  cfmoro
# Fixed set_context in SQL2
#
# Revision 1.11  2005/06/08 01:27:12  cfmoro
# Renamed function to make parent set_context work
#
# Revision 1.10  2005/06/07 10:16:37  ncq
# - setContext -> set_context
#
# Revision 1.9  2005/05/08 21:40:57  ncq
# - cleanup
#
# Revision 1.8  2005/04/14 18:24:57  ncq
# - some cleanup of funky magic so we are faster
#
# Revision 1.7  2005/04/11 18:00:54  ncq
# - cleanup
#
# Revision 1.6  2005/03/14 14:35:27  ncq
# - add match provider class cMatchProvider_Func which pulls
#   match candidates through a function
#
# Revision 1.5  2004/07/17 21:08:51  ncq
# - gmPG.run_query() now has a verbosity parameter, so use it
#
# Revision 1.4  2004/05/02 22:54:43  ncq
# - cleanup
#
# Revision 1.3  2004/04/30 09:10:57  ncq
# - label needs to be str()ed in list.append()
#
# Revision 1.2  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.13  2004/01/12 13:10:27  ncq
# - remove debugging code
#
# Revision 1.12  2004/01/06 10:02:47  ncq
# - add _SQL2 match provider that operates on queries rather than tables/columns
#
# Revision 1.11  2003/12/29 16:28:04  uid66147
# - I think we got the indentation level wrong when
#   applying the extra condition default context
#
# Revision 1.10  2003/11/20 08:55:05  ncq
# - some internal cleanup/renaming
#
# Revision 1.9  2003/11/20 02:16:03  sjtan
#
# make __context_val  in base class gmMatchProvider protected instead of class private, so subclasses can
# access it.
#
# Revision 1.8  2003/11/20 01:37:05  sjtan
#
# syntax correction.
#
# Revision 1.7  2003/11/20 00:33:12  ncq
# - improve comments on extra conditions in __find_matches()
#
# Revision 1.6  2003/11/19 23:18:37  ncq
# - some cleanup
#
