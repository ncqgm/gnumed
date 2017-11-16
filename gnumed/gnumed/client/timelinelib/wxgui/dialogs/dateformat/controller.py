# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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


import locale
import datetime

from timelinelib.config.dateformatparser import DateFormatParser
from timelinelib.wxgui.framework import Controller


class DateFormatDialogController(Controller):

    def on_init(self, config):
        self.config = config
        self.view.SetDateFormat(config.get_date_format())
        self.view.SetLocaleDateFormat(self._create_locale_sample_date())
        self.dateformat_parser = DateFormatParser()

    def on_ok(self, event):
        date_format = self.view.GetDateFormat()
        if self._is_valid_format(date_format):
            self.config.set_date_format(date_format)
            self.view.EndModalOk()
        else:
            self.view.DisplayErrorMessage(self.dateformat_parser.get_error_text())

    def _is_valid_format(self, date_format):
        return self.dateformat_parser.is_valid(date_format)

    def _create_locale_sample_date(self):
        locale.setlocale(locale.LC_TIME, "")
        sample = datetime.datetime(3333, 11, 22).strftime('%x')
        sample = sample.replace("3", "y")
        sample = sample.replace("2", "d")
        sample = sample.replace("1", "m")
        return sample
