"""
A class, extending wxTextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
#@copyright: GPL

############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/Attic/gmTestTableMatcher.py,v $
# $Id: gmTestTableMatcher.py,v 1.1 2003-09-18 12:05:42 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan"

import string, types, time, sys, re

if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog

from gmPhraseWheel import *
import gmPG, gmExceptions

from wxPython.wx import *

_true = (1==1)
_false = (1==0)
#------------------------------------------------------------
# usable instances
#------------------------------------------------------------
class SingleTableMatchProvider(cMatchProvider):
	"""match provider which looks in all the text fields , or a given set of text fields
	"""
	def __init__(self, table, searchable_fields = None, limit = 50, aService = 'default'):
		""" table - the name of the table to search
		    searchable_fields - restrict the searchable fields to these fields, otherwise
		    			use all varchar fields.
		    limit - the limit of fields  to fetch 
		"""
		self.limit = limit

		self.dbpool = gmPG.ConnectionPool()
		self.connection = self.dbpool.GetConnection(aService)
		self.connection.conn.toggleShowQuery

		# sanity check
		cursor = self.connection.cursor()
		cmd = "select 1 from %s limit 1" % table
		if not gmPG.run_query(cursor, cmd):
			cursor.close()
			self.connection.ReleaseConnection()
			_log.Log(gmLog.lErr, 'cannot access table [%s] for matching' % table)
			raise gmExceptions.ConstructorError, 'cannot access table [%s] for matching' % table

		self.table = table
		self._find_matchable_fields(cursor, searchable_fields)
		_log.Log(gmLog.lData, 'matching against %s => %s' % (self.table, self.fieldPosition.keys()))

		cursor.close()
		cMatchProvider.__init__(self)
	#--------------------------------------------------------
	def _find_matchable_fields(self, cursor, fields = None):
		pk_name = gmPG.get_pkey_name(cursor, self.table)
		cmd = "select * from %s limit 1" % self.table
		if not gmPG.run_query(cursor, cmd):
			return
		# FIXME: why not use column names in the query directly ?
		self.fieldPosition = {}
		self.PK_pos = None
		pos = -1
		for col_desc in cursor.description:
			print col_desc
			print col_desc[1]
			print type(col_desc[1])
			pos += 1
			if col_desc[0] in fields or ((fields is None) and (str(col_desc[1]) in ["varchar", "text"])):
				self.fieldPosition[col_desc[0]] = pos
				continue
			if col_desc[0] == pk_name:
				self.PK_pos = pos
		
		print "varchar/text fields:", self.fieldPosition.keys()
		print "PKEY field:", self.PK_pos
		return

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
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		condition = "~*"
		fragment = "( %s)|(^%s)" % (aFragment, aFragment)
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		condition = "ilike"
		fragment = "%%%s%%" % aFragment
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def findMatchListForSearchableTextFields(self, search_condition, aFragment):
		print "condition:", search_condition
		print "fragment:", aFragment
		self.matches = []
		cursor = self.connection.cursor()
		for field in self.fieldPosition.keys():
			cmd = "select * from %s where %s %s %%s limit %s" % (self.table, field, search_condition, self.limit)
			if not gmPG.run_query(cursor, cmd, aFragment):
				_log.Log(gmLog.lErr, 'cannot check for matches')
				return (_false, [])
			matching_rows = cursor.fetchall()
			for row in matching_rows:
				self.matches.append({'label': self.getConcatenationOfRowTextFields(row) , 'ID': row[self.PK_pos]})
		cursor.close()

		# no matches found
		if len(self.matches) == 0:
			return (_false, [])

		self.matches.sort(self.__cmp_items)
		return (_true, self.matches)
	#--------------------------------------------------------
	def	getConcatenationOfRowTextFields(self, tuple):
		concat = []
		for field in self.fieldPosition.keys():
			pos = self.fieldPosition[field]
			concat.append( tuple[pos] )
		return "; ".join(concat)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return self.getMatchesBySubstr(self, '')
	#--------------------------------------------------------
	def __cmp_items(self, item1, item2):
		"""naive ordering"""
		if item1 < item2:
			return -1
		if item1 == item2:
			return 0
		return 1
#--------------------------------------------------------
# MAIN
#--------------------------------------------------------

	
if __name__ == '__main__':
	print """ can execute with optional  arguments:

			table  displayablefield1 displayablfield2  ... 

	 	to display a table with/without a restriction on the displayable fields"""
	if (len(sys.argv) > 1):
		table = sys.argv[1]
	else:
		table = "disease_code"
	
	searchable_fields = []
	if (len(sys.argv) > 2):
		for x in range( 2, len(sys.argv) ):
			searchable_fields.append( sys.argv[x] )

	import gmI18N
	#----------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wxApp):
		def OnInit (self):
					
			mp = SingleTableMatchProvider(table, searchable_fields)

			frame = wxFrame (None, -4, "phrase wheel test for GNUmed", size=wxSize(300, 350), style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)

			# actually, aDelay of 300ms is also the built-in default
			ww = cPhraseWheel(frame, clicked, pos = (50, 50), size = (180, 30), aMatchProvider=mp)
			ww.on_resize (None)
			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()
