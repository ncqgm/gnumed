"""
A class, extending wxTextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
#@copyright: GPL

############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPhraseWheel.py,v $
# $Id: gmPhraseWheel.py,v 1.13 2003-09-29 00:16:55 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan <sjtan@bigpond.com>"

import string, types, time, sys, re

if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog
import gmExceptions, gmPG

from wxPython.wx import *

import mx.DateTime as mxDT

_true = (1==1)
_false = (1==0)
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
	default_ignored_chars = re.compile("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
	#--------------------------------------------------------
	def __init__(self):
		self.enableMatching()
		self.enableLearning()
		self.setThresholds()
		self.setWordSeparators()
		self.ignored_chars = cMatchProvider.default_ignored_chars
	#--------------------------------------------------------
	# actions
	#--------------------------------------------------------
	def getMatches(self, aFragment = None):
		"""Return matches according to aFragment and matching thresholds.

		FIXME: design decision: we don't worry about data source changes
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
#------------------------------------------------------------
# usable instances
#------------------------------------------------------------
class cMatchProvider_FixedList(cMatchProvider):
	"""Match provider where all possible options can be held
	   in a reasonably sized, pre-allocated list.
	"""
	def __init__(self, aSeq = None):
		"""aSeq must be a list of dicts. Each dict must have the keys (ID, label, weight)
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

	Each table must have a primary key, at least one column
	providing terms to match, a gmpw_user field and a gmpw_score
	field.
	"""
	def __init__(self, source_defs):
		self.dbpool = gmPG.ConnectionPool()

		# sanity check table connections
		self.srcs = []
		for src_def in source_defs:
			tmp = {
				'service': src_def['service'],
				'table': src_def['table'],
				'col': src_def['column'],
				'limit': src_def['limit']
			}
			conn = self.dbpool.GetConnection(tmp['service'])
			if conn is None:
				for src in self.srcs:
					src['conn'].ReleaseConnection()
				raise gmExceptions.ConstructorError, 'cannot connect to service [%s]' % tmp['service']
#			conn.conn.toggleShowQuery
			curs = conn.cursor()
			cmd = "select %s, gmpw_user, gmpw_score from %s limit 1" % (tmp['col'], tmp['table'])
			if not gmPG.run_query(curs, cmd):
				curs.close()
				for src in self.srcs:
					src['conn'].ReleaseConnection()
				raise gmExceptions.ConstructorError, 'cannot access [%s.{%s/gmpw_user/gmpw_score}] in service [%s]' % (tmp['table'], tmp['col'], tmp['service'])
			pk = gmPG.get_pkey_name(curs, tmp['table'])
			curs.close()
			if pk is None:
				tmp['pk'] = "oid"
			else:
				tmp['pk'] = pk
			tmp['conn'] = conn
			tmp['query'] = "select %s, %s from %s where %s" % (tmp['pk'], tmp['col'], tmp['table'], tmp['col'])
			self.srcs.append(tmp)
			_log.Log(gmLog.lData, 'valid match source: %s' % tmp)

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
			cmd = "%s %s %%s limit %s" % (src['query'], search_condition, src['limit'])
			if not gmPG.run_query(curs, cmd, aFragment):
				curs.close()
				_log.Log(gmLog.lErr, 'cannot check for matches in %s' % src)
				return (_false, [])
			matching_rows = curs.fetchall()
			curs.close()
			for row in matching_rows:
				matches.append({'ID': row[0], 'label': row[1]})

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
#============================================================
class cMatchProvider_Date(cMatchProvider):
	def __init__(self, allow_past = None):
		self.__def_text = _('enter date here')
		self.__expanders = []
		self.__display_format = _('%d.%b %Y (%a)')
		self.__allow_past = allow_past
		self.__expanders.append(self.__single_number)
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
		self.__now = mxDT.now()
		print "now:", self.__now
		matches = []
		for expander in self.__expanders:
			items = expander(aFragment)
			if items is not None:
				matches.extend(items)
		if len(matches) > 0:
			return (_true, matches)
		else:
			return (_false, [])
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return None
	#--------------------------------------------------------
	# date fragment expanders
	#--------------------------------------------------------
	def __single_number(self, aFragment):
		if not re.match("^(\s|\t)*\d+(\s|\t)*$", aFragment):
			return None
		val = aFragment.replace(' ', '')
		val = int(val.replace('\t', ''))

		matches = []
		# nth day of this month (if larger than today or past explicitely allowed)
		if (self.__now.day <= val) or (self.__allow_past):
			target_date = self.__now + mxDT.RelativeDateTime(day = val)
			print "target:", target_date, '(that day, this month)'
			tmp = {
				'value': target_date,
				'label': target_date.strftime(self.__display_format),
				'ID': 0
			}
			matches.append(tmp)
		# day of next month
		target_date = self.__now + mxDT.RelativeDateTime(months = 1, day = val)
		print "target:", target_date, '(that day, next month)'
		tmp = {
			'value': target_date,
			'label': target_date.strftime(self.__display_format),
			'ID': 1
		}
		matches.append(tmp)
		# X days from now (if <32)
		if val < 32:
			target_date = self.__now + mxDT.RelativeDateTime(days = val)
			print "target:", target_date, '(that many days from today)'
			tmp = {
				'value': target_date,
				'label': target_date.strftime(self.__display_format),
				'ID': 2
			}
			matches.append(tmp)
		# X weeks from now (if <5)
		if val < 7:
			target_date = self.__now + mxDT.RelativeDateTime(weeks = val)
			print "target:", target_date, '(that many weeks from today)'
			tmp = {
				'value': target_date,
				'label': target_date.strftime(self.__display_format),
				'ID': 3
			}
			matches.append(tmp)
		# day of this week
		# day of next week
		return matches
	#--------------------------------------------------------
	#--------------------------------------------------------
