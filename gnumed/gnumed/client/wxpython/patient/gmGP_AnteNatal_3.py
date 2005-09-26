try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx
	from wxPython import grid

import string

from Gnumed.wxpython import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
from Gnumed.wxpython import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
from Gnumed.wxpython import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
from Gnumed.wxpython import gmPlugin_Patient, gmEditArea

from Gnumed.wxpython.gmPatientHolder import PatientHolder
ID_ANCNOTEBOOK =wxNewId()
#---------------------------------------------------------------------------

class CustomDataTable(wxPyGridTableBase):
    """
    """

    def __init__(self):
        wxPyGridTableBase.__init__(self)
        #self.log = log

        self.colLabels = ['Date', 'Gest','Fundus', 'Girth', 'Presentation', ' FH ',
                          '  Urine  ', '  BP  ', 'Weight','       Comment       ']
        self.dataTypes = [wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_CHOICE + ':cephalic,breech,transverse',
                          wxGRID_VALUE_CHOICE + ':FMF,FHH',
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING,
                          wxGRID_VALUE_STRING]

        self.data = [
            ['20/10/2001', "31", '32',"", 'cephalic', 'FHH', 'NAD', '120/70', '77kg','?UTI msu sent'],
            #[1011, "I've got a wicket in my wocket", "wish list", 2, 'other', 0, 0, 0,0],
            #[1012, "Rectangle() returns a triangle", "critical", 5, 'all', 0, 0, 0,0]

            ]


    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data) + 1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        return not self.data[row][col]

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        try:
            self.data[row][col] = value
        except IndexError:
            # add a new row
            self.data.append([''] * self.GetNumberCols())
            self.SetValue(row, col, value)

            # tell the grid we've added a row
            msg = wxGridTableMessage(self,                             # The table
                                     wxGRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                     1)                                # how many

            self.GetView().ProcessTableMessage(msg)


    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # nativly by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = string.split(self.dataTypes[col], ':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)





#---------------------------------------------------------------------------



class CustTableGrid(wxGrid):
    def __init__(self, parent):
        wxGrid.__init__(self, parent, -1)

        table = CustomDataTable()

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(True)

        EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)



    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()


#---------------------------------------------------------------------------
class AntenatalPanel (wxPanel , PatientHolder):
     def __init__(self,parent, id):
  	  wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxNO_BORDER)
	  PatientHolder.__init__(self)
	  self.sizer = wxBoxSizer(wxHORIZONTAL)
	  self.notebook1 = wxNotebook(self, -1, wxDefaultPosition, wxDefaultSize, style =0)
	  ListScript_ID = wxNewId()                                                         #can use wxLC_VRULES to put faint cols in list
	  #self.List_Script = wxListCtrl(self.notebook1, ListScript_ID,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
	  #self.List_Script.SetForegroundColour(wxColor(131,129,131))
	  self.firstvisitpanel = wxPanel(self.notebook1,-1)
	  self.scanpanel = wxPanel(self.notebook1,-1)
	  self.grid = CustTableGrid(self.notebook1)
	  self.notebook1.AddPage(self.firstvisitpanel, "First Visit")
	  self.notebook1.AddPage(self.grid, "Ante-natal Chart")
	  self.notebook1.AddPage(self.scanpanel, "Scans")
	  #self.notebook1.AddPage(self.grid, "Scans")
	  self.notebook1.SetSelection(0) 
	  self.szr_notebook = wxNotebookSizer(self.notebook1)
	  self.sizer.AddSizer(self.szr_notebook,1,wxEXPAND)
	  self.SetSizer(self.sizer)
	  self.sizer.Fit(self) 
          self.SetAutoLayout(True)
          self.Show(True)
    

class gmGP_AnteNatal_3 (gmPlugin_Patient.wxPatientPlugin):
	"""
	Plugin to encapsulate the antenatalcare window
	"""
	__icons = {
"""icon-future_mom""":"x\xdam\x90?o\x830\x10\xc5\xf7|\nKNB\x15\x1cd\xc0\x80!\x7fDm`\xac\x87,\xacQ\
\xd4\xa9Q\xe9\xf7\x9f\xea\xf3\xd9Uq\xeb[\xf8\xbd\xf7\xee\x0e\xfb\xe5\xf9\x95\
onI^\x93\\\x92\xa2%y\xb2\xb9\xdf\x12I\x1eD=\xef\x8f\x0fG\xc6\x12-9\x94\xe3\
\x12\xb8\xe5\x927\xc8\x15\xb0\xe6\x9ck\xe4\x03\xf0 \xb5P\xc8[\xe0\x89\x0f\
\xda\xfb\x02\xf3*0G\xd6\xa1\xff\x8a\xfdP\x8e\x8f\xd8?\xea\t\xfd\xcc\xfb\xda\
\xfb\x17\xd7/\x95xE?uy9r\x8d\xfe\x1e\xd8\x92V\xc8\xd4\xfb\xc2\xfb;\xcf\xd2s\
\x1fx\xc0y'\x9c\xaf\x83?\xe3\xbcA\x8f\xe8\xd7\x98ox\x81\xdc\xa2\x0f\xe5\xb8\
\xf1\xbe\xf0>\xb1\xfc\xb6|\xbe;`hNz\xc2\xe19\xb0\x94?\x8f\xdb\x01W\x12\xcaq\
\x01\xac\xa4\n\x979\xbb\xc7\xe0P\x8e\x17\xcfb\x08\xcbH6g\xf3b\xec\xb1\xdf$\
\x88pL\xda\xd3\xadY\x8b\x86R\xbas\xeao1\xa5=\xed\xf7&j?Pz\x89\xdaA\x86E\xd9:\
i\x8e\xa7.^te\xe7\x8e\xe6\xab\x99\x861Vt\xb4\x8c\xb63&\xba\xfeo\x92EI\xc3\
\xaa\xaab\xeb\xa4\xd5\xea\xba\x8a\x92 6\xff$mw\x94\x94\x19\xec\x89\xb7\x9b\
\xd6\x8a<\xfeO\xe3\x0f^3\xfb\x06\xbe\xc9\xae+"
}

	def name (self):
		return 'Ante-natal'

	def MenuInfo (self):
		return ('view', '&Ante-natal')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon-future_mom""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon-future_mom""")]
	   
	def GetWidget (self, parent):
		return  AntenatalPanel (parent, -1)


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(AntenatalPanel, -1)
	app.MainLoop()
