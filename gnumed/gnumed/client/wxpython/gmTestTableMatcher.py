"""
A class, extending wxTextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
#@copyright: GPL

############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmTestTableMatcher.py,v $
# $Id: gmTestTableMatcher.py,v 1.2 2003-09-15 18:38:04 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood"

import string, types, time, sys, re

if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog

from gmPhraseWheel import *
from wxPython.wx import *
#import pgdb
import gmPG, gmExceptions
import traceback

_true = (1==1)
_false = (1==0)
#------------------------------------------------------------
# usable instances
#------------------------------------------------------------
class SingleTableMatchProvider(cMatchProvider):
	"""match provider which looks in all the text fields , or a given set of text fields
	"""
	def __init__(self, table, searchable_fields= [],  connect_str=":template1", limit = 50, aService = 'default'):
		""" table - the name of the table to search
		    searchable_fields - restrict the searchable fields to these fields, otherwise
		    			use varchar fields.
		    connect_str - connection string
		    limit - the limit of fields  to fetch 
					
		"""
		self.limit = limit

#		self.connection = pgdb.connect(connect_str)
		self.dbpool = gmPG.ConnectionPool()
		self.connection = self.dbpool.GetConnection(aService)
		self.connection.conn.toggleShowQuery

		# why ?
#		self.connection.rollback()
		cursor = self.connection.cursor()
		cmd = "select * from %s limit 1" % table
		if not gmPG.run_query(cursor, cmd):
			cursor.close()
			self.connection.ReleaseConnection()
			print "table must be the name for a  public schema table"
			raise gmExceptions.ConstructorError, "invalid source table name"

		self.table = table
		print "table:", table
		self.find_matchable_fields(cursor, searchable_fields)
		print "searchable fields:", searchable_fields

		cursor.close()
		cMatchProvider.__init__(self)


	def find_matchable_fields(self, cursor, fields):
		cmd = "select * from %s limit 1" % self.table
		print cmd
		if not gmPG.run_query(cursor, cmd):
			return
		# FIXME: why not use column names ?
		self.fieldPosition = {}
		self.idPos = None
		pos = -1
		for x in cursor.description:
			print x
			pos += 1
			if x[0] in fields or (fields == [] and x[1] == "varchar"):
				self.fieldPosition[x[0]] = pos
				continue
			# FIXME: make this reference the PK of the table
			if x[0] == "id":
				self.idPos = pos
		print "varchar fields:", self.fieldPosition
		print "PKEY field:", self.idPos
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
		print "condition:", condition
		print "fragment:", fragment
#		fragments = {'frag': aFragment}
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		condition = "~*"
		fragment = "(\s%s)|(^%s)" % (aFragment, aFragment)
		print "condition:", condition
		print "fragment:", fragment
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		condition = "ilike"
		fragment = "%%%s%%" % aFragment
		print "condition:", condition
		print "fragment:", fragment
#		fragments = {'frag': aFragment}
		return self.findMatchListForSearchableTextFields(condition, fragment)
	#--------------------------------------------------------
	def findMatchListForSearchableTextFields(self, search_condition, aFragment):
		self.matches = []
		cursor = self.connection.cursor()
		for field in self.fieldPosition.keys():
			cmd = "select * from %s where %s %s %%s limit %s" % (self.table, field, search_condition, self.limit)
			print "running", cmd, "with data", aFragment
			self.addToMatchListFromSelect(cursor, cmd, aFragment)
			print "current matches:", self.matches
		cursor.close()

		# no matches found
		if len(self.matches) == 0:
			return (_false, [])

		self.matches.sort(self.__cmp_items)
		return (_true, self.matches)
	#--------------------------------------------------------
	def addToMatchListFromSelect(self, cursor, search_cmd, aFragment):
		if not gmPG.run_query(cursor, search_cmd, aFragment):
			_log.Log(gmLog.lErr, 'cannot look for matches')
			return None

		selected_tuples = cursor.fetchall()
		print selected_tuples
		for x in selected_tuples:
			self.matches.append({'label': self.getConcatenationOfRowTextFields( x) , 'ID': x[self.idPos]} )
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
		return (_true, matches)
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
