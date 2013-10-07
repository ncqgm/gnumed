# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


import os.path
import webbrowser

import wx
import wx.html

from timelinelib.config.paths import HELP_RESOURCES_DIR
from timelinelib.config.paths import ICONS_DIR
from timelinelib.wxgui.utils import display_error_message


class HelpBrowser(wx.Frame):

    HOME_ID = 10
    BACKWARD_ID = 20
    FORWARD_ID = 30

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=_("Help"),
                          size=(600, 550), style=wx.DEFAULT_FRAME_STYLE)
        self.history = []
        self.current_pos = -1
        self._create_help_system()
        self._create_gui()
        self._update_buttons()

    def _create_help_system(self):
        try:
            import markdown
        except ImportError:
            self.help_system = None
        else:
            import timelinelib.help.system as help
            import timelinelib.help.pages as help_pages
            self.help_system = help.HelpSystem(
                "contents", HELP_RESOURCES_DIR + "/", "page:")
            help_pages.install(self.help_system)

    def show_page(self, id, type="page", change_history=True):
        """
        Where which is a tuple (type, id):

          * (page, page_id)
          * (search, search_string)
        """
        if self.help_system is None:
            display_error_message(
                _("Could not find markdown Python package.  It is needed by the help system. See the Timeline website or the doc/installing.rst file for instructions how to install it."),
                self.GetParent())
            return
        if change_history:
            same_page_as_last = False
            if self.current_pos != -1:
                current_type, current_id = self.history[self.current_pos]
                if id == current_id:
                    same_page_as_last = True
            if same_page_as_last == False:
                self.history = self.history[:self.current_pos + 1]
                self.history.append((type, id))
                self.current_pos += 1
        self._update_buttons()
        if type == "page":
            self.html_window.SetPage(self._generate_page(id))
        elif type == "search":
            self.html_window.SetPage(self.help_system.get_search_results_page(id))
        self.Show()
        self.Raise()

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        self.toolbar = self.CreateToolBar()
        size = (24, 24)
        if 'wxMSW' in wx.PlatformInfo:
            home_bmp = wx.Bitmap(os.path.join(ICONS_DIR, "home.png"))
            back_bmp = wx.Bitmap(os.path.join(ICONS_DIR, "backward.png"))
            forward_bmp = wx.Bitmap(os.path.join(ICONS_DIR, "forward.png"))
        else:
            home_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR,
                                                size)
            back_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                                                size)
            forward_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                                   wx.ART_TOOLBAR, size)
        self.toolbar.SetToolBitmapSize(size)
        # Home
        home_str = _("Go to home page")
        self.toolbar.AddLabelTool(HelpBrowser.HOME_ID, home_str,
                                  home_bmp, shortHelp=home_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click, id=HelpBrowser.HOME_ID)
        # Separator
        self.toolbar.AddSeparator()
        # Backward
        backward_str = _("Go back one page")
        self.toolbar.AddLabelTool(HelpBrowser.BACKWARD_ID, backward_str,
                                  back_bmp, shortHelp=backward_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click,
                  id=HelpBrowser.BACKWARD_ID)
        # Forward
        forward_str = _("Go forward one page")
        self.toolbar.AddLabelTool(HelpBrowser.FORWARD_ID, forward_str,
                                  forward_bmp, shortHelp=forward_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click,
                  id=HelpBrowser.FORWARD_ID)
        # Separator
        self.toolbar.AddSeparator()
        # Search
        self.search = wx.SearchCtrl(self.toolbar, size=(150, -1),
                                    style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_on_text_enter, self.search)
        self.toolbar.AddControl(self.search)
        self.toolbar.Realize()
        # Html window
        self.html_window = wx.html.HtmlWindow(self)
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED,
                  self._html_window_on_link_clicked, self.html_window)
        self.html_window.Connect(wx.ID_ANY, wx.ID_ANY, wx.EVT_KEY_DOWN.typeId,
                                 self._window_on_key_down)

    def _window_on_close(self, e):
        self.Show(False)

    def _window_on_key_down(self, evt):
        """
        Event handler used when a keyboard key has been pressed.

        The following keys are handled:
        Key         Action
        --------    ------------------------------------
        Backspace   Go to previous page
        """
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_BACK:
            self._go_back()
        evt.Skip()

    def _toolbar_on_click(self, e):
        if e.GetId() == HelpBrowser.HOME_ID:
            self._go_home()
        elif e.GetId() == HelpBrowser.BACKWARD_ID:
            self._go_back()
        elif e.GetId() == HelpBrowser.FORWARD_ID:
            self._go_forward()

    def _search_on_text_enter(self, e):
        self._search(self.search.GetValue())

    def _html_window_on_link_clicked(self, e):
        url = e.GetLinkInfo().GetHref()
        if url.startswith("page:"):
            self.show_page(url[5:])
        else:
            webbrowser.open(url)

    def _go_home(self):
        self.show_page(self.help_system.home_page)

    def _go_back(self):
        if self.current_pos > 0:
            self.current_pos -= 1
            current_type, current_id = self.history[self.current_pos]
            self.show_page(current_id, type=current_type, change_history=False)

    def _go_forward(self):
        if self.current_pos < len(self.history) - 1:
            self.current_pos += 1
            current_type, current_id = self.history[self.current_pos]
            self.show_page(current_id, type=current_type, change_history=False)

    def _search(self, string):
        self.show_page(string, type="search")

    def _update_buttons(self):
        history_len = len(self.history)
        enable_backward = history_len > 1 and self.current_pos > 0
        enable_forward = history_len > 1 and self.current_pos < history_len - 1
        self.toolbar.EnableTool(HelpBrowser.BACKWARD_ID, enable_backward)
        self.toolbar.EnableTool(HelpBrowser.FORWARD_ID, enable_forward)

    def _generate_page(self, id):
        page = self.help_system.get_page(id)
        if page == None:
            error_page_html = "<h1>%s</h1><p>%s</p>" % (
                _("Page not found"),
                _("Could not find page '%s'.") % id)
            return self._wrap_in_html(error_page_html)
        else:
            return self._wrap_in_html(page.render_to_html())

    def _wrap_in_html(self, content):
        HTML_SKELETON = """
        <html>
        <head>
        </head>
        <body>
        %s
        </body>
        </html>
        """
        return HTML_SKELETON % content
