#!/usr/bin/python
"""
Manager class for the main window.
Allows plugins to register, and swap in an out of view.
A plugin may elect to be in three modes:
- wholescreen - the plugin seizes the whole panel
- lefthalf - the plugin gets the left column onscreen, the right
column becomes visible.
- right column - the plugin is added to a vertical sizer on the right
hand column (note all of these plugins are visible at once)
"""



from wxPython.wx import *
from gmLog import *
log = gmDefLog.Log
import gmConf
import gmGuiBroker
import gmDispatcher
import gmShadow
import gmPlugin

class PatientWindow (wxPanel):

    def __init__ (self, parent):
        wxPanel.__init__ (self, parent, -1)
        EVT_SIZE (self, self.OnSize)
        self.__gb = gmGuiBroker.GuiBroker ()
        self.wholescreen = {}
        self.lefthalf = {}
        self.visible = '' # plugin currectly visible in left or whole
        # screen
        self.default = '' # set by one plugin!
        self.righthalf = {}
        self.sizer = wxBoxSizer (wxHORIZONTAL)
        self.SetSizer (self.sizer)

    def OnSize (self, event):
        w,h = self.GetClientSizeTuple ()
        self.sizer.SetDimension (0,0, w, h)

    def SetDefault (self, d):
        self.default = d

    def DisplayDefault (self):
        self.Display (self.default)

    def RegisterWholeScreen (self, name, panel):
        """
        Recieves a wxPanel which is to fill the whole screen
        Client must NOT do Show () on the panel!
        """ 
        self.wholescreen[name] = panel
        panel.Show (0) # make sure all hidden
        #log (lInfo, "Registering %s as whole screen widget" % name)

    def RegisterLeftSide (self, name, panel):
        """
        Register for left side
        """
        self.lefthalf[name] = panel
        panel.Show (0)
        

    def RegisterRightSide (self, name, panel, position =1):
        """
        Register for right column
        Note there is no display function for these: they are
        automatcially displayed when a left-column plugin is displayed
        """
        self.righthalf[name] = (panel, position)
        panel.Show (0)
        #log (lInfo, "Registering %s as right side widget" % name)

    def Unregister (self, name):
        if name == self.default:
            log (lErr, 'Cannot delete %s' % name)
        else:
            if self.visible == name:
                self.Display (self.default)
            log (lInfo, 'Unregistering widget %s' % name)
            if self.righthalf.has_key (name):
                if self.lefthalf.has_key (self.visible):
                    self.vbox.Remove (self.righthalf[name][0])
                    self.vbox.Layout ()
                del self.righthalf[name]
            elif self.lefthalf.has_key (name):
                del self.lefthalf[name]
            elif self.wholescreen.has_key (name):
                del self.wholescreen[name]
            else:
                log (lErr, 'tried to delete non-existent widget %s' % name)
            

    def Display (self, name):
        """
        Displays the named widget
        """
        if self.wholescreen.has_key (name):
            self.DisplayWhole (name)
        elif self.lefthalf.has_key (name):
            self.DisplayLeft (name)
        else:
            log (lErr, 'Widget %s not registered' % name)

    def DisplayWhole (self, name):
        log (lInfo, 'displaying whole screen widget %s' % name)
        if self.wholescreen.has_key (self.visible):
            # already in full-screen mode
            self.wholescreen[self.visible].Show (0)
            self.sizer.Remove (0)
            self.sizer.Add (self.wholescreen[name])
            self.wholescreen[name].Show (1)
            self.sizer.Layout ()
            self.visible = name
        else:
            if self.lefthalf.has_key (self.visible):
                # remove left half and right column
                self.sizer.Remove (0)
                self.lefthalf[self.visible].Show (0)
                for widget, position in self.righthalf.values ():
                    self.vbox.Remove (widget)
                    widget.Show (0)
                self.sizer.Remove (self.vbox)
            # now put whole screen in
            self.wholescreen[name].Show (1)
            self.sizer.Add (self.wholescreen[name], 1, wxEXPAND, 0)
            self.visible = name
            self.sizer.Layout ()

    def DisplayLeft (self, name):
        log (lInfo, 'displaying left screen widget %s' % name)
        if self.lefthalf.has_key (self.visible):
            self.sizer.Remove (self.lefthalf[self.visible])
            self.lefthalf[self.visible].Show (0)
            self.lefthalf[name].Show (1)
            self.sizer.Prepend (self.lefthalf[name], 2, wxEXPAND, 0)
            self.sizer.Layout ()
            self.visible = name
        else:
            if self.wholescreen.has_key (self.visible):
                self.sizer.Remove (self.wholescreen[self.visible])
                self.wholescreen[self.visible].Show (0)
            self.lefthalf[name].Show (1)
            self.sizer.Add (self.lefthalf[name], 2, wxEXPAND, 0)
            self.vbox = wxBoxSizer (wxVERTICAL)
            pos = 1
            done = 0
            while done < len (self.righthalf.values ()):
                for w, p in self.righthalf.values ():
                    if p == pos:
                        w.Show (1)
                        self.vbox.Add (w, 1, wxEXPAND, 0)
                        done += 1
                pos += 1
            self.sizer.Add (self.vbox, 1, wxEXPAND, 0) 
            self.sizer.Layout ()
            self.visible = name

    def GetVisible (self):
        return self.visible
            
class gmPatientWindowManager (gmPlugin.wxNotebookPlugin):


    def name (self):
        return "Patient"

    def MenuInfo (self):
        return None # we add our own submenu

    def GetWidget (self, parent):
        self.pw = PatientWindow (parent)
        self.gb['patient.manager'] = self.pw
        return self.pw

    def register (self):
        gmPlugin.wxNotebookPlugin.register (self)
        # add own submenu, patient plugins add to this
        ourmenu = wxMenu ()
        self.gb['patient.submenu'] = ourmenu
        menu = self.gb['main.viewmenu']
        self.menu_id = wxNewId ()
        menu.AppendMenu (self.menu_id, '&Patient', ourmenu, self.name ())
        for plugin in gmPlugin.GetAllPlugins ('patient'):
            gmPlugin.LoadPlugin ('patient', plugin,
                                 guibroker = self.gb)
        self.pw.DisplayDefault ()
        self.gb['toolbar.%s' % self.name ()].Realize ()

    def Shown (self):
        self.gb['modules.patient'][self.pw.GetVisible ()].Shown ()
            
        
    
    



