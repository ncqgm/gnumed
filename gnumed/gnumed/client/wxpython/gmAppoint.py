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
# @Date: $Date: 2005-09-28 21:27:30 $
# @version $Revision: 1.15 $ $Date: 2005-09-28 21:27:30 $ $Author: ncq $
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


class MainWindow(wx.Panel):
    def __init__(self,parent,id, a):
        wx.Panel.__init__ (self, parent, id)
        # colour to mark free times. FIXME: set from configuration system.
        self.freecolour = wx.GREEN
        self.bookedcolour = wx.BLUE
        self.nobookcolour = wx.WHITE
        # setup calendar
        cID = wx.NewId ()
        self.calendar = wx.CalendarCtrl(self, cID,
                                       style=wx.CAL_MONDAY_FIRST |
                                       wx.CAL_SHOW_HOLIDAYS)
        wx.EVT_CALENDAR_DAY (self.calendar, cID, self.OnDayChange)

        # get database connection
        self.db = gmPG.ConnectionPool ()
        self.doctors = self.GetDoctors ()

        # setup booking grid
        lID = wx.NewId ()
        self.grid = wx.Grid (self, lID)
        self.cell_selected_active = 0
        wx.EVT_GRID_SELECT_CELL (self.grid, self.onCellSelected)
        wx.EVT_GRID_CELL_LEFT_DCLICK (self.grid, self.onCellDClicked)
        wx.EVT_GRID_CELL_RIGHT_CLICK (self.grid, self.onCellGetFloatMenu)
        wx.EVT_GRID_LABEL_LEFT_DCLICK (self.grid, self.onDoctorClicked)
        self.grid.EnableEditing (0)
        self.grid.CreateGrid (0, len(self.doctors))
        for i in range (0,len(self.doctors)):
            self.grid.SetColLabelValue (i, self.doctors[i][1])
        self.grid.AutoSizeColumns ()
        self.grid.SetDefaultCellBackgroundColour (wx.WHITE)
        self.grid.SetDefaultCellTextColour (wx.BLACK)


        wx.EVT_CHAR (self, self.onChar)

        # buttons and controls in left lower corner
        self.namectrl = wx.TextCtrl (self, -1, style=wx.TE_READONLY)
        buttonid= wx.NewId ()
        self.bookbutton = wx.Button (self, buttonid, "Book...")
        wx.EVT_BUTTON (self.bookbutton, buttonid, self.onBooking)
        buttonid = wx.NewId ()
        self.cancelbutton = wx.Button (self, buttonid, "Cancel....")
        wx.EVT_BUTTON (self.cancelbutton, buttonid, self.onBookCancel)
        buttonid= wx.NewId ()
        self.findbutton = wx.Button (self, buttonid, "Find...")
        wx.EVT_BUTTON (self.findbutton, buttonid, self.onFindPatient)
        buttonid= wx.NewId ()
        self.sessionbutton = wx.Button (self, buttonid, "Sessions...")
        wx.EVT_BUTTON (self.sessionbutton, buttonid, self.onSessionsEdit)


        # button rows
        row1 = wx.BoxSizer (wx.HORIZONTAL)
        row1.Add (wx.StaticText (self, -1, "Patient: "))
        row1.Add (self.namectrl, 1, wx.EXPAND)
        buttonbox = wx.GridSizer (2)
        buttonbox.Add (self.bookbutton, 1, wx.EXPAND)
        buttonbox.Add (self.cancelbutton, 1, wx.EXPAND)
        buttonbox.Add (self.findbutton, 1, wx.EXPAND)
        buttonbox.Add (self.sessionbutton, 1, wx.EXPAND)

        leftsizer = wx.BoxSizer (wx.VERTICAL)
        leftsizer.Add (self.calendar)
        leftsizer.Add (row1, 0, wx.EXPAND)
        leftsizer.Add (buttonbox, 1, wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add (leftsizer, 0, wx.ALL, 5)
        self.sizer.Add (self.grid, 1, wx.EXPAND)

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


class appointapp (wx.App):

    def OnInit (self):  
        frame = wx.Frame(None,-4, "Appointments Book", size=wx.Size (900, 400),
                        style=wx.DEFAULT_FRAME_STYLE|  
                        wx.NO_FULL_REPAINT_ON_RESIZE)
        mainwindow = MainWindow (frame, -1, self)
        wx.EVT_CLOSE (frame, self.OnCloseWindow)
        # Setting up the menu.  
        filemenu= wx.Menu()     
        filemenu.Append(ID_ABOUT, "&About"," Information about this program")  
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        # Creating the menubar.  
        menuBar = wx.MenuBar()  
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
        frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        wx.EVT_MENU(frame, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)
        frame.Show(1)
        return 1

    def OnAbout(self,e):
        d= wx.MessageDialog( self, " A drug database editor",
                            "About Drug DB", wx.OK)
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
# Revision 1.15  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.14  2005/09/28 15:57:47  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.13  2005/09/26 18:01:50  ncq
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