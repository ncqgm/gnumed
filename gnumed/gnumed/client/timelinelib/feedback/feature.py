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


from timelinelib.wxgui.dialogs.feedback import show_feedback_dialog


"""
For each entry in the FETURES dictionary a submenu under Help -> Give Feedback on Features,
will be created with the dictionary key as label.
When one of these submenues is selected the function show_feature_feedback_dialog() will
be called with the dictionary key as the feature_name argument.S
"""
FEATURES = { "Vertical &Scrolling" :
             """
             This new feature enables you to scroll the Timeline events vertically.
             You accomplish this by pressing the Ctrl+Shift keys and then scroll the mouse wheel.
             Point events and period events are scrolled in opposite directions and disappear
             from view when they cross the divider line.
             """,
              
             "Vertical &Zooming" :
             """
             This new feature enables you to zoom the Timeline events vertically.
             You accomplish this by pressing the Alt key and then scroll the mouse wheel.
             """,
             
             "E&xporting whole Timeline to images" :
             """
             Now you can export the entire timeline to a series of images.
             Select menu File -> Export Whole Timeline to Image.
             Each image will contain the timespan currently displayed in the Timeline view.
             """,
             
             "&Containers" :
             """
             Containers are a way to group events together.
             In a container events can not overlap, so if you add a new event to a container
             all other events are moved to give room for the new event. The same thing happens
             if you resize an event within the container.
             
             Have a look at this video for a demo. http://www.youtube.com/watch?v=dBwEQ3vqB_I
             """,
               }


class FeatureForm(object):

    def __init__(self, dialog):
        self.dialog = dialog

    def populate(self, subject):
        self.subject = subject
        self.dialog.set_feature_name(subject)
        self.dialog.set_feature_description(FEATURES[subject])

    def give_feedback(self):
        show_feedback_dialog("", self.subject, "")


def show_feature_feedback_dialog(feature_name, parent=None):
    from timelinelib.wxgui.dialogs.feature import FeatureDialog
    dialog = FeatureDialog(parent)
    dialog.controller.populate(feature_name)
    dialog.ShowModal()
    dialog.Destroy()
