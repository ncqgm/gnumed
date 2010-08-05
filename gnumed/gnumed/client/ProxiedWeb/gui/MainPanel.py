from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.HTML import HTML
from pyjamas.ui.MenuBar import MenuBar
from pyjamas.ui.MenuItem import MenuItem
from pyjamas.ui.DecoratorPanel import DecoratedTabPanel
from pyjamas import Window

from TestPanel import cTestPanel
from PatientsummaryPanel import cPatientsummaryPanel
from OpenCommand import cOpenCommand
from SaveCommand import cSaveCommand
from LogoutCommand import cLogoutCommand

#======================================================
class cMainPanel(VerticalPanel):
    def __init__(self, app, **kwargs):
        self.app = app
        VerticalPanel.__init__(self, **kwargs)

        # tab panel
        self.fTabs = DecoratedTabPanel(Size=("1024px", "100%"))
        self.fTabs.add(cPatientsummaryPanel(app), "Patient summary")
        self.fTabs.add(HTML("Panel 2"), "Tab2")
        self.fTabs.add(HTML(""), None) # spacer
        self.fTabs.add(cTestPanel(app), "RPC Test")
        self.fTabs.add(HTML("This is a Test.<br />Tab should be on right"),
                       "Test")
        self.fTabs.selectTab(0)

        # commands
        self.savecmd = cSaveCommand(app)
        self.opencmd = cOpenCommand(app)
        self.logoutcmd = cLogoutCommand(app)

        # menu
        self.menu = MenuBar()

        menuGNUmed = MenuBar(True)
        subMenuGoToPlugin = MenuBar(True)
        subMenuGoToPlugin.addItem("Patient summary", True, self)
        subMenuGoToPlugin.addItem("<strike>Strikethrough</strike>", True, self)
        subMenuGoToPlugin.addItem("<u>Underlined</u>", True, self)
        menuGNUmed.addItem(MenuItem("Go to plugin",subMenuGoToPlugin))
        menuGNUmed.addItem("Preferences", True, self.opencmd)
        menuGNUmed.addItem("Logout", True, self.logoutcmd)
        
        menuPerson = MenuBar(True)
        menuPerson.addItem("Register person", True, self)
        menuPerson.addItem("<font color='#FFFF00'><b>Banana</b></font>", True, self)
        menuPerson.addItem("<font color='#FFFFFF'><b>Coconut</b></font>", True, self)
        menuPerson.addItem("<font color='#8B4513'><b>Donut</b></font>", True, self)

        menuEMR = MenuBar(True)
        menuEMR.addItem("Bling", self)
        menuEMR.addItem("Ginormous", self)
        menuEMR.addItem("<code>w00t!</code>", True, self)

        menuCorrespondence = MenuBar(True)
        subMenu = MenuBar(True)
        subMenu.addItem("<code>Code</code>", True, self)
        subMenu.addItem("<strike>Strikethrough</strike>", True, self)
        subMenu.addItem("<u>Underlined</u>", True, self)
        menuCorrespondence.addItem(MenuItem("Submenu",subMenu))
        
        menuTools = MenuBar(True)
        menuKnowledge = MenuBar(True)
        menuOffice = MenuBar(True)
        menuHelp = MenuBar(True)


        self.menu.addItem(MenuItem("GNUmed", menuGNUmed))
        self.menu.addItem(MenuItem("Person", menuPerson))
        self.menu.addItem(MenuItem("EMR", menuEMR))
        self.menu.addItem(MenuItem("Correspondence", menuCorrespondence))
        self.menu.addItem(MenuItem("Tools", menuTools))
        self.menu.addItem(MenuItem("Knowledge", menuKnowledge))
        self.menu.addItem(MenuItem("Office", menuOffice))
        self.menu.addItem(MenuItem("Help", menuHelp))

        self.menu.setWidth("100%")

        # add tabs and menu
        self.add(self.menu)
        self.add(self.fTabs)

    def execute(self):
        Window.alert("Thank you for selecting a menu item.")


