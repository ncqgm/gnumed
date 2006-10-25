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

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog


def LabelListControl(listctrl, labellist):
    """Set the labels of a list box control

    listctrl: a wx.ListCtrl
    labellist: a list of strings
    """
    for i in range(len(labellist)):
        listctrl.InsertColumn(i, labellist[i])
    #listctrl.SetSingleStyle(wx.LC_VRULES)
    #listctrl.SetSingleStyle(wx.LC_HRULES)


class SQLListControl(wx.ListCtrl):
	"Intelligent list control able to display SQL query results in a formatted way"

	__querystr = ''
	__service = 'default'
	__status = None
	__saved_stdout = None
	__saved_stderr = None
	__stdout = None
	__stderr = None
	__feedback = True
	__labels = []
	__maxfetch = 0



	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_REPORT, feedback=True, hideid=False):
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		self.__feedback = feedback
		self.__hide_id=hideid # first column is assumed to be id field


	def SetMaxfetch(self, n):
		self.__maxfetch = maxfetch


	def GetMaxFetch(self):
		return self.__maxfetch


	def SetQueryStr(self, querystr, service = 'default'):
		self.__querystr = querystr
		self.__service = service


	def GetQueryStr(self):
		return self.__querystr



	def SetLabels(self, labels):
		self.__labels = labels
		LabelListControl(self, self.__labels)


	def GetLabels(self):
		return self.__labels



	def SetRedirectedOutput(self, stderr, stdout=None):
		self.__saved_stdout = sys.stdout
		self.__saved_stderr = sys.stderr
		self.__stderr = stderr
		if stdout is not None:
			self.__feedback = True
			self.__stdout = stdout



	def RedirectOutput(self):
		try:
			if self.__stderr is not None:
				sys.stderr = self.__stderr
		except:
			_log.Log (gmLog.lData,  "can't redirect stderr")
		try:
			if self.__stdout is not None:
				sys.stdout = self.__stdout
		except:
			_log.Log (gmLog.lData,  "can't redirect stdout")



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
			#no need to process an empty query
			return
		self.RedirectOutput()
		_log.Log (gmLog.lData,  "running query on service %s" % self.__service, gmLog.lCooked)
		try:	
#			conn = gmPG.ConnectionPool().GetConnection(self.__service)
			cursor = conn.cursor ()
		except:
			_log.LogException("Cannot connect to backend.", sys.exc_info(), verbose=0)
			self.RestoreOutput()
			return

		#clear results from previous query
		self.ClearAll()
		#workaround for mysterious wxGTK bug
		wx.Yield()
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
			_log.Log (gmLog.lData,  "Query [%s] returned %d tuples in %3.3f sec\n\n" % (self.__querystr, cursor.rowcount, t2-t1))

		#set list control labels depending on the returned fields, unless manually overridden

		if len(self.__labels)<=0:
			self.__labels = gmPG.fieldNames(cursor)
			if self.__hide_id:
				del self.__labels[0]

		LabelListControl(self, self.__labels)
		rowcount=0
		for row in queryresult:
			colcount = 0
			if self.__hide_id:
				id = row[0]
				row = row[1:] # dont print ID column
			for attr in row:
				if colcount==0:
					item = self.InsertStringItem(rowcount,str(attr))
				else:
					self.SetStringItem(rowcount,colcount, str(attr))
                		colcount +=1
			if self.__hide_id:
				self.SetItemData (item, id)
            		rowcount +=1

		#adjust column width according to the query results
		for w in range(0, len(self.__labels)):
			self.SetColumnWidth(w, wx.LIST_AUTOSIZE)

		t2f = time.time()
		self.__SetStatusText("%d records found; retrieved and displayed in %1.3f sec." % (cursor.rowcount, t2f-t1f))

		#restore standard output
		self.RestoreOutput()

if __name__ == "__main__":
	print "test function needs to be written! Please do it."
	print "make sure you can import gmLog !!"
