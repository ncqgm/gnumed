#!/usr/bin/python
#!/usr/bin/python
#############################################################################
#
# gmAppoint - A simple interface to the appointments book.
#             INCOMPLETE, do not link in to rest of app.
# ---------------------------------------------------------------------------
#
# @author: Ian Haywood
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @Date: $Date: 2002-03-15 00:37:19 $
# @version $Revision: 1.2 $ $Date: 2002-03-15 00:37:19 $ $Author: ihaywood $
# @change log:
#	14.03.02 ihaywood inital version.
#      
#               
#
# @TODO: everything
#
############################################################################
"""GNUMed Appointment book.
A simple interface to the appointments book.
"""

# text translation function for localization purposes
import gettext
_ = gettext.gettext
from wxPython.wx import *
from wxPython.calendar import *
from wxPython.grid import *
from gmI18N import *
import sys, time, os
import gmGuiBroker, gmPG, gmmanual, gmSQLSimpleSearch


ID_ABOUT=101  
ID_OPEN=102 
ID_BUTTON1=110 
ID_EXIT=200


class MainWindow(wxPanel):
    def __init__(self,parent,id, a):
        self.dbpool = gmPG.ConnectionPool () 
        wxPanel.__init__ (parent, id)
        # colour to mark free times. FIXME: set from configuration system.
        self.freecolour = wxGREEN
        self.bookedcolour = wxBLUE
        self.nobookcolour = wxWHITE
        # setup calendar
        cID = wxNewId ()
        self.calendar = wxCalendarCtrl(self, cID,
                                       style=wxCAL_MONDAY_FIRST |
                                       wxCAL_SHOW_HOLIDAYS)
        EVT_CALENDAR_DAY (self.calendar, cID, self.OnDayChange)
        # setup booking grid
        lID = wxNewId ()
        self.grid = wxGrid (self, lID)
        EVT_GRID_SELECT_CELL (self.grid, onCellSelected)
        EVT_GRID_CELL_LEFT_DCLICK (self.grid, onCellDClicked)
        EVT_GRID_CELL_RIGHT_CLICKED (self.grid, onCellGetFloatMenu)
        EVT_GRID_LABEL_LEFT_DCLICK (self.grid, onDoctorClicked)
        self.doctors = self.GetDoctors () 
        self.grid_num_rows = 10
        self.grid.CreateGrid (len (self.doctors), self.num_rows)
        self.grid.SetDefaultCellBackgroundColour (wxWHITE)
        self.grid.SetDefaultCellTextColour (wxBLACK)
        self.grid.DisableCellEditControl ()

        EVT_CHAR (self, self.onChar)

        # buttons and controls in left lower corner
        self.namectrl = wxTextCtrl (self, -1, style=wxTE_READONLY)
        buttonid= wxNewId ()
        self.bookbutton = wxButton (self, buttonid, "Book...")
        EVT_BUTTON (self.bookbutton, self.onBooking)
        buttonid = wxNewId ()
        self.cancelbutton = wxButton (self, buttonid, "Cancel....")
        EVT_BUTTON (self.cancelbutton, self.onBookCancel)
        buttonid= wxNewId ()
        self.findbutton = wxButton (self, buttonid, "Find...")
        EVT_BUTTON (self.findbutton, self.onFindPatient) 
        buttonid= wxNewId ()
        self.sessionbutton = wxButton (self, buttonid, "Sessions...")
        EVT_BUTTON (self.sessionbutton, self.onSessionsEdit)


        # button rows
        row1 = wxBoxSizer (wxHORIZONTAL)
        row1.Add (wxStaticText (self, -1, "Patient: "), 1, wxEXPAND, 0)
        row1.Add (self.namectrl, 1, wxEXPAND, 0)
        row2 = wxBoxSizer (wxHORIZONTAL)
        row2.Add (self.bookbutton, 1, wxEXPAND, 0)
        row2.Add (self.cancelbutton, 1, wxEXPAND, 0)
        row3 = wxBoxSizer (wxHORIZONTAL)
        row3.Add (self.findbutton, 1, wxEXPAND, 0)
        row3.Add (self.sessionbutton, 1, wxEXPAND, 0)

        leftsizer = wxBoxSizer (wxVERTICAL)
        leftsizer.Add (self.calendar, 0, wxALL, 0)
        leftsizer.Add (row1, 0, wxALL, 0)
        leftsizer.Add (row2, 0, wxALL, 0)
        leftsizer.Add (row3, 0, wxALL, 0)
        
        self.sizer = wxBoxSizer(wxHORIZONTAL) 
        self.sizer.Add (self.calendar, 0, wxALL, 5)
        self.sizer.Add (self.grid, 1, wxEXPAND)
         
        #Layout sizers 
        self.SetSizer(self.sizer) 
        self.SetAutoLayout(1) 
        self.sizer.Fit(self) 
        self.Show(1)

        # set grid to today's date
        self.SetGrid (time.strftime ("%d %b %Y"))

    def OnDayChange (self, event):
        print event.GetDate ()
        self.SetGrid (event.GetDate ()[4:14]) # get just the date

    def SetGrid (self, date):
        select = ''
        for doc in self.doctors:
            select += 'is_booked (%d, %s, time),' % (doc[0], date)
        select = select[0,-1] # delete final comma
        cursor = self.dbpool.GetConnection ('appoint').cursor ()
        cursor.execute ("""
SELECT time, %s FROM list WHERE float8 (day) = extract (dow from date ''%s'')
ORDER BY time""" % (select, date))
        result = cursor.fetchall ()
        self.dbpool.ReleaseConnection ('appoint')
        self.grid_num_rows = len (result)
        self.grid.SetNumRows (self.grid_num_rows)
        line = 0
        for i in result:
            col = 0
            for j in i:
                if j is not None:
                    if j:
                        self.grid.SetCellBackgroundColor (self.bookedcolour,
                                                          line, col)
                    else:
                        self.grid.SetCellBackgroundColour (self.freecolour,
                                                           line, col)
                else:
                    self.grid.SetCellBackgroundColor (self.nobookcolour,
                                                      line, col)
                col += 1
            line += 1

    # return list of doctor_number, doctor_name tuples
    def GetDoctors (self):
        cursor = self.dbpool.GetConnection ('appoint').cursor ()
        cursor.execute ("SELECT id, name FROM clinician")
        self.dbpool.ReleaseConnection ('appoint')
        return cursor.fetchall ()


    
