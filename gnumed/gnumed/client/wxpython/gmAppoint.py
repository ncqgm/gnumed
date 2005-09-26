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
# @Date: $Date: 2005-09-26 18:01:50 $
# @version $Revision: 1.13 $ $Date: 2005-09-26 18:01:50 $ $Author: ncq $
#      
#               
#
# @TODO: everything
#
############################################################################
"""GNUMed Appointment book.
A simple interface to the appointments book.
"""

import sys, time, os

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#from wxPython.wx import *
#from wxPython.calendar import *
#from wxPython.grid import *

from Gnumed.pycommon import gmGuiBroker, gmPG
from Gnumed.wxpython import gmSQLSimpleSearch


ID_ABOUT=101  
ID_OPEN=102 
ID_BUTTON1=110 
ID_EXIT=200


class MainWindow(wxPanel):
    def __init__(self,parent,id, a):
        wxPanel.__init__ (self, parent, id)
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

        # get database connection
        self.db = gmPG.ConnectionPool ()
        self.doctors = self.GetDoctors ()

        # setup booking grid
        lID = wxNewId ()
        self.grid = wxGrid (self, lID)
        self.cell_selected_active = 0
        EVT_GRID_SELECT_CELL (self.grid, self.onCellSelected)
        EVT_GRID_CELL_LEFT_DCLICK (self.grid, self.onCellDClicked)
        EVT_GRID_CELL_RIGHT_CLICK (self.grid, self.onCellGetFloatMenu)
        EVT_GRID_LABEL_LEFT_DCLICK (self.grid, self.onDoctorClicked)
        self.grid.EnableEditing (0)
        self.grid.CreateGrid (0, len(self.doctors))
        for i in range (0,len(self.doctors)):
            self.grid.SetColLabelValue (i, self.doctors[i][1])
        self.grid.AutoSizeColumns ()
        self.grid.SetDefaultCellBackgroundColour (wxWHITE)
        self.grid.SetDefaultCellTextColour (wxBLACK)


        EVT_CHAR (self, self.onChar)

        # buttons and controls in left lower corner
        self.namectrl = wxTextCtrl (self, -1, style=wxTE_READONLY)
        buttonid= wxNewId ()
        self.bookbutton = wxButton (self, buttonid, "Book...")
        EVT_BUTTON (self.bookbutton, buttonid, self.onBooking)
        buttonid = wxNewId ()
        self.cancelbutton = wxButton (self, buttonid, "Cancel....")
        EVT_BUTTON (self.cancelbutton, buttonid, self.onBookCancel)
        buttonid= wxNewId ()
        self.findbutton = wxButton (self, buttonid, "Find...")
        EVT_BUTTON (self.findbutton, buttonid, self.onFindPatient)
        buttonid= wxNewId ()
        self.sessionbutton = wxButton (self, buttonid, "Sessions...")
        EVT_BUTTON (self.sessionbutton, buttonid, self.onSessionsEdit)


        # button rows
        row1 = wxBoxSizer (wxHORIZONTAL)
        row1.Add (wxStaticText (self, -1, "Patient: "))
        row1.Add (self.namectrl, 1, wxEXPAND)
        buttonbox = wxGridSizer (2)
        buttonbox.Add (self.bookbutton, 1, wxEXPAND)
        buttonbox.Add (self.cancelbutton, 1, wxEXPAND)
        buttonbox.Add (self.findbutton, 1, wxEXPAND)
        buttonbox.Add (self.sessionbutton, 1, wxEXPAND)

        leftsizer = wxBoxSizer (wxVERTICAL)
        leftsizer.Add (self.calendar)
        leftsizer.Add (row1, 0, wxEXPAND)
        leftsizer.Add (buttonbox, 1, wxEXPAND)

        self.sizer = wxBoxSizer(wxHORIZONTAL)
        self.sizer.Add (leftsizer, 0, wxALL, 5)
        self.sizer.Add (self.grid, 1, wxEXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show(1)

        # set grid to today's date
        self.SetGrid (time.strftime ("%d %b %Y"))

    def OnDayChange (self, event):
        self.cell_selected_active = 0 # stop spurious calls to onCellSelected
        self.SetGrid (event.GetDate ().Format("%d %b %Y")) # get just the date
        self.cell_selected_active = 1

    def SetGrid (self, date):
        select = ''
        for doc in self.doctors:
            select += 'is_booked (%d, \'%s\', list.time),' % (doc[0], date)
        select = select[0:-1] # delete final comma
        cursor = self.db.GetConnection ('appointments').cursor ()
        cursor.execute ("""
SELECT DISTINCT ON (l.time) l.time %s FROM list l, session s WHERE
float8 (s.day) = extract (dow from date \'%s\')
AND
session.id = list.session
ORDER BY time""" % (select, date))
        result = cursor.fetchall ()
        self.db.ReleaseConnection ('appointments')
        # if there's a better way of doinf this I don't know...
        self.grid.DeleteRows (numRows=self.grid.GetNumberRows ())
        self.grid.AppendRows (len (result))
        line = 0
        for i in result:
            self.grid.SetRowLabelValue (line, i[0][:-3])
            col = 0
            for j in i[1:]:
                if j is not None:
                    if j:
                        self.grid.SetCellBackgroundColour (line, col,
                                                          self.bookedcolour)
                    else:
                        self.grid.SetCellBackgroundColour (line, col, self.freecolour)                      
                else:
                    self.grid.SetCellBackgroundColour (line, col,
                                                      self.nobookcolour)
                col += 1
            line += 1
        # KLUDGE: this prevents the first cell selected from having thw wrong
        # background colour
        self.grid.SetGridCursor (1, 1)
        self.grid.SetGridCursor (0,0)

    # return list of doctor_number, doctor_name tuples
    def GetDoctors (self):
        cursor = self.db.GetConnection ('appointments').cursor ()
        cursor.execute ("SELECT id, name FROM clinician")
        self.db.ReleaseConnection ('appointments')
        return cursor.fetchall ()

    # callabcks for UI
    def onCellSelected (self, event):
        if self.cell_selected_active:
            pass
        # NOT DOCUMENTED!!!:
        # event.GetCol (), event.GetRow ()
        event.Skip ()

    def onCellDClicked (self, event):
        "when a cell is double-clicked"
        pass

    def onCellGetFloatMenu (self, event):
        pass

    def onDoctorClicked (self, event):
        pass

    def onChar (self, event):
        pass

    # callbacks for buttons

    def onBooking (self, event):
        pass

    def onSessionsEdit (self, event):
        pass

    def onBookCancel (self, event):
        pass

    def onFindPatient (self, event):
        pass


# This is a framework for a Free Bonus standalone application
# for making bookings


class appointapp (wxApp):

    def OnInit (self):  
        frame = wxFrame(None,-4, "Appointments Book", size=wxSize (900, 400),
                        style=wxDEFAULT_FRAME_STYLE|  
                        wxNO_FULL_REPAINT_ON_RESIZE)
        mainwindow = MainWindow (frame, -1, self)
        EVT_CLOSE (frame, self.OnCloseWindow)
        # Setting up the menu.  
        filemenu= wxMenu()     
        filemenu.Append(ID_ABOUT, "&About"," Information about this program")  
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        # Creating the menubar.  
        menuBar = wxMenuBar()  
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
        frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        EVT_MENU(frame, ID_ABOUT, self.OnAbout)
        EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)
        frame.Show(1)
        return 1

    def OnAbout(self,e):
        d= wxMessageDialog( self, " A drug database editor",
                            "About Drug DB", wxOK)
        # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.

    def OnCloseWindow (self, e):
        self.ExitMainLoop ()

def run ():
    import os, sys
    #os.chdir (os.path.split(sys.argv[0])[0])
    app = appointapp (0)
    app.MainLoop ()


if __name__ == '__main__':
    # text translation function for localization purposes
    import gmI18N
    run ()

#=================================================================
# $Log: gmAppoint.py,v $
# Revision 1.13  2005-09-26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.12  2004/06/20 15:46:20  ncq
# - better please epydoc
#

#
# @change log:
#   14.03.02 ihaywood inital version.