
from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin
from pyPgSQL import PgSQL
import re
import sys
from traceback import *
import time

class TestListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=0):
        wxListCtrl.__init__(self, parent, ID, pos, size, style)
        wxListCtrlAutoWidthMixin.__init__(self)



class BrowseSizer(wxBoxSizer):
	
	def __init__(self, parent, columnList):
		wxBoxSizer.__init__(self,wxHORIZONTAL)
		self.ctrl = BrowseListCtrl( parent, columnList)
		self.Add( self.ctrl)
		self.ctrl.SetAutoLayout(1)

	

class BrowseListCtrl( TestListCtrl):		
	def __init__( self, parent, id = -1,  columnList =[  { 'name':'date' , 'width': 80 }, { 'name':'description', 'width': 150 }, { 'name': 'value' , 'width' : 80 } ] ):
		TestListCtrl.__init__(self, parent, id, wxDefaultPosition, size = wxSize(800,400), style = wxLC_REPORT | wxSUNKEN_BORDER | wxLC_VRULES )#| wxLC_HRULES)
		self._test()
		self._configureEvents()


	def _configureEvents(self):
		EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self._listItemActivated)
		self.notifyList = []
		self.notifyList.append(self._dummyNotify)
		

	def _listItemActivated(self,  event):
		#row =  self.rows[ event.GetIndex()]
		for func in self.notifyList:
			func(event)
	

	def _dummyNotify(self, row):
		print row

		
	def _setColumns( self, columnList):
		col = 0
		self.columnList = columnList
		for x in columnList:
			print "_setColumn with ", x
			item = wxListItem()
			item.SetText(x['name'])
			item.SetWidth(x['width'])
			item.SetColumn(col)
			#item.SetMask( wxLIST_MASK_TEXT | wxLIST_MASK_FORMAT | wxLIST_MASK_STATE | wxLIST_MASK_DATA) 
			#self.ctrl.InsertColumnInfo( col, item)
			print col, item.GetText(), item.GetWidth()
			self.InsertColumn(col, item.GetText(), width = item.GetWidth() )
			self.SetColumn(col, item)
			col += 1
	
	def _setData( self, description , rows):
		"""data is in dbapi format, of list of tuples. Order assumed to be same as columnList used to init control"""
		map = {}
		self.rows = rows
		self.description = description
		# for the indices of description:
		for x in xrange(0, len(description)):
			#set a map with indexes as keys, and indexes and table column description as a 2-tuple entry.
			map[description[x][0]] = (x, description[x])
		
		self.descriptionMap = map

		row = 0
		for t in rows:
			self._setRow(  map ,  t, row)
			row += 1

	def getDescription(self):
		return self.description

	def getRow(self, index):
		return self.rows[index]


	def _setRow(self, descriptionMap,  tuple, row):
		print "tuple data = ", tuple	
		item = wxListItem()
		for col in xrange(0,self.GetColumnCount()):
			name = self.columnList[col]['name'] 
			(pos, rowDescription) = descriptionMap.get( name, (None, None) )
			if pos == None:
				text = ""
			else:
				if tuple[pos] == None:
					text = ""
				else:	
					text = str(tuple[pos])
				
					
			if col == 0:
				self.InsertStringItem(row, text )
			else:
				self.SetStringItem(row, col, text )

			

			
	def convertColList(self, list):
		list2 = []
		for ( name, width ) in list:
			list2.append( { 'name': name.split('.')[-1], 'width': width } )
		return list2	


	def update(self,columnList, cursor, limit = 100):
		"""update the list using columnList of form [ {'name':'xx', 'width': w }, ...], 
		and dbapi compliant cursor , showing up to limit rows """
		
		self.ClearAll()
		self._setColumns(columnList)
		rows = cursor.fetchmany(limit)
		description = cursor.description
		self._setData( description, rows)
		
	def addListSelectionListener( self, func):
		"""func will be notified with a list selection event"""
		#the selected row ( as in dbapi fetchone()) """
		self.notifyList.append(func)

		
	def _test(self, dbapi = PgSQL, connectStr = "localhost::gnumed2"):	
		statement = "create view drug_all as select d.id, d.name, g.name as generic_name, c.description from drug d, generic g, drug_classes c where d.id_generic = g.id and d.id_drug_classes = c.id" 
	
		conn = dbapi.connect( connectStr)
		
		cu = conn.cursor()
		try:
			cu.execute(statement)
			conn.commit()
		except:
			print sys.exc_info()[2]
			pass
		cu = conn.cursor()
		cu.execute("select * from drug_all")
		self.update( [{ "name": "name" , "width":200 }, {"name":"generic_name" , "width":150 }, {"name":"description" , "width" : 300 } ], cu)
		

if __name__ == '__main__':

	 app = wxPyWidgetTester( size=(500, 200) )
	 app.SetWidget( BrowseListCtrl, -1)
	 app.MainLoop()

	
	