# This is a framework for a Free Bonus standalone application
# for making bookings
#
        
def OnAbout(self,e):  
    d= wxMessageDialog( self, " A drug database editor",
                        "About Drug DB", wxOK)  
    # Create a message dialog box  
    d.ShowModal() # Shows it  
    d.Destroy() # finally destroy it when finished.  
    
    
def OnCloseWindow (self, e):
    self.app.ExitMainLoop ()        




if __name__ = '__main__':        
    app = wxPySimpleApp()  
    frame = wxFrame(None,-4, "Appointments Book",
                    style=wxDEFAULT_FRAME_STYLE|  
                    wxNO_FULL_REPAINT_ON_RESIZE)
    mainwindow = MainWindow (frame, -1, app)
    EVT_CLOSE (frame, OnCloseWindow)
    # Setting up the menu.  
    filemenu= wxMenu()     
    filemenu.Append(ID_ABOUT, "&About"," Information about this program")  
    filemenu.AppendSeparator()  
    filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
    # Creating the menubar.  
    menuBar = wxMenuBar()  
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar  
    frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.  
    EVT_MENU(frame, ID_ABOUT, OnAbout) 
    EVT_MENU(frame, ID_EXIT, OnCloseWindow) 

    frame.Show(1)  
    app.MainLoop() 

