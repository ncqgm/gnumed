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


import sys
import re

import wx

from timelinelib.calendar.monthnames import abbreviated_name_of_month
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import time_period_center
from timelinelib.drawing.interface import Strip
from timelinelib.drawing.utils import get_default_font
from timelinelib.time.typeinterface import TimeType


# To save computation power (used by `delta_to_microseconds`)
US_PER_SEC = 1000000
US_PER_HOUR = 60 * 60 * 1000 * 1000
US_PER_MINUTE = 60 * 1000 * 1000
US_PER_DAY = 24 * 60 * 60 * US_PER_SEC
MIN_YEAR = -4700
MAX_YEAR = 120000

class WxTimeType(TimeType):

    def __eq__(self, other):
        return isinstance(other, WxTimeType)

    def __ne__(self, other):
        return not (self == other)

    def time_string(self, time):
        return time.Format("%Y-%m-%d %H:%M:%S")

    def parse_time(self, time_string):
        match = re.search(r"^(-?\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$", time_string)
        if match:
            year = int(match.group(1))
            month = int(match.group(2)) - 1
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            return try_to_create_wx_date_time_from_dmy(day, month, year, hour, minute, second)
        else:
            raise ValueError("Time not on correct format = '%s'" % time_string)

    def get_navigation_functions(self):
        return [
            (_("Go to &Today\tCtrl+T"), go_to_today_fn),
            (_("Go to D&ate...\tCtrl+G"), go_to_date_fn),
            ("SEP", None),
            (_("Backward\tPgUp"), backward_fn),
            (_("Forward\tPgDn"), forward_fn),
            (_("Forward One Wee&k\tCtrl+K"), forward_one_week_fn),
            (_("Back One &Week\tCtrl+W"), backward_one_week_fn),
            (_("Forward One Mont&h\tCtrl+h"), forward_one_month_fn),
            (_("Back One &Month\tCtrl+M"), backward_one_month_fn),
            (_("Forward One Yea&r\tCtrl+R"), forward_one_year_fn),
            (_("Back One &Year\tCtrl+Y"), backward_one_year_fn),
            ("SEP", None),
            (_("Fit Millennium"), fit_millennium_fn),
            (_("Fit Century"), fit_century_fn),
            (_("Fit Decade"), fit_decade_fn),
            (_("Fit Year"), fit_year_fn),
            (_("Fit Month"), fit_month_fn),
            (_("Fit Week"), fit_week_fn),
            (_("Fit Day"), fit_day_fn),
        ]

    def is_date_time_type(self):
        return True

    def format_period(self, time_period):
        """Returns a unicode string describing the time period."""
        def label_with_time(time):
            return u"%s %s" % (label_without_time(time), time_label(time))
        def label_without_time(time):
            return "%s %s %s" % (
                time.Format("%d"),
                abbreviated_name_of_month(int(time.Format("%m"))),
                time.Format("%Y"))
        def time_label(time):
            return time.Format("%H:%M")
        if time_period.is_period():
            if time_period.has_nonzero_time():
                label = u"%s to %s" % (label_with_time(time_period.start_time),
                                      label_with_time(time_period.end_time))
            else:
                label = u"%s to %s" % (label_without_time(time_period.start_time),
                                      label_without_time(time_period.end_time))
        else:
            if time_period.has_nonzero_time():
                label = u"%s" % label_with_time(time_period.start_time)
            else:
                label = u"%s" % label_without_time(time_period.start_time)
        return label

    def format_delta(self, delta):
        days = delta.days
        hours = delta.hours - days * 24
        minutes = delta.minutes - (days * 24 + hours) * 60
        collector = []
        if days == 1:
            collector.append(u"1 %s" % _("day"))
        elif days > 1:
            collector.append(u"%d %s" % (days, _("days")))
        if hours == 1:
            collector.append(u"1 %s" % _("hour"))
        elif hours > 1:
            collector.append(u"%d %s" % (hours, _("hours")))
        if minutes == 1:
            collector.append(u"1 %s" % _("minute"))
        elif minutes > 1:
            collector.append(u"%d %s" % (minutes, _("minutes")))
        delta_string = u" ".join(collector)
        if delta_string == "":
            delta_string = "0"
        return delta_string

    def get_min_time(self):
        min_time = wx.DateTimeFromDMY(1, 0, MIN_YEAR)
        return (min_time, _("can't be before year %d") % (MIN_YEAR))

    def get_max_time(self):
        max_time = wx.DateTimeFromDMY(1, 0, MAX_YEAR)
        return (max_time, _("can't be after year %d") % (MAX_YEAR))

    def choose_strip(self, metrics, config):
        """
        Return a tuple (major_strip, minor_strip) for current time period and
        window size.
        """
        today = metrics.time_period.start_time
        tomorrow = today + wx.DateSpan.Day()
        day_period = TimePeriod(self, today, tomorrow)
        one_day_width = metrics.calc_exact_width(day_period)
        if one_day_width > 600:
            return (StripDay(), StripHour())
        elif one_day_width > 45:
            return (StripWeek(config), StripWeekday())
        elif one_day_width > 25:
            return (StripMonth(), StripDay())
        elif one_day_width > 1.5:
            return (StripYear(), StripMonth())
        elif one_day_width > 0.12:
            return (StripDecade(), StripYear())
        elif one_day_width > 0.012:
            return (StripCentury(), StripDecade())
        else:
            return (StripCentury(), StripCentury())

    def mult_timedelta(self, delta, num):
        """Return a new timedelta that is `num` times larger than `delta`."""
        microsecs = delta_to_microseconds(delta) * num
        delta = microseconds_to_delta(microsecs)
        return delta

    def get_default_time_period(self):
        return time_period_center(self, wx.DateTime.Now(), wx.TimeSpan.Days(30))

    def now(self):
        return wx.DateTime.Now()

    def get_time_at_x(self, time_period, x_percent_of_width):
        """Return the time at pixel `x`."""
        microsecs = delta_to_microseconds(time_period.delta())
        microsecs = microsecs * x_percent_of_width
        return time_period.start_time + microseconds_to_delta(microsecs)

    def div_timedeltas(self, delta1, delta2):
        """Return how many times delta2 fit in delta1."""
        # Since Python can handle infinitely large numbers, this solution works. It
        # might however not be optimal. If you are clever, you should be able to
        # treat the different parts individually. But this is simple.
        total_us1 = delta_to_microseconds(delta1)
        total_us2 = delta_to_microseconds(delta2)
        # Make sure that the result is a floating point number
        return float(total_us1) / float(total_us2)

    def get_max_zoom_delta(self):
        max_zoom_delta = wx.TimeSpan.Days(1200 * 365)
        return (max_zoom_delta, _("Can't zoom wider than 1200 years"))

    def get_min_zoom_delta(self):
        return (wx.TimeSpan.Hour(), _("Can't zoom deeper than 1 hour"))

    def get_zero_delta(self):
        return wx.TimeSpan()

    def time_period_has_nonzero_time(self, time_period):
        nonzero_time = (not time_period.start_time.IsSameTime(wx.DateTimeFromHMS(0, 0, 0))  or
                        not time_period.end_time.IsSameTime(wx.DateTimeFromHMS(0, 0, 0))    )
        return nonzero_time

    def get_name(self):
        return u"wxtime"

    def get_duplicate_functions(self):
        return [
            (_("Day"), move_period_num_days),
            (_("Week"), move_period_num_weeks),
            (_("Month"), move_period_num_months),
            (_("Year"), move_period_num_years),
        ]

    def zoom_is_ok(self, delta):
        return (delta.GetMilliseconds() > 3600000) or (delta.GetDays() > 0)

    def half_delta(self, delta):
        microseconds = delta_to_microseconds(delta) / 2
        return microseconds_to_delta(microseconds)

    def margin_delta(self, delta):
        microseconds = delta_to_microseconds(delta) / 24
        return microseconds_to_delta(microseconds)

    def event_date_string(self, time):
        return time.Format("%Y-%m-%d")

    def event_time_string(self, time):
        return time.Format("%H:%M")

    def eventtimes_equals(self, time1, time2):
        s1 = "%s %s" % (self.event_date_string(time1),
                        self.event_date_string(time1))
        s2 = "%s %s" % (self.event_date_string(time2),
                        self.event_date_string(time2))
        return s1 == s2

    def adjust_for_bc_years(self, time):
        if time.Year == 0:
            return time  + wx.DateSpan.Year()
        else:
            return time


