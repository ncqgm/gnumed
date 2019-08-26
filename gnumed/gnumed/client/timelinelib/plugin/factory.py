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


from timelinelib.plugin.plugins.eventboxdrawers import EVENTBOX_DRAWER
from timelinelib.plugin.plugins.exporters import EXPORTER
from timelinelib.plugin.plugins.texttransformers import TEXT_TRANSFORMER
from timelinelib.plugin.plugins.eventboxdrawers.defaulteventboxdrawer import DefaultEventBoxDrawer
from timelinelib.plugin.plugins.eventboxdrawers.gradienteventboxdrawer import GradientEventBoxDrawer
from timelinelib.plugin.plugins.eventboxdrawers.othergradienteventboxdrawer import OtherGradientEventBoxDrawer
from timelinelib.plugin.plugins.eventboxdrawers.othergradienteventboxdrawerfuzzyedges import OtherGradientEventBoxDrawerFuzzyEdges
from timelinelib.plugin.plugins.exporters.timelineexporter import TimelineExporter
from timelinelib.plugin.plugins.exporters.exporttosvg import SvgExporter
from timelinelib.plugin.plugins.exporters.exporttolist import ListExporter
from timelinelib.plugin.plugins.exporters.exporttobitmap import BitmapExporter
from timelinelib.plugin.plugins.exporters.exporttobitmaps import MultiBitmapExporter
from timelinelib.plugin.plugins.texttransformers.defaulttexttransformer import DefaultTextTransformer
from timelinelib.plugin.plugins.texttransformers.plaintexttohtml import PlainTextToHtml


VALID_SERVICES = [EVENTBOX_DRAWER, EXPORTER, TEXT_TRANSFORMER]
PLUGINS = {
    EVENTBOX_DRAWER: [
        DefaultEventBoxDrawer(),
        GradientEventBoxDrawer(),
        OtherGradientEventBoxDrawer(),
        OtherGradientEventBoxDrawerFuzzyEdges(),
    ],
    EXPORTER: [
        SvgExporter(),
        ListExporter(),
        BitmapExporter(),
        MultiBitmapExporter(),
        TimelineExporter(),
    ],
    TEXT_TRANSFORMER: [
        DefaultTextTransformer(),
        PlainTextToHtml(),
    ]
}


class PluginException(Exception):
    pass


class PluginFactory(object):

    def get_plugins(self, service):
        try:
            return PLUGINS[service]
        except:
            return []

    def get_plugin(self, service, name):
        try:
            return [plugin for plugin in PLUGINS[service] if str(plugin.display_name().encode('utf-8')) == name][0]
        except:
            pass

