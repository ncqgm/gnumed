# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
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

Used by HelpBrowserFrame in GUI.

Usage:

    help_system = HelpPageRepository(...)
    help_system.install_page(...)
    help_system.install_page(...)
    help_system.install_page(...)
    page = help_system.get_page(id)
    html = page.render_to_html()
"""


import re
from markdown import markdown


class HelpPageRepository(object):

    def __init__(self, home_page, help_resources_root_dir, page_prefix):
        self.help_pages = {}
        self.home_page = home_page
        self.help_resources_root_dir = help_resources_root_dir
        self.page_prefix = page_prefix

    def install_page(self, page_id, header, body, related_pages=[]):
        self.help_pages[page_id] = HelpPage(self, page_id, header, body, related_pages)

    def get_page(self, page_id):
        return self.help_pages.get(page_id, None)

    def get_search_results_page(self, target_words):
        found_pages = self._find_pages(target_words)
        return self._render_search_result_page(target_words, found_pages)

    def _render_search_result_page(self, target_words, found_pages):
        tex = ""
        tex += "<ul>"
        for page in found_pages:
            tex += "<li>"
            tex += "<a href=\"%s%s\">%s</a>" % (self.page_prefix, page.page_id, page.header)
            tex += "</li>"
        tex += "</ul>"
        search_page_html = "<h1>%s</h1>%s" % (
            _("Search results for '%s'") % target_words,
            tex)
        return search_page_html

    def _find_pages(self, target_words):
        search_words = [r"\b%s\b" % x for x in target_words.split()]
        pages = []
        for help_page in self.help_pages.values():
            match = True
            for search_word in search_words:
                if (not re.search(search_word, help_page.header, re.IGNORECASE) and
                   not re.search(search_word, help_page.body, re.IGNORECASE)):
                    match = False
                    break
            if match:
                pages.append(help_page)
        return pages


class HelpPage(object):

    def __init__(self, help_page_repository, page_id, header, body, related_pages):
        self.help_page_repository = help_page_repository
        self.page_id = page_id
        self.header = header
        self.body = body
        self.related_pages = related_pages

    def render_to_html(self):
        html = "<h1>%s</h1>%s" % (self.header, markdown(self.body))
        # Change headers
        html = self._replace_help_placeholder_with_proper_link(html)
        html = self._replace_helpfigure_placeholder_with_proper_image(html)
        html = self._render_related_pages(html)
        return html

    def _replace_help_placeholder_with_proper_link(self, html):
        # Our link markup: Replace Help(foo) with proper link
        while True:
            match = re.search(r"Help\(([^)]+)\)", html)
            if match:
                page = self.help_page_repository.get_page(match.group(1))
                replacement = "??"
                if page:
                    replacement = "<a href=\"%s%s\">%s</a>" % (
                        self.help_page_repository.page_prefix,
                        match.group(1), page.header)
                html = html[0:match.start(0)] + replacement + html[match.end(0):]
            else:
                break
        return html

    def _replace_helpfigure_placeholder_with_proper_image(self, html):
        # Our link markup: Replace HelpFigure(foo) with proper image
        while True:
            match = re.search(r"HelpFigure\(([^)]+)\)", html)
            if match:
                replacement = "<img src=\"%s%s.png\" border=\"0\">" % (
                    self.help_page_repository.resources_prefix, match.group(1))
                html = html[0:match.start(0)] + replacement + html[match.end(0):]
            else:
                break
        return html

    def _render_related_pages(self, html):
        if self.related_pages:
            related_pages_html = "<h2>%s</h2>" % _("Related pages")
            related_pages_html += "<ul>"
            for page_id in self.related_pages:
                page = self.help_page_repository.get_page(page_id)
                if page:
                    related_pages_html += "<li>"
                    related_pages_html += "<a href=\"%s%s\">%s</a>" % (
                        self.help_page_repository.page_prefix, page.page_id, page.header)
                    related_pages_html += "</li>"
            related_pages_html += "</ul>"
            html = html + related_pages_html
        return html