def go_to_today_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.center(wx.DateTime.Now()))


def go_to_date_fn(main_frame, current_period, navigation_fn):
    def navigate_to(time):
        navigation_fn(lambda tp: tp.center(time))
    main_frame.display_time_editor_dialog(
        WxTimeType(), current_period.mean_time(), navigate_to, _("Go to Date"))


def backward_fn(main_frame, current_period, navigation_fn):
    move_page_smart(current_period, navigation_fn, -1)


def forward_fn(main_frame, current_period, navigation_fn):
    move_page_smart(current_period, navigation_fn, 1)


def move_page_smart(current_period, navigation_fn, direction):
    start, end = current_period.start_time, current_period.end_time
    year_diff = end.Year - start.Year
    start_months = start.Year * 12 + start.Month
    end_months = end.Year * 12 + end.Month
    month_diff = end_months - start_months
    whole_years = start.Month == end.Month and start.Day == end.Day
    whole_months = start.Day == 1 and end.Day == 1
    direction_backward = direction < 0
    # Whole years
    if whole_years and year_diff > 0:
        _move_smart_year(navigation_fn, direction, start, end)
    # Whole months
    elif whole_months and month_diff > 0:
        _move_smart_month(navigation_fn, direction_backward, start, end)
    # No need for smart delta
    else:
        navigation_fn(lambda tp: tp.move_delta(direction*current_period.delta()))


