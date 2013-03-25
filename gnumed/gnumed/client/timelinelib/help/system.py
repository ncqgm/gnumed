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


"""
A wiki-like help system.

Used by HelpBrowser in GUI.

Usage:

    help_system = HelpSystem(...)
    help_system.install_page(...)
    help_system.install_page(...)
    help_system.install_page(...)
    page = help_system.get_page(id)
    html = page.render_to_html()
"""


import re
from markdown import markdown


class HelpSystem(object):

    def __init__(self, home_page, resources_prefix, page_prefix):
        self.pages = {}
        self.home_page = home_page
        self.resources_prefix = resources_prefix
        self.page_prefix = page_prefix

    def install_page(self, id, header="", body="", related_pages=[]):
        self.pages[id] = HelpPage(self, id, header, body, related_pages)

    def get_page(self, id):
        return self.pages.get(id, None)

    def get_search_results_page(self, search):
        matches = self._get_pages_matching_search(search)
        # search
        tex = ""
        tex += "<ul>"
        for page in matches:
            tex += "<li>"
            tex += "<a href=\"%s%s\">%s</a>" % (self.page_prefix, page.id, page.header)
            tex += "</li>"
        tex += "</ul>"
        search_page_html = "<h1>%s</h1>%s" % (
            _("Search results for '%s'") % search,
            tex)
        return search_page_html

    def _get_pages_matching_search(self, search):
        search_words = search.split(" ")
        content_res = [r"\b%s\b" % x for x in search_words]
        matches = []
        for page in self.pages.values():
            match = True
            for content_re in content_res:
                if (not re.search(content_re, page.header, re.IGNORECASE) and
                    not re.search(content_re, page.body, re.IGNORECASE)):
                    match = False
                    break
            if match:
                matches.append(page)
        return matches


class HelpPage(object):

    def __init__(self, help_system, id, header, body, related_pages):
        self.help_system = help_system
        self.id = id
        self.header = header
        self.body = body
        self.related_pages = related_pages

    def render_to_html(self):
        html = u"<h1>%s</h1>%s" % (self.header, markdown(self.body))
        # Change headers
        # Our link markup: Replace Help(foo) with proper link
        while True:
            match = re.search(r"Help\(([^)]+)\)", html)
            if match:
                page = self.help_system.get_page(match.group(1))
                replacement = "??"
                if page:
                    replacement = "<a href=\"%s%s\">%s</a>" % (
                        self.help_system.page_prefix,
                        match.group(1), page.header)
                html = html[0:match.start(0)] + replacement + \
                       html[match.end(0):]
            else:
                break
        # Our link markup: Replace HelpFigure(foo) with proper image
        while True:
            match = re.search(r"HelpFigure\(([^)]+)\)", html)
            if match:
                replacement = "<img src=\"%s%s.png\" border=\"0\">" % (
                    self.help_system.resources_prefix, match.group(1))
                html = html[0:match.start(0)] + replacement + \
                       html[match.end(0):]
            else:
                break
        # Related pages
        if self.related_pages:
            related_pages_html = "<h2>%s</h2>" % _("Related pages")
            related_pages_html += "<ul>"
            for page_id in self.related_pages:
                page = self.help_system.get_page(page_id)
                if page:
                    related_pages_html += "<li>"
                    related_pages_html += "<a href=\"%s%s\">%s</a>" % (
                        self.help_system.page_prefix, page.id, page.header)
                    related_pages_html += "</li>"
            related_pages_html += "</ul>"
            html = html + related_pages_html
        return html