#============================================================
class cWheelTimer(wxTimer):
	"""Timer for delayed fetching of matches.

	It would be quite useful to tune the delay
	according to current network speed either at
	application startup or even during runtime.

	No logging in here as this should be as fast as possible.
	"""
	def __init__(self, aCallback = None, aDelay = 300):
		"""Set up our timer with reasonable defaults.

		- delay default is 300ms as per Richard Terry's experience
		- delay should be tailored to network speed/user speed
		"""
		# sanity check
		if aCallback is None:
			_log.Log(gmLog.lErr, "No use setting up a timer without a callback function.")
			return None
		else:
			self.__callback = aCallback

		self.__delay = aDelay

		wxTimer.__init__(self)
	#--------------------------------------------------------
	def Notify(self):
		self.__callback()
#============================================================
class cPhraseWheel (wxTextCtrl):
	"""Widget for smart guessing of user fields, after Richard Terry's interface."""

	default_phrase_separators = re.compile('[;/|]+')

	def __init__ (self,
					parent,
					id_callback,
					id = -1,
					pos = wxDefaultPosition,
					size = wxDefaultSize,
					aMatchProvider = None,
					aDelay = 300):
		"""
		id_callback holds a reference to another Python function.
		This function is called when the user selects a value.
		This function takes a single parameter -- being the ID of the
		value so selected"""

		if not isinstance(aMatchProvider, cMatchProvider):
			_log.Log(gmLog.lErr, "aMatchProvider must be a match provider object")
			return None
		self.__matcher = aMatchProvider
		self.__currMatches = []
		self.phrase_separators = cPhraseWheel.default_phrase_separators
		self.__timer = cWheelTimer(self._on_timer_fired, aDelay)

		wxTextCtrl.__init__ (self, parent, id, "", pos, size)
		# unnecessary as we are using styles
		#self.SetBackgroundColour (wxColour (200, 100, 100))
		self.parent = parent

		# set event handlers
		# 1) entered text changed
		EVT_TEXT (self, self.GetId(), self.__on_text_update)
		# - user pressed <enter>
		EVT_TEXT_ENTER	(self, self.GetId(), self.__on_enter)
		# 2) a key was pressed
		EVT_KEY_DOWN (self, self.__on_key_pressed)
		# 3) evil user wants to resize widget
		EVT_SIZE (self, self.on_resize)

		self.id_callback = id_callback

		x, y = pos
		width, height = size
		self.__picklist_win = wxWindow (parent, -1, pos = (x, y+height), size = (width, height*6))
		self.panel = wxPanel(self.__picklist_win, -1)
		self.__picklist = wxListBox(self.panel, -1, style=wxLB_SINGLE | wxLB_NEEDED_SB)
		self.__picklist.Clear()
		self.__picklist_win.Hide ()
		self.__picklist_visible = _false

		self.left_part = ''
		self.right_part = ''
	#--------------------------------------------------------
	def __updateMatches(self):
		"""Get the matches for the currently typed input fragment."""

		entire_input = self.GetValue()
