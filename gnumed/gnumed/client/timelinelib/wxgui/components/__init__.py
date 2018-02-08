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


from .categorychoice import CategoryChoice
from .categorytree import CustomCategoryTree
from .colourselect import ColourSelect
from .containerchoice import ContainerChoice
from .dialogbuttonssizers.dialogbuttonsapplyclosesizer import DialogButtonsApplyCloseSizer
from .dialogbuttonssizers.dialogbuttonsclosesizer import DialogButtonsCloseSizer
from .dialogbuttonssizers.dialogbuttonseditaddremoveclosesizer import DialogButtonsEditAddRemoveCloseSizer
from .dialogbuttonssizers.dialogbuttonsokcancelsizer import DialogButtonsOkCancelSizer
from .feedbacktext import FeedbackText
from .filechooser import FileChooser
from .header import Header
from .messagebar import MessageBar
from .propertyeditors.alerteditor import AlertEditor
from .propertyeditors.coloreditor import ColorEditor
from .propertyeditors.descriptioneditor import DescriptionEditor
from .propertyeditors.hyperlinkeditor import HyperlinkEditor
from .propertyeditors.iconeditor import IconEditor
from .propertyeditors.progresseditor import ProgressEditor
from .textctrl import TextCtrl
from .textctrlselect import TextCtrlSelect
from .textpatterncontrol.view import TextPatternControl
from .twostatebutton import TwoStateButton


def TimePicker(parent, time_type, name="", *args, **kwargs):
    return time_type.create_time_picker(parent, *args, **kwargs)


def PeriodPicker(parent, time_type, name="", *args, **kwargs):
    return time_type.create_period_picker(parent, *args, **kwargs)
