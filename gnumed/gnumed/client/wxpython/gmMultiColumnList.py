try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx
	from wxPython import grid

EXTRA_ROW_SPACE = 40

class MultiColumnList( wx.Grid):
	def __init__(self, parent, id = -1):
		wx.Grid.__init__(self, parent, id)
		self.CreateGrid( 10, 1)
		self.SetData( { 1: "2000 AMI",  2 : "2000 Stroke", 3 : "1987 Asthma", 4 : "2002 Thin bones", 5 : "2002 cough" } , 4)

		wx.EVT_SIZE( self, self._resizeData)

		self.EnableEditing(0)
		wx.EVT_GRID_CELL_LEFT_DCLICK( self, self._cellDoubleClicked)
		self.listeners = []
		
	
	def _cellDoubleClicked( self, event):
		event.Skip()
		x, y =  self.GetGridCursorRow(), self.GetGridCursorCol()
		items = self.data.items()
		ix = y * self.col_rows[1] + x
		if ix < len(items):
			self.selData = items[ix]
			self._notifyObservers()
	
	def addItemListener(self, listener):
		if listener not in self.listeners:
			self.listeners.append(listener)

	def removeItemListener(self, listener):		
		if listener in self.listeners:
			self.listeners.remove(listener)

	def _notifyObservers(self):
		for l in self.listeners:
			l( { 'source':self, 'item': self.selData } )
			
		
		

	def _resizeData(self, event):
		event.Skip()
		self.SetData( self.GetData() , fitClientSize = 1)
	
	def _getLongestItem(self, list):
		l = 0
		item = 'AAAAAAAAAAAA    ' 
		for x in list:
			if len(x) > l:
				l = len(x)
				item = x
		return  item		

	def _ensureStringList(self, list):
		alist = []
		for x in list:
			if type(x) == type(''):
				alist.append(x)
			if type(x) in (type( () ), type( [] ) ):
				l = []
				for f in x:
					l.append(str(f))
					
				alist.append("  ".join(l) )
		return alist		

	def _getPredictedRows(self, items):
		(w,h) = self.GetClientSize()
		predictedRows = h/ (self.GetRowSize(0) + 1)  
		if predictedRows == 0: 
			predictedRows = 4
		predictedCols = len(items) / predictedRows
		list = []
		for id , v in items:
			list.append(v)
		(x,y ) = self.GetTextExtent(self._getLongestItem(self._ensureStringList(list) ))
		maxCols = w / (x + EXTRA_ROW_SPACE)
		if maxCols == 0:
			maxCols = 1
		if predictedCols >= maxCols:
			predictedCols = maxCols 
			predictedRows = len(items) / predictedCols + 1
			
		return predictedRows

	def SetData(self, map, maxRows = 8, fitClientSize = 0):
		self.SetDataItems( map.items(), maxRows, fitClientSize) 


	def SetDataItems( self, items,  maxRows = 8 , fitClientSize = 0):

		self.GetTable().SetValue(0,0, 'AAAAAAAAAAAAAAAA')
		if len(items) == 0:
			items = [ [ 0, [""] ] ]
		if fitClientSize :
			predictedRows = self._getPredictedRows(items)
		else:
			predictedRows = maxRows
			
		self.ClearGrid()
		rows = []
		cols = []
	
	
		seqTypes = ( type([]), type( () ) )

		
		for k,v in items:
			if type(v) in seqTypes:
				v = "   ".join(v)

			rows.append( (k,v) )
			if len(rows) >= maxRows or ( fitClientSize and   (len(rows) ) >= predictedRows ):
				cols.append(rows)
				rows = []
		
		if rows <> []:
			cols.append(rows)
		
		table = self.GetTable()
		
		self.BeginBatch()
		table.DeleteCols( 0, table.GetNumberCols())	
		#table.DeleteRows( 1, table.GetNumberRows() )	
		table.AppendCols( len(cols))
		r = len(cols[0]) - table.GetNumberRows()
		if r < 0:
			table.DeleteRows(0, -r)
		else:
			table.AppendRows(r)
		y , x = 0, 0
		for c in cols:
			y = 0
			for r in c:
				table.SetValue(y, x,  str(r[1]) )
				y += 1
			x += 1	
		self.AutoSizeColumns()
		self.AutoSizeRows()
		self.SetRowLabelSize( 1)
		self.SetColLabelSize(1)
		self.EndBatch()
		self.col_rows = ( len(cols), predictedRows)	

		map = {}
		for id, m in items:
			map[id] = m
		self.data = map
		
	def GetData(self):
		return self.data
		



			
	

if __name__ == "__main__":
	 app = wxPyWidgetTester(size = (400, 100))
         app.SetWidget(MultiColumnList, -1)
	 app.MainLoop()