#		print "---------------------"
#		print "phrase wheel content:", entire_input
		cursor_pos = self.GetInsertionPoint()
#		print "cursor at position:", cursor_pos
		left_of_cursor = entire_input[:cursor_pos]
		right_of_cursor = entire_input[cursor_pos:]
#		print "cursor in input: %s>>>CURSOR<<<%s" % (left_of_cursor, right_of_cursor)
		# find last phrase separator before cursor position
		left_boundary = self.phrase_separators.search(left_of_cursor)
		if left_boundary is not None:
#			print "left boundary span:", left_boundary.span()
			phrase_start = left_boundary.end()
		else:
			phrase_start = 0
		self.left_part = entire_input[:phrase_start]
#		print "phrase start:", phrase_start
		# find next phrase separator after cursor position
		right_boundary = self.phrase_separators.search(right_of_cursor)
		if right_boundary is not None:
#			print "right boundary span:", right_boundary.span()
			phrase_end = cursor_pos + (right_boundary.start() - 1)
		else:
			phrase_end = len(entire_input) - 1
		self.right_part = entire_input[phrase_end+1:]
#		print "phrase end:", phrase_end

		# get current(ly relevant part of) input
		relevant_input = entire_input[phrase_start:phrase_end+1]
#		print "relevant input:", relevant_input
		# get all currently matching items
		(matched, self.__currMatches) = self.__matcher.getMatches(relevant_input)
		# and refill our picklist with them
		self.__picklist.Clear()
		if matched:
			for item in self.__currMatches:
				self.__picklist.Append(item['label'], clientData = item['ID'])
	#--------------------------------------------------------
	def __show_picklist(self):
		"""Display the pick list."""

		# if only one match and text == match
#		if (len(self.__currMatches) == 1) and (self.__currMatches[0]['label'] == self.GetValue()):
			# don't display drop down list
#			self.__hide_picklist()
#			return 1

		# recalculate position
		# FiXME: check for number of entries - shrink list windows
		#pos = self.ClientToScreen ((0,0))
		#dim = self.GetSize ()
		#self.__picklist_win.Position(pos, (0, dim.height))

		# select first value
		self.__picklist.SetSelection(0)

		# remember that we have a list window
		self.__picklist_visible = _true

		# and show it
		# FIXME: we should _update_ the list window instead of redisplaying it
		self.__picklist_win.Show()
		self.__picklist.Show()
	#--------------------------------------------------------
	def __hide_picklist(self):
		"""Hide the pick list."""
		if self.__picklist_visible:
			self.__picklist_win.Hide()		# dismiss the dropdown list window
		self.__picklist_visible = _false
	#--------------------------------------------------------
	# specific event handlers
	#--------------------------------------------------------
	def OnSelected (self):
		"""Gets called when user selected a list item."""
		self.__hide_picklist()

		n = self.__picklist.GetSelection()		# get selected item
		data = self.__picklist.GetClientData(n)		# get data associated with selected item
		selected_string = self.__picklist.GetString(n)
		self.SetValue('%s%s%s' % (self.left_part, selected_string, self.right_part))

		self.id_callback (data)				# and tell our parent about the user's selection
	#--------------------------------------------------------
	# individual key handlers
	#--------------------------------------------------------
	def __on_enter (self):
		"""Called when the user pressed <ENTER>.

		FIXME: this might be exploitable for some nice statistics ...
		"""
		# if we have a pick list
		if self.__picklist_visible:
			# tell the input field about it
			self.OnSelected()
	#--------------------------------------------------------
	def __on_down_arrow(self, key):
