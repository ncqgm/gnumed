from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.HTML import HTML
from pyjamas.ui.MenuBar import MenuBar
from pyjamas.ui.MenuItem import MenuItem
from pyjamas.ui.DecoratorPanel import DecoratedTabPanel
from pyjamas import Window

from pyjamas.builder.Builder import Builder, HTTPUILoader
import GMWevents
import Remote

from TestPanel import cTestPanel
from PatientsummaryPanel import cPatientsummaryPanel
from PatientsearchPanel import cPatientsearchPanel
from OpenCommand import cOpenCommand
from SaveCommand import cSaveCommand
from LogoutCommand import cLogoutCommand

#======================================================
class cMainPanel(cOpenCommand, cSaveCommand, cLogoutCommand):

    def __init__(self):

        HTTPUILoader(self).load("gnumedweb.xml") # calls onUILoaded when done

    def onUILoaded(self, text):
        self.b = Builder(text)
        self.mp = self.b.createInstance("MainPanel", self)

        # tab panel
        self.mp.fTabs.add(cPatientsummaryPanel(), "Patient summary")
        self.mp.fTabs.add(HTML("Panel 2"), "Tab2")
        self.mp.fTabs.add(HTML(""), None) # spacer
        self.mp.fTabs.add(cTestPanel(), "RPC Test")
        self.mp.fTabs.add(HTML("This is a Test.<br />Tab should be on right"),
                       "Test")
        self.mp.fTabs.selectTab(0)

        self.searchpanel = cPatientsearchPanel()
        self.mp.insert(self.searchpanel, 1)

    def getPanel(self):
        return self.mp

    def onMenuItemRegisterPerson(self):
        print "TODO: register person"

