

from wxPython.wx import *

from wxPython.grid import *

EXTRA_ROW_SPACE = 40

class MultiColumnList( wxGrid):
	def __init__(self, parent, id = -1):
		wxGrid.__init__(self, parent, id)
		self.CreateGrid( 10, 1)
		self.SetData( { 1: "2000 AMI",  2 : "2000 Stroke", 3 : "1987 Asthma", 4 : "2002 Thin bones", 5 : "2002 cough" } , 4)

		EVT_SIZE( self, self._resizeData)
		

	def _resizeData(self, event):
		event.Skip()
		self.SetData( self.GetData() , fitClientSize = 1)
	
	def _getLongestItem(self, list):
		l = 0
		item = None
		for x in list:
			if len(x) > l:
				l = len(x)
				item = x
		return  item		

	def _getPredictedRows(self, map):
		(w,h) = self.GetClientSize()
		predictedRows = h/ (self.GetRowSize(0) + 1)  
		if predictedRows == 0: 
			predictedRows = 4
		predictedCols = len(map) / predictedRows
		
		(x,y ) = self.GetTextExtent(self._getLongestItem(map.values())[1] ) 
		maxCols = w / (x + EXTRA_ROW_SPACE)
		if maxCols == 0:
			maxCols = 1
		if predictedCols >= maxCols:
			predictedCols = maxCols 
			predictedRows = len(map) / predictedCols + 1
			
		print "text extent", x, y,"  ;row height ", self.GetRowSize(0), "; client size", w, h , "  ;maxCols", maxCols, "  predictedCols", predictedCols, "  predictedRows", predictedRows	

		return predictedRows

	def SetData( self, map,  maxRows = 8 , fitClientSize = 0):
		self.GetTable().SetValue(0,0, 'AAAAAAAAAAAAAAAA')
		if fitClientSize:
			predictedRows = self._getPredictedRows(map)
			
		self.ClearGrid()
		rows = []
		cols = []
		seqTypes = ( type([]), type( () ) )
		for k,v in map.items():
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

		self.data = map
		
	def GetData(self):
		return self.data
		



			
	

if __name__ == "__main__":
	 app = wxPyWidgetTester(size = (400, 100))
         app.SetWidget(MultiColumnList, -1)
	 app.MainLoop()