#		import pdb
#		pdb.set_trace ()
		# if we already have a pick list go to next item
		if self.__picklist_visible:
			self.__picklist.ProcessEvent (key)

		# if we don't yet have a pick list
		# - open new pick list
		# (this can happen when we TAB into a field pre-filled
		#  with the top-weighted contextual data but want to
		#  select another contextual item)
		else:
			# don't need timer anymore since user explicitely requested list
			self.__timer.Stop()
			# update matches according to current input
			self.__updateMatches()
			# if we do have matches now show list
			if len(self.__currMatches) > 0:
				self.__show_picklist()
	#--------------------------------------------------------
	def __on_up_arrow(self, key):
		if self.__picklist_visible:
			selected = self.__picklist.GetSelection()
			# select previous item if available
			if selected > 0:
				self.__picklist.SetSelection(selected-1)
			else:
				# FIXME: return to input field and close pick list ?
				pass
		else:
			# FIXME: input history ?
			pass
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def __on_key_pressed (self, key):
		"""Is called when a key is pressed."""
		# user moved down
		if key.GetKeyCode() == WXK_DOWN:
			self.__on_down_arrow(key)
			return
		# user moved up
		if key.GetKeyCode() == WXK_UP:
			self.__on_up_arrow(key)
			return
		# FIXME: need PAGE UP/DOWN//POS1/END here

		# user pressed <ENTER>
		if key.GetKeyCode() == WXK_RETURN:
			self.__on_enter()
			return

		key.Skip()
	#--------------------------------------------------------
	def __on_text_update (self, event):
		"""Internal handler for EVT_TEXT (called when text has changed)"""

		# if empty string then kill list dropdown window
		# we also don't need a timer event then
		if len(self.GetValue()) == 0:
			self.__hide_picklist()
			# and kill timer lest there be a zombie of it running
			self.__timer.Stop()
		else:
			# start timer for delayed match retrieval
			self.__timer.Start(oneShot = _true)
	#--------------------------------------------------------
	def on_resize (self, event):
		sz = self.GetSize()
		rows = len (self.__currMatches)
		if rows == 0:
			rows = 1
		if rows > 10:
			rows = 10
		self.__picklist.SetSize ((sz.width, sz.height*rows))
		# as wide as the textctrl, and 6 times the height
		self.panel.SetSize (self.__picklist.GetSize ())
		self.__picklist_win.SetSize (self.panel.GetSize())
	#--------------------------------------------------------
	def _on_timer_fired (self):
		"""Callback for delayed match retrieval timer.

		if we end up here:
		 - delay has passed without user input
		 - the value in the input field has not changed since the timer started
		"""
		# update matches according to current input
		self.__updateMatches()
		# we now have either:
		# - all possible items (within reasonable limits) if input was '*'
		# - all matching items
		# - an empty match list if no matches were found
		# also, our picklist is refilled and sorted according to weight

		# display list - but only if we have more than one match
		if len(self.__currMatches) > 0:
			# show it
			self.on_resize (None)
			self.__show_picklist()
		else:
			# we may have had a pick list window so we
			# need to dismiss that since we don't have
			# more than one item anymore
			self.__hide_picklist()
#--------------------------------------------------------
# MAIN
#--------------------------------------------------------
if __name__ == '__main__':
	import gmI18N
	#----------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wxApp):
		def OnInit (self):

			frame = wxFrame (
				None,
				-4,
				"phrase wheel test for GNUmed",
				size=wxSize(300, 350),
				style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE
			)

			items = [	{'ID':1, 'label':"Bloggs", 	'weight':5},
						{'ID':2, 'label':"Baker",  	'weight':4},
						{'ID':3, 'label':"Jones",  	'weight':3},
						{'ID':4, 'label':"Judson", 	'weight':2},
						{'ID':5, 'label':"Jacobs", 	'weight':1},
						{'ID':6, 'label':"Judson-Jacobs",'weight':5}
					]
			mp1 = cMatchProvider_FixedList(items)
			ww1 = cPhraseWheel(frame, clicked, pos = (50, 50), size = (180, 30), aMatchProvider=mp1)
			ww1.on_resize (None)

			mp3 = cMatchProvider_Date(allow_past = 0)
			ww3 = cPhraseWheel(frame, clicked, pos = (50, 150), size = (180, 30), aMatchProvider=mp3)
			ww3.on_resize(None)

			print "Do you want to test the database connected phrase wheel ?"
			yes_no = raw_input('y/n: ')
			if yes_no == 'y':
				src = {
					'service': 'default',
					'table': 'gmpw_sql_test',
					'column': 'phrase',
					'limit': 25
				}
				mp2 = cMatchProvider_SQL([src])
				ww2 = cPhraseWheel(frame, clicked, pos = (50, 250), size = (180, 30), aMatchProvider=mp2)
				ww2.on_resize (None)

			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()