def _move_smart_year(navigation_fn, direction, start, end):
    year_diff = direction * (end.Year - start.Year)
    start.SetYear(start.Year + year_diff)
    end.SetYear(end.Year + year_diff)
    navigation_fn(lambda tp: tp.update(start, end))


def _months_to_year_and_month(months):
    years = int(months / 12)
    month = months - years * 12
    if month == 12:
        month = 0
        years -=1
    return years, month


def _move_smart_month(navigation_fn, direction_backward, start, end):
    if direction_backward:
        _move_smart_month_backward(navigation_fn, start, end)
    else:
        _move_smart_month_forward(navigation_fn, start, end)


def _move_smart_month_backward(navigation_fn, start, end):
    start_months = start.Year * 12 + start.Month
    end_months = end.Year * 12 + end.Month
    month_diff = end_months - start_months
    new_end = start
    new_start_year, new_start_month = _months_to_year_and_month(
                                            start_months -
                                            month_diff)
    new_start = wx.DateTimeFromDMY(start.Day, new_start_month, new_start_year,
                                   start.Hour, start.Minute, start.Second)
    navigation_fn(lambda tp: tp.update(new_start, new_end))


def _move_smart_month_forward(navigation_fn, start, end):
    start_months = start.Year * 12 + start.Month
    end_months = end.Year * 12 + end.Month
    month_diff = end_months - start_months
    new_start = end
    new_end_year, new_end_month = _months_to_year_and_month(
                                            end_months +
                                            month_diff)
    new_end = wx.DateTimeFromDMY(end.Day, new_end_month, new_end_year,
                                 end.Hour, end.Minute, end.Second)
    navigation_fn(lambda tp: tp.update(new_start, new_end))


def forward_one_week_fn(main_frame, current_period, navigation_fn):
    week = wx.DateSpan.Week()
    navigation_fn(lambda tp: tp.move_delta(week))


def backward_one_week_fn(main_frame, current_period, navigation_fn):
    week = wx.DateSpan.Week()
    navigation_fn(lambda tp: tp.move_delta(-1 * week))


def navigate_month_step(current_period, navigation_fn, direction):
    """
    Currently does not notice leap years.
    """
    tm = current_period.mean_time()
    if direction > 0:
        if tm.Month == 1:
            d = 28
        elif tm.Month in (3,5,8,10):
            d = 30
        else:
            d = 31
    else:
        if tm.Month == 2:
            d = 28
        elif tm.Month in (4,6,9,11):
            d = 30
        else:
            d = 31
    mv = wx.DateSpan.Days(d)
    navigation_fn(lambda tp: tp.move_delta(direction*mv))


def forward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, 1)


def backward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, -1)


def forward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = wx.DateSpan.Year()
    navigation_fn(lambda tp: tp.move_delta(yr))


def backward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = wx.DateSpan.Year()
    navigation_fn(lambda tp: tp.move_delta(-1*yr))


