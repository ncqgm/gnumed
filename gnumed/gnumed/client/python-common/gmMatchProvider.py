"""Base classes for match providers.

They are used by business objects to give
phrasewheels the ability to guess phrases.

Copyright (C) GNUMed developers
license: GPL
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmMatchProvider.py,v $
# $Id: gmMatchProvider.py,v 1.9 2003-11-20 02:16:03 sjtan Exp $
__version__ = "$Revision: 1.9 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>, S.J.Tan <sjtan@bigpond.com>"

import string, types, time, sys, re
import gmPG, gmExceptions

_true = (1==1)
_false = (1==0)

import gmLog
_log = gmLog.gmDefLog

#------------------------------------------------------------
# generic base class
#------------------------------------------------------------
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
		self._context_val = {}
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
			return (_false, [])

		# sanity check
		if aFragment is None:
			_log.Log(gmLog.lErr, 'Cannot find matches without a fragment.')
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
		if lngFragment >= self.__threshold['substring']:
			return self.getMatchesBySubstr(tmpFragment)
		elif lngFragment >= self.__threshold['word']:
			return self.getMatchesByWord(tmpFragment)
		elif lngFragment >= self.__threshold['phrase']:
			return self.getMatchesByPhrase(tmpFragment)
		else:
			return (_false, [])
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
			_log.Log(gmLog.lErr, 'Setting substring threshold (%s) lower than word-start threshold (%s) does not make sense. Retaining original thresholds (%s:%s, respectively).' % (aSubstring, aWord, self.__threshold['substring'], self.__threshold['word']))
			return (1==0)
		if aWord < aPhrase:
			_log.Log(gmLog.lErr, 'Setting word-start threshold (%s) lower than phrase-start threshold (%s) does not make sense. Retaining original thresholds (%s:%s, respectively).' % (aSubstring, aWord, self.__threshold['word'], self.__threshold['phrase']))
			return (1==0)

		# now actually reassign thresholds
		self.__threshold['phrase']	= aPhrase
		self.__threshold['word']	= aWord
		self.__threshold['substring']	= aSubstring

		return _true
	#--------------------------------------------------------
	def setWordSeparators(self, separators = None):
		if separators is None:
			self.word_separators = cMatchProvider.default_word_separators
			return 1
		if separators == "":
			_log.Log(gmLog.lErr, 'Not defining any word separators does not make sense ! Keeping previous setting.')
			return None
		try:
			self.word_separators = re.compile(separators)
		except:
			_log.LogException('cannot compile word separators regex >>>%s<<<, keeping previous setting' % separators)
			return None
		return _true
	#--------------------------------------------------------
	def setIgnoredChars(self, ignored_chars = None):
		if ignored_chars is None:
			self.ignored_chars = cMatchProvider.default_ignored_chars
			return 1
		try:
			self.ignored_chars = re.compile(ignored_chars)
		except:
			_log.LogException('cannot compile ignored_chars regex >>>%s<<<, keeping previous setting' % ignored_chars)
			return None
		return _true
	#--------------------------------------------------------
	def disableMatching(self):
		"""Don't search for matches.

		Useful if a slow network database link is detected, for example.
		"""
		self.__deliverMatches = _false
	#--------------------------------------------------------
	def enableMatching(self):
		self.__deliverMatches = _true
	#--------------------------------------------------------
	def disableLearning(self):
		"""Immediately stop learning new items."""
		self.__learnNewItems = _false
	#--------------------------------------------------------
	def enableLearning(self):
		"""Immediately start learning new items."""
		self.__learnNewItems = _true
	#--------------------------------------------------------
	def setContext (self, name, val):
		""" sets values to provide context information
		for matches. The matching code may ignore it depending
		on it's exact implementation. names and values of the
		context depend on what is being matched.
		can pass a fixed value, in which case it is nt called,
		but used in context as is (i.e a constant context)
		"""
		self._context_val[name] = val
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
			_log.Log(gmLog.lErr, 'fixed list match provider argument must be a list or tuple of dicts')
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
			return (_false, [])

		matches.sort(self.__cmp_items)
		return (_true, matches)
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
			return (_false, [])

		matches.sort(self.__cmp_items)
		return (_true, matches)
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
			return (_false, [])

		matches.sort(self.__cmp_items)
		return (_true, matches)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		matches = self.__items
		# no matches found
		if len(matches) == 0:
			return (_false, [])

		matches.sort(self.__cmp_items)
		return (_true, matches)
	#--------------------------------------------------------
	def setItems(self, items):
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
#------------------------------------------------------------
class cMatchProvider_SQL(cMatchProvider):
	"""Match provider which searches matches
	   in possibly several database tables.
	"""
	def __init__(self, source_defs, score_def = []):
		"""
		source_defs is a list of dictionaries of (pk, column, table, extra conditions, limit)
		column: the column containing the string to be matched
		pk: the primary key's column name
		table: the table (in reality will nearly always be a view)
		limit: the max. number of returned rows
		extra conditions: a dictionary, where keys are context variables, values are
		SQL expressions applying that context to the query
		"""
		self.dbpool = gmPG.ConnectionPool()

		# sanity check table connections
		self.srcs = []
		for src_def in source_defs:
			# FIXME: testing every table at load time is going to get slow
			# that remains to be seen
			conn = self.dbpool.GetConnection(src_def['service'])
			if conn is None:
				self.__close_sources()
				raise gmExceptions.ConstructorError, 'cannot connect to source service [%s]' % src_def['service']
			curs = conn.cursor()
			cmd = "select %s from %s limit 1" % (src_def['column'], src_def['table'])
			if not gmPG.run_query(curs, cmd):
				curs.close()
				self.__close_sources()
				raise gmExceptions.ConstructorError, 'cannot access [%s.%s] in service [%s]' % (src_def['table'], src_def['column'], src_def['service'])
			if not src_def.has_key('pk'):
				pk = gmPG.get_pkey_name(curs, src_def['table'])
				if pk is None:
					src_def['pk'] = "oid"
				else:
					src_def['pk'] = pk
			curs.close()
			src_def['conn'] = conn
			self.srcs.append(src_def)
			_log.Log(gmLog.lData, 'valid match source: %s' % src_def)

		if score_def <> []:
			rw_conn = self.dbpool.GetConnection(score_def['service'], readonly = 0)
			if rw_conn is None:
				self.__close_sources()
				raise gmExceptions.ConstructorError, 'cannot connect to score storage service [%s]' % score_def['service']
			rw_curs = rw_conn.cursor()
			cmd = "select %s, cookie, user, score from %s limit 1" % (score_def['column'], score_def['table'])
			if not gmPG.run_query(rw_curs, cmd):
				rw_curs.close()
				rw_conn.close()
				self.__close_sources()
				raise gmExceptions.ConstructorError, 'cannot access [%s.{%s/gmpw_user/gmpw_score}] in service [%s]' % (score_def['table'], score_def['column'], score_def['service'])
			if not score_def.has_key('pk'):
				pk = gmPG.get_pkey_name(rw_curs, score_def['table'])
				if pk is None:
					score_def['pk'] = "oid"
				else:
					score_def['pk'] = pk
			rw_curs.close()
			score_def['conn'] = rw_conn
#			score_def['query'] = "select %s, %s from %s where %s" % (
#				src_def['pk'],
#				src_def['column'],
#				src_def['table'],
#				src_def['column'])
			self.score_def = score_def
			_log.Log(gmLog.lData, 'valid score storage target: %s' % score_def)

		cMatchProvider.__init__(self)
	#--------------------------------------------------------
	def __close_sources(self):
		for src in self.srcs:
			self.dbpool.ReleaseConnection(src['service'])
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
		condition = "ilike"
		fragment = "%s%%" % aFragment
		return self.__find_matches(condition, fragment)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		condition = "~*"
		fragment = "( %s)|(^%s)" % (aFragment, aFragment)
		return self.__find_matches(condition, fragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		condition = "ilike"
		fragment = "%%%s%%" % aFragment
		return self.__find_matches(condition, fragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return self.getMatchesBySubstr('')
	#--------------------------------------------------------
	def __find_matches(self, search_condition, aFragment):
		matches = []
		for src in self.srcs:
			curs = src['conn'].cursor()
			# FIXME: deal with gmpw_score...
			ctxt_where = ''
			values = [aFragment]
			# any extra conditions defined for this source ?
			if src.has_key('extra conditions'):
				# loop over name and condition for contexts
				for ctxt_name, ctxt_condition in src['extra conditions'].iteritems():
					# value known for this context condition ?
					if self._context_val.has_key(ctxt_name) and self._context_val[ctxt_name]:
						# add context condition
						ctxt_where += " and (%s)" % ctxt_condition
						# remember value for condition
						values.append(self._context_val[ctxt_name])
			# do we have any contexts that always apply ?
			if src['extra conditions'].has_key('default'):
				ctxt_where += " and (%s)" % src['extra conditions']['default']

			cmd = "select %s, %s from %s where %s %s %%s %s" % (
				src['pk'],
				src['column'],
				src['table'],
				src['column'],
				search_condition,
				ctxt_where
			)
			if not gmPG.run_query(curs, cmd, values):
				curs.close()
				_log.Log(gmLog.lErr, 'cannot check for matches in %s' % src)
				return (_false, [])
			matching_rows = curs.fetchall()
			curs.close()
			for row in matching_rows:
				matches.append({'data': row[0], 'label': row[1], 'weight':0})

		# no matches found
		if len(matches) == 0:
			return (_false, [])

		matches.sort(self.__cmp_items)
		return (_true, matches)
	#--------------------------------------------------------
	def __cmp_items(self, item1, item2):
		"""naive ordering"""
		if item1 < item2:
			return -1
		if item1 == item2:
			return 0
		return 1


# FUTURE: a cMatchProvider_LDAP

#================================================================
# $Log: gmMatchProvider.py,v $
# Revision 1.9  2003-11-20 02:16:03  sjtan
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