#==================================================
# $Log: gmPhraseWheel.py,v $
# Revision 1.13  2003-09-29 00:16:55  ncq
# - added date match provider
#
# Revision 1.12  2003/09/21 10:55:04  ncq
# - coalesce merge conflicts due to optional SQL phrase wheel testing
#
# Revision 1.11  2003/09/21 07:52:57  ihaywood
# those bloody umlauts killed by python interpreter!
#
# Revision 1.10  2003/09/17 05:54:32  ihaywood
# phrasewheel box size now approximate to length of search results
#
# Revision 1.8  2003/09/16 22:25:45  ncq
# - cleanup
# - added first draft of single-column-per-table SQL match provider
# - added module test for SQL matcher
#
# Revision 1.7  2003/09/15 16:05:30  ncq
# - allow several phrases to be typed in and only try to match
#   the one the cursor is in at the moment
#
# Revision 1.6  2003/09/13 17:46:29  ncq
# - pattern match word separators
# - pattern match ignore characters as per Richard's suggestion
# - start work on phrase separator pattern matching with extraction of
#   relevant input part (where the cursor is at currently)
#
# Revision 1.5  2003/09/10 01:50:25  ncq
# - cleanup
#
#
#==================================================

#----------------------------------------------------------
# ideas
#----------------------------------------------------------
#- display possible completion but highlighted for deletion
#(- cycle through possible completions)
#- pre-fill selection with SELECT ... LIMIT 25
#- weighing by incrementing counter - if rollover, reset all counters to percentage of self.value()
#- ageing of item weight
#- async threads for match retrieval instead of timer
#  - on truncated results return item "..." -> selection forcefully retrieves all matches

#- plugin for pattern matching/validation of input

#- generators/yield()
#- OnChar() - process a char event

# split input into words and match components against known phrases
# -> accumulate weights into total item weight

# - case insensitive by default but
# - make case sensitive matching possible
#   - if no matches found revert to case _insensitive_ matching
# - maybe _sensitive_ by default + auto-revert if too few matches ?

# make special list window:
# - deletion of items
# - highlight matched parts
# - faster scrolling
# - wxEditableListBox ?

# - press down only once to get into list
# - moving between list members is too slow

# - if non-learning (i.e. fast select only): autocomplete with match
#   and move cursor to end of match
#-----------------------------------------------------------------------------------------------
# darn ! this clever hack won't work since we may have crossed a search location threshold
#----
#	#self.__prevFragment = "XXXXXXXXXXXXXXXXXX-very-unlikely--------------XXXXXXXXXXXXXXX"
#	#self.__prevMatches = []		# a list of tuples (ID, listbox name, weight)
#
#	# is the current fragment just a longer version of the previous fragment ?
#	if string.find(aFragment, self.__prevFragment) == 0:
#	    # we then need to search in the previous matches only
#	    for prevMatch in self.__prevMatches:
#		if string.find(prevMatch[1], aFragment) == 0:
#		    matches.append(prevMatch)
#	    # remember current matches
#	    self.__prefMatches = matches
#	    # no matches found
#	    if len(matches) == 0:
#		return [(1,_('*no matching items found*'),1)]
#	    else:
#		return matches
#----
#TODO:
# - see spincontrol for list box handling
# stop list (list of negatives): "an" -> "animal" but not "and"

# maybe store fixed list matches as balanced tree if otherwise to slow
#-----
#> > remember, you should be searching on  either weighted data, or in some
#> > situations a start string search on indexed data
#>
#> Can you be a bit more specific on this ?

#seaching ones own previous text entered  would usually be instring but
#weighted (ie the phrases you use the most auto filter to the top)

#Searching a drug database for a   drug brand name is usually more
#functional if it does a start string search, not an instring search which is
#much slower and usually unecesary.  There are many other examples but trust
#me one needs both
#-----
