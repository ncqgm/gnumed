from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.HTML import HTML
from pyjamas.ui.MenuBar import MenuBar
from pyjamas.ui.MenuItem import MenuItem
from pyjamas.ui.DecoratorPanel import DecoratedTabPanel
from pyjamas import Window

from TestPanel import cTestPanel
from OpenCommand import cOpenCommand
from SaveCommand import cSaveCommand
from LogoutCommand import cLogoutCommand

#======================================================
class cMainPanel(VerticalPanel):
    def __init__(self, app, **kwargs):
        self.app = app
        VerticalPanel.__init__(self, **kwargs)

        # tab panel
        self.fTabs = DecoratedTabPanel(Size=("600px", "100%"))
        self.fTabs.add(HTML("Panel 1"), "Tab 1")
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

        subMenu = MenuBar(True)
        subMenu.addItem("<code>Code</code>", True, self)
        subMenu.addItem("<strike>Strikethrough</strike>", True, self)
        subMenu.addItem("<u>Underlined</u>", True, self)

        menu0 = MenuBar(True)
        menu0.addItem("Go to plugin", True, self.savecmd)
        menu0.addItem("Preferences", True, self.opencmd)
        menu0.addItem("Logout", True, self.logoutcmd)
        menu1 = MenuBar(True)
        menu1.addItem("Register person", True, self)
        menu1.addItem("<font color='#FFFF00'><b>Banana</b></font>", True, self)
        menu1.addItem("<font color='#FFFFFF'><b>Coconut</b></font>", True, self)
        menu1.addItem("<font color='#8B4513'><b>Donut</b></font>", True, self)
        menu2 = MenuBar(True)
        menu2.addItem("Bling", self)
        menu2.addItem("Ginormous", self)
        menu2.addItem("<code>w00t!</code>", True, self)
        menu3 = MenuBar(True)
        menu4 = MenuBar(True)
        menu5 = MenuBar(True)
        menu6 = MenuBar(True)
        menu7 = MenuBar(True)

        self.menu.addItem(MenuItem("GNUmed", menu0))
        self.menu.addItem(MenuItem("Person", menu1))
        self.menu.addItem(MenuItem("EMR", menu2))
        self.menu.addItem(MenuItem("Correspondence", menu3))
        self.menu.addItem(MenuItem("Tools", menu4))
        self.menu.addItem(MenuItem("Knowledge", menu5))
        self.menu.addItem(MenuItem("Office", menu6))
        self.menu.addItem(MenuItem("Help", menu7))

        self.menu.setWidth("100%")

        # add tabs and menu
        self.add(self.menu)
        self.add(self.fTabs)

    def execute(self):
        Window.alert("Thank you for selecting a menu item.")


