#!/usr/bin/python
#############################################################################
#
# gmSQLListControl - a wx list control that hanldles SQL queries automatically
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG, gmLoginInfo
# @change log:
#	02.07.2001 hherb first draft, untested
#	03.11.2001 hherb adapted to distributed server paradigm
#
# @TODO: testing & writing the module test function
#	 a context menu (right click) for most common actions (like delete row)
############################################################################

import sys, time
from wxPython.wx import *
import gmPG, gmLabels

class SQLListControl(wxListCtrl):
	"Intelligent list control able to display SQL query results in a formatted way"

	__querystr = ''
	__service = None
	__status = None
	__saved_stdout = None
	__saved_stderr = None
	__stdout = None
	__stderr = None
	__feedback = true
	__labels = []
	__maxfetch = 0



	def __init__(self, parent, id, pos=wxPyDefaultPosition, size=wxPyDefaultSize, style=wxLC_REPORT, feedback=true):
		wxListCtrl.__init__(self, parent, id, pos, size, style)
		self.__feedback = feedback
		EVT_LIST_ITEM_SELECTED(self, -1 , self.OnItemSelected)


	def SetMaxfetch(self, n):
		self.__maxfetch = maxfetch


	def GetMaxFetch(self):
		return self.__maxfetch


	def SetQueryStr(self, querystr, service = 'default'):
		print "setting query string to " , querystr
		self.__querystr = querystr
		self.__service = service


	def GetQueryStr(self):
		return self.__querystr



	def SetLabels(self, labels):
		self.__labels = labels
		gmLabels.LabelListControl(self, self.__labels)


	def GetLabels(self):
		return self.__labels



	def SetRedirectedOutput(self, stderr, stdout=None):
		self.__saved_stdout = sys.stdout
		self.__saved_stderr = sys.stderr
		self.__stderr = stderr
		if stdout is not None:
			self.__feedback = true
			self.__stdout = stdout



	def RedirectOutput(self):
		try:
			if self.__stderr is not None:
				sys.stderr = self.__stderr
		except:
			print "can't redirect stderr"
		try:
			if self.__stdout is not None:
				sys.stdout = self.__stdout
		except:
			print "can't redirect stdout"



	def RestoreOutput(self):
		if self.__saved_stderr is not None:
			sys.stderr = self.__saved_stderr
		if self.__saved_stdout is not None:
			sys.stdout = self.__saved_stdout



	def SetStatusFunc(self, statusfunc):
		self.__status = statusfunc



	def __SetStatusText(self, txt):
		if self.__status is not None:
			self.__status(txt)



	def RunQuery(self):
		if self.__querystr is None or self.__querystr == '':
			print "no need to process an empty query"
			return
		self.RedirectOutput()
		try:
			print "running query on service ", self.__service
			conn = gmPG.ConnectionPool().GetConnection(self.__service)
			cursor = conn.cursor ()
		except:
			print "Exception thrown when trying to connect to backend in RunQuery()"
			self.RestoreOutput()
			return

		#clear results from previous query
		self.ClearAll()
		#time needed for database AND gui handling
        	t1f = time.time()
        	#time needed for database query
        	t1 = time.time()

		cursor = conn.cursor()
		cursor.execute(self.__querystr)
		if self.__maxfetch > 0:
			queryresult = cursor.fetchmany(self.__maxfetch)
		else:
			queryresult = cursor.fetchall()

		t2 = time.time()
		if self.__feedback:
			print "Query [%s] returned %d tuples in %3.3f sec\n\n" % (self.__querystr, cursor.rowcount, t2-t1)

		#set list control labels depending on the returned fields, unless manually overridden

		if len(self.__labels)<=0:
			self.__labels = gmPG.fieldNames(cursor)

		gmLabels.LabelListControl(self, self.__labels)
		rowcount=0
		for row in queryresult:
			colcount = 0
			for attr in row:
				if colcount==0:
					self.InsertStringItem(rowcount,str(attr))
				else:
					self.SetStringItem(rowcount,colcount, str(attr))            
                		colcount +=1
            		rowcount +=1

		#adjust column width according to the query results
		
		for w in range(0, len(self.__labels)):
			self.SetColumnWidth(w, wxLIST_AUTOSIZE)

		t2f = time.time()
		self.__SetStatusText("%d records found; retrieved and displayed in %1.3f sec." % (cursor.rowcount, t2f-t1f))
	
	

		#restore standard output
		self.RestoreOutput()

#--------------- changed 21/3/2002
#store the queryresult for later retrieval
		self.queryresult = queryresult

	def update(self):
		self.RunQuery()


	def GetRow(self, index):
		try:
			return self.queryresult[index]
		except Exception, errorStr:
			print Exception, errorStr
		
		return ''

	def GetSelectedIndex(self):
		return self.sel_index						

	def GetSelectedRow(self):
		return self.GetRow( self.GetSelectedIndex())

	def OnItemSelected(self, event):
		self.sel_index = event.m_itemIndex	
		
if __name__ == "__main__":
	print "test function needs to be written! Please do it."