def fit_millennium_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(1, 0, int(mean.Year/1000)*1000)
    end = wx.DateTimeFromDMY(1, 0, int(mean.Year/1000)*1000 + 1000)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_century_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(1, 0, int(mean.Year/100)*100)
    end = wx.DateTimeFromDMY(1, 0, int(mean.Year/100)*100 + 100)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_decade_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(1, 0, int(mean.Year/10)*10)
    end = wx.DateTimeFromDMY(1, 0, int(mean.Year/10)*10+10)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_year_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(1, 0, mean.Year)
    end = wx.DateTimeFromDMY(1, 0, mean.Year + 1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_month_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(1, mean.Month, mean.Year)
    if mean.Month == 11:
        end = wx.DateTimeFromDMY(1, 0, mean.Year + 1)
    else:
        end = wx.DateTimeFromDMY(1, mean.Month + 1, mean.Year)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_day_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(mean.Day, mean.Month, mean.Year)
    end = start + wx.DateSpan.Day()
    navigation_fn(lambda tp: tp.update(start, end))


def fit_week_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = wx.DateTimeFromDMY(mean.Day, mean.Month, mean.Year)
    start.SetToWeekDayInSameWeek(1)
    if not main_frame.week_starts_on_monday():
        start = start - wx.DateSpan.Day()
    end = start + wx.DateSpan.Days(7)
    navigation_fn(lambda tp: tp.update(start, end))

  
class StripCentury(Strip):

    def label(self, time, major=False):
        if major:
            # TODO: This only works for English. Possible to localize?
            start_year = self._century_start_year(time.Year)
            next_start_year = start_year + 100
            return str(next_start_year / 100) + " century"
        return ""

    def start(self, time):
        return wx.DateTimeFromDMY(1, 0, max(self._century_start_year(time.Year), MIN_YEAR))

    def increment(self, time):
        return time + wx.DateSpan.Years(100)

    def get_font(self, time_period):
        return get_default_font(8)

    def _century_start_year(self, year):
        return (int(year) / 100) * 100


class StripDecade(Strip):

    def label(self, time, major=False):
        # TODO: This only works for English. Possible to localize?
        return str(self._decade_start_year(time.Year)) + "s"

    def start(self, time):
        return wx.DateTimeFromDMY(1, 0, self._decade_start_year(time.Year))

    def increment(self, time):
        return time + wx.DateSpan.Year() * 10

    def _decade_start_year(self, year):
        return (int(year) / 10) * 10

    def get_font(self, time_period):
        return get_default_font(8)


class StripYear(Strip):

    def label(self, time, major=False):
        return str(wx.DateTime.ConvertYearToBC(time.Year))

    def start(self, time):
        return wx.DateTimeFromDMY(1, 0, time.Year)

    def increment(self, time):
        return time + wx.DateSpan.Year()

    def get_font(self, time_period):
        return get_default_font(8)


class StripMonth(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s" % (time.GetMonthName(time.Month, time.Name_Abbr), time.Year)
        return time.GetMonthName(time.Month, wx.DateTime.Name_Abbr)

    def start(self, time):
        return wx.DateTimeFromDMY(1, time.Month, time.Year)

    def increment(self, time):
        if time.Month < 11:
            return wx.DateTimeFromDMY(1, time.Month + 1, time.Year, 0, 0)
        else:
            return wx.DateTimeFromDMY(1, 0, time.Year + 1, 0, 0)

    def get_font(self, time_period):
        return get_default_font(8)


class StripDay(Strip):

    def label(self, time, major=False):
        if major:
            month_name = time.GetMonthName(time.Month, time.Name_Abbr)
            return "%s %s %s" % (time.Day, month_name, time.Year)
        return str(time.Day)

    def start(self, time):
        return wx.DateTimeFromDMY(time.Day, time.Month, time.Year)

    def increment(self, time):
        return time + wx.DateSpan.Day()

    def get_font(self, time_period):
        saturday_or_sunday = (0,6)
        bold = False
        if (time_period.start_time.GetWeekDay() in saturday_or_sunday):
            bold = True
        return get_default_font(8, bold)


class StripWeek(Strip):

    def __init__(self, config):
        Strip.__init__(self)
        self.config = config

    def label(self, time, major=False):
        if major:
            # Example: Week 23 (1-7 Jan 2009)
            first_weekday = self.start(time)
            next_first_weekday = self.increment(first_weekday)
            last_weekday = next_first_weekday - wx.DateSpan.Day()
            range_string = self._time_range_string(first_weekday, last_weekday)
            if self.config.week_start == "monday":
                return (_("Week") + " %s (%s)") % (time.GetWeekOfYear(), range_string)
            else:
                # It is sunday (don't know what to do about week numbers here)
                return range_string
        # This strip should never be used as minor
        return ""

    def start(self, time):
        stripped_date = wx.DateTimeFromDMY(time.Day, time.Month, time.Year)
        if self.config.week_start == "monday":
            days_to_subtract = stripped_date.GetWeekDay() - 1
        else: # It is sunday
            days_to_subtract = stripped_date.GetWeekDay() % 7
        return stripped_date - wx.DateSpan.Days(days_to_subtract)

    def increment(self, time):
        return time + wx.DateSpan.Week()

    def get_font(self, time_period):
        return get_default_font(8)

    def _time_range_string(self, time1, time2):
        """
        Examples:

        * 1-7 Jun 2009
        * 28 Jun-3 Jul 2009
        * 28 Jun 08-3 Jul 2009
        """
        if time1.Year == time2.Year:
            if time1.Month == time2.Month:
                return "%s-%s %s %s" % (time1.Day, time2.Day,
                                        time1.GetMonthName(time1.Month, time1.Name_Abbr),
                                        time1.Year)
            return "%s %s-%s %s %s" % (time1.Day,
                                       time1.GetMonthName(time1.Month, time1.Name_Abbr),
                                       time2.Day,
                                       time2.GetMonthName(time2.Month, time2.Name_Abbr),
                                       time1.Year)
        return "%s %s %s-%s %s %s" % (time1.Day,
                                      time1.GetMonthName(time1.Month, time1.Name_Abbr),
                                      time1.Year,
                                      time2.Day,
                                      time2.GetMonthName(time2.Month, time2.Name_Abbr),
                                      time2.Year)


class StripWeekday(Strip):

    def label(self, time, major=False):
        if major:
            # This strip should never be used as major
            return ""
        return time.GetWeekDayName(time.GetWeekDay(), wx.DateTime.Name_Abbr)

    def start(self, time):
        return wx.DateTimeFromDMY(time.Day, time.Month, time.Year)

    def increment(self, time):
        return time + wx.DateSpan.Day()

    def get_font(self, time_period):
        return get_default_font(8)


class StripHour(Strip):

    def label(self, time, major=False):
        if major:
            # This strip should never be used as major
            return ""
        return str(time.Hour)

    def start(self, time):
        start_time = wx.DateTimeFromDMY(time.Day, time.Month, time.Year, time.Hour)
        return start_time

    def increment(self, time):
        new_time = time + wx.TimeSpan.Hour()
        return new_time

    def get_font(self, time_period):
        return get_default_font(8)


def microseconds_to_delta(microsecs):
    # The wx.TimeSpan.Milliseconds(ms) take a wxLong argument instead
    # of the expected wxLonLong. And that's why we can't code like
    #     ms = delta.GetMilliseconds() / 2
    #     return wx.TimeSpan.Milliseconds(ms)
    counter = 0
    milliseconds = microsecs / 1000
    while abs(milliseconds) > sys.maxint:
        milliseconds = milliseconds / 2
        counter += 1
    delta = wx.TimeSpan.Milliseconds(milliseconds)
    while counter > 0:
        delta = delta * 2;
        counter -= 1
    return delta


def delta_to_microseconds(delta):
    """Return the number of microseconds that the delta represents."""
    days = delta.GetDays()
    hours = delta.GetHours()
    minutes = delta.GetMinutes()
    seconds = delta.GetSeconds()
    milliseconds = delta.GetMilliseconds()
    neg = False
    if days < 0:
        neg = True
        days  = -days
        hours = -hours
        minutes = -minutes
        seconds = -seconds
        milliseconds = - milliseconds
    microsecs = days * US_PER_DAY
    if hours >= 0:
        microsecs = hours * US_PER_HOUR
        if minutes >= 0:
            microsecs = minutes * US_PER_MINUTE
            if seconds >= 0:
                microsecs = seconds * US_PER_SEC
                if milliseconds >= 0:
                    microsecs = milliseconds * 1000
    if neg:
        microsecs = -microsecs
    return microsecs


def move_period_num_days(period, num):
    return _move_period_time_span(period, wx.TimeSpan.Days(num))


def move_period_num_weeks(period, num):
    return _move_period_time_span(period, wx.TimeSpan.Days(7*num))


def move_period_num_months(period, num):
    new_start_time = period.start_time + wx.DateSpan.Months(num)
    if new_start_time.Day != period.start_time.Day:
        return None
    return _move_period_time_span(period, new_start_time-period.start_time)


def move_period_num_years(period, num):
    new_start_time = period.start_time + wx.DateSpan.Years(num)
    if (new_start_time.Month != period.start_time.Month or
        new_start_time.Day != period.start_time.Day):
        return None
    return _move_period_time_span(period, new_start_time-period.start_time)


def _move_period_time_span(period, time_span):
    try:
        new_start = period.start_time + time_span
        new_end = period.end_time + time_span
        return TimePeriod(period.time_type, new_start, new_end)
    except ValueError:
        return None


def try_to_create_wx_date_time_from_dmy(day, month, year, hour=0, minute=0, second=0):
    def fail_with_invalid_date():
        raise ValueError("Invalid date")
    try:
        datetime = wx.DateTimeFromDMY(day, month, year, hour, minute, second)
    except AssertionError:
        fail_with_invalid_date()
    else:
        if not datetime.IsValid():
            fail_with_invalid_date()
        return datetime

