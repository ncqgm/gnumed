"""
A class, extending wxTextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
#@copyright: GPL

############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmTestTableMatcher.py,v $
# $Id: gmTestTableMatcher.py,v 1.1 2003-09-15 14:56:10 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood"

import string, types, time, sys, re

if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog

from gmPhraseWheel import *
from wxPython.wx import *
import pgdb
import traceback

_true = (1==1)
_false = (1==0)
#------------------------------------------------------------
# usable instances
#------------------------------------------------------------
class SingleTableMatchProvider(cMatchProvider):
	"""match provider which looks in all the text fields , or a given set of text fields
	"""
	def __init__(self, table, searchable_fields= [],  connect_str=":template1", limit = 50):
		""" table - the name of the table to search
		    searchable_fields - restrict the searchable fields to these fields, otherwise
		    			use varchar fields.
		    connect_str - connection string
		    limit - the limit of fields  to fetch 
					
		"""
		self.limit = limit


		self.connection = pgdb.connect(connect_str)

		try:
			self.connection.rollback()
			cursor = self.connection.cursor()
			cursor.execute("select * from %s" % table)
		except:
			traceback.print_tb(sys.exc_info()[2])
			print "table must be the name for a  public schema table"
			return None
		
		self.table = table

		self.find_matchable_fields(cursor, searchable_fields)

		cursor.close()
		cMatchProvider.__init__(self)

		

	def find_matchable_fields(self, cursor, fields):
		self.fieldPosition = {}
		pos = -1
		for x in  cursor.description:
			pos += 1
			if x[0] in fields or ( fields ==[] and  x[1] == "varchar"):
				self.fieldPosition[x[0]] = pos
				continue
			if x[0] == "id":
				self.idPos = pos
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
		# look for matches

		return self.findMatchListForSearchableTextFields("select * from %s where lower(%s) like '%s%%'" , aFragment)

	def findMatchListForSearchableTextFields( self, search_str, aFragment):
		self.connection.rollback()
		cursor = self.connection.cursor()
		self.matches = []
		for field in self.fieldPosition.keys():
			self.addToMatchListFromSelect(cursor,search_str , field, aFragment)
		# no matches found
		if len(self.matches) == 0:
			return (_false, [])

		self.matches.sort(self.__cmp_items)
		return (_true, self.matches)
	#--------------------------------------------------------


	def addToMatchListFromSelect( self,cursor, search_str,  field, aFragment):
		cursor.execute(search_str % (self.table, field, aFragment) )
		selected_tuples = cursor.fetchmany(self.limit)
		for x in selected_tuples:
			self.matches.append({'label': self.getConcatenationOfRowTextFields( x) , 'ID': x[self.idPos]} )
		

	
	def	getConcatenationOfRowTextFields(self, tuple):
		concat = []
		for field in self.fieldPosition.keys():
			pos = self.fieldPosition[field]
			concat.append( tuple[pos] )
		return "; ".join(concat)


	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.findMatchListForSearchableTextFields("select * from %s where lower(%s) like '%% %s%%'" , aFragment)
		
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.findMatchListForSearchableTextFields("select * from %s where lower(%s) like '%%%s%%'" , aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return self.getMatchesBySubstr(self, aFragment)
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
