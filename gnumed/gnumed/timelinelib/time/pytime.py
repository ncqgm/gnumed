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


from datetime import datetime
from datetime import time
from datetime import timedelta
import calendar
import re

from timelinelib.calendar.monthnames import abbreviated_name_of_month
from timelinelib.calendar.weekdaynames import abbreviated_name_of_weekday
from timelinelib.db.objects import TimeOutOfRangeLeftError
from timelinelib.db.objects import TimeOutOfRangeRightError
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import time_period_center
from timelinelib.drawing.interface import Strip
from timelinelib.drawing.utils import get_default_font
from timelinelib.time.typeinterface import TimeType


# To save computation power (used by `delta_to_microseconds`)
US_PER_SEC = 1000000
US_PER_DAY = 24 * 60 * 60 * US_PER_SEC


class PyTimeType(TimeType):

    def __eq__(self, other):
        return isinstance(other, PyTimeType)

    def __ne__(self, other):
        return not (self == other)

    def time_string(self, time):
        return "%s-%s-%s %s:%s:%s" % (time.year, time.month, time.day,
                                      time.hour, time.minute, time.second)

    def parse_time(self, time_string):
        match = re.search(r"^(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$", time_string)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            try:
                return datetime(year, month, day, hour, minute, second)
            except ValueError:
                raise ValueError("Invalid time, time string = '%s'" % time_string)
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
            return u"%s %s %s" % (time.day, abbreviated_name_of_month(time.month), time.year)
        def time_label(time):
            return time.time().isoformat()[0:5]
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
        hours = delta.seconds / 3600
        minutes = (delta.seconds - hours * 3600) / 60
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
        min_time = datetime(10, 1, 1)
        return (min_time, _("can't be before year 10"))

    def get_max_time(self):
        max_time = datetime(9990, 1, 1)
        return (max_time, _("can't be after year 9989"))

    def choose_strip(self, metrics, config):
        """
        Return a tuple (major_strip, minor_strip) for current time period and
        window size.
        """
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
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
        days = delta.days * num
        seconds = delta.seconds * num
        microseconds = delta.microseconds * num
        return timedelta(days, seconds, microseconds)

    def get_default_time_period(self):
        return time_period_center(self, datetime.now(), timedelta(days=30))

    def now(self):
        return datetime.now()

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
        return total_us1 / float(total_us2)

    def get_max_zoom_delta(self):
        return (timedelta(days=1200*365),
                _("Can't zoom wider than 1200 years"))

    def get_min_zoom_delta(self):
        return (timedelta(hours=1), _("Can't zoom deeper than 1 hour"))

    def get_zero_delta(self):
        return timedelta(0)

    def time_period_has_nonzero_time(self, time_period):
        nonzero_time = (time_period.start_time.time() != time(0, 0, 0) or
                        time_period.end_time.time()   != time(0, 0, 0))
        return nonzero_time

    def get_name(self):
        return u"pytime"

    def get_duplicate_functions(self):
        return [
            (_("Day"), move_period_num_days),
            (_("Week"), move_period_num_weeks),
            (_("Month"), move_period_num_months),
            (_("Year"), move_period_num_years),
        ]

    def zoom_is_ok(self, delta):
        return (delta.seconds > 3600) or (delta.days > 0)

    def half_delta(self, delta):
        return delta / 2

    def margin_delta(self, delta):
        return delta / 24

    def event_date_string(self, time):
        return "%04d-%02d-%02d" % (time.year, time.month, time.day)

    def event_time_string(self, time):
        return "%02d:%02d" % (time.hour, time.minute)

    def eventtimes_equals(self, time1, time2):
        s1 = "%s %s" % (self.event_date_string(time1),
                        self.event_date_string(time1))
        s2 = "%s %s" % (self.event_date_string(time2),
                        self.event_date_string(time2))
        return s1 == s2

    def adjust_for_bc_years(self, time):
        return time

def go_to_today_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.center(datetime.now()))


def go_to_date_fn(main_frame, current_period, navigation_fn):
    def navigate_to(time):
        navigation_fn(lambda tp: tp.center(time))
    main_frame.display_time_editor_dialog(
        PyTimeType(), current_period.mean_time(), navigate_to, _("Go to Date"))


def backward_fn(main_frame, current_period, navigation_fn):
    _move_page_smart(current_period, navigation_fn, -1)


def forward_fn(main_frame, current_period, navigation_fn):
    _move_page_smart(current_period, navigation_fn, 1)


def _move_page_smart(current_period, navigation_fn, direction):
    if _whole_number_of_years(current_period):
        _move_page_years(current_period, navigation_fn, direction)
    elif _whole_number_of_months(current_period):
        _move_page_months(current_period, navigation_fn, direction)
    else:
        navigation_fn(lambda tp: tp.move_delta(direction*current_period.delta()))


def _whole_number_of_years(period):
    start, end = period.start_time, period.end_time
    year_diff = _calculate_year_diff(period)
    whole_years = start.replace(year=start.year+year_diff) == end
    return whole_years and year_diff > 0


def _move_page_years(curret_period, navigation_fn, direction):
    def navigate(tp):
        year_delta = direction * _calculate_year_diff(curret_period)
        new_start_year = curret_period.start_time.year + year_delta
        new_end_year = curret_period.end_time.year + year_delta
        try:
            new_start = curret_period.start_time.replace(year=new_start_year)
            new_end = curret_period.end_time.replace(year=new_end_year)
        except ValueError:
            if direction < 0:
                raise TimeOutOfRangeLeftError()
            else:
                raise TimeOutOfRangeRightError()
        return tp.update(new_start, new_end)
    navigation_fn(navigate)


def _calculate_year_diff(period):
    return period.end_time.year - period.start_time.year


def _whole_number_of_months(period):
    start, end = period.start_time, period.end_time
    start_months = start.year * 12 + start.month
    end_months = end.year * 12 + end.month
    month_diff = end_months - start_months
    whole_months = start.day == 1 and end.day == 1
    return whole_months and month_diff > 0


def _move_page_months(curret_period, navigation_fn, direction):
    def navigate(tp):
        start_months = curret_period.start_time.year * 12 + curret_period.start_time.month
        end_months = curret_period.end_time.year * 12 + curret_period.end_time.month
        month_diff = end_months - start_months
        month_delta = month_diff * direction
        new_start_year, new_start_month = _months_to_year_and_month(start_months + month_delta)
        new_end_year, new_end_month = _months_to_year_and_month(end_months + month_delta)
        try:
            new_start = curret_period.start_time.replace(year=new_start_year, month=new_start_month)
            new_end = curret_period.end_time.replace(year=new_end_year, month=new_end_month)
        except ValueError:
            if direction < 0:
                raise TimeOutOfRangeLeftError()
            else:
                raise TimeOutOfRangeRightError()
        return tp.update(new_start, new_end)
    navigation_fn(navigate)


def _months_to_year_and_month(months):
    years = int(months / 12)
    month = months - years * 12
    if month == 0:
        month = 12
        years -= 1
    return years, month


def forward_one_week_fn(main_frame, current_period, navigation_fn):
    wk = timedelta(days=7)
    navigation_fn(lambda tp: tp.move_delta(wk))


def backward_one_week_fn(main_frame, current_period, navigation_fn):
    wk = timedelta(days=7)
    navigation_fn(lambda tp: tp.move_delta(-1*wk))


def navigate_month_step(current_period, navigation_fn, direction):
    """
    Currently does notice leap years.
    """
    tm = current_period.mean_time()
    if direction > 0:
        if tm.month == 2:
            d = 28
        elif tm.month in (4,6,9,11):
            d = 30
        else:
            d = 31
    else:
        if tm.month == 3:
            d = 28
        elif tm.month in (5,7,10,12):
            d = 30
        else:
            d = 31
    mv = timedelta(days=d)
    navigation_fn(lambda tp: tp.move_delta(direction*mv))


def forward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, 1)


def backward_one_month_fn(main_frame, current_period, navigation_fn):
    navigate_month_step(current_period, navigation_fn, -1)


def forward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = timedelta(days=365)
    navigation_fn(lambda tp: tp.move_delta(yr))


def backward_one_year_fn(main_frame, current_period, navigation_fn):
    yr = timedelta(days=365)
    navigation_fn(lambda tp: tp.move_delta(-1*yr))


def fit_millennium_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    if mean.year > get_millenium_max_year():
        year = get_millenium_max_year()
    else:
        year = max(get_min_year(), int(mean.year/1000)*1000)
    start = datetime(year, 1, 1)
    end = datetime(year + 1000, 1, 1)
    navigation_fn(lambda tp: tp.update(start, end))


def get_min_year():
    return PyTimeType().get_min_time()[0].year


def get_millenium_max_year():
    return PyTimeType().get_max_time()[0].year - 1000

    
def get_century_max_year():
    return PyTimeType().get_max_time()[0].year - 100


def fit_century_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    if mean.year > get_century_max_year():
        year = get_century_max_year()
    else:
        year = max(get_min_year(), int(mean.year/100)*100)
    start = datetime(year, 1, 1)
    end = datetime(year + 100, 1, 1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_decade_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = datetime(int(mean.year/10)*10, 1, 1)
    end = datetime(int(mean.year/10)*10+10, 1, 1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_year_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = datetime(mean.year, 1, 1)
    end = datetime(mean.year + 1, 1, 1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_month_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = datetime(mean.year, mean.month, 1)
    if mean.month == 12:
        end = datetime(mean.year + 1, 1, 1)
    else:
        end = datetime(mean.year, mean.month + 1, 1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_day_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = datetime(mean.year, mean.month, mean.day)
    end = start + timedelta(days=1)
    navigation_fn(lambda tp: tp.update(start, end))


def fit_week_fn(main_frame, current_period, navigation_fn):
    mean = current_period.mean_time()
    start = datetime(mean.year, mean.month, mean.day)
    weekday = datetime.weekday(start)
    start = start - timedelta(days=weekday)
    if not main_frame.week_starts_on_monday():
        start = start - timedelta(days=1)
    end = start + timedelta(days=7)
    navigation_fn(lambda tp: tp.update(start, end))


class StripCentury(Strip):

    def label(self, time, major=False):
        if major:
            # TODO: This only works for English. Possible to localize?
            start_year = self._century_start_year(time.year)
            next_start_year = start_year + 100
            return str(next_start_year / 100) + " century"
        return ""

    def start(self, time):
        return datetime(max(self._century_start_year(time.year), 10), 1, 1)

    def increment(self, time):
        return time.replace(year=time.year + 100)

    def get_font(self, time_period):
        return get_default_font(8)

    def _century_start_year(self, year):
        year = (int(year) / 100) * 100
        #if year > get_century_max_year():
        #    year = get_century_max_year
        return year 


class StripDecade(Strip):

    def label(self, time, major=False):
        # TODO: This only works for English. Possible to localize?
        return str(self._decade_start_year(time.year)) + "s"

    def start(self, time):
        return datetime(self._decade_start_year(time.year), 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+10)

    def _decade_start_year(self, year):
        return (int(year) / 10) * 10

    def get_font(self, time_period):
        return get_default_font(8)


class StripYear(Strip):

    def label(self, time, major=False):
        return str(time.year)

    def start(self, time):
        return datetime(time.year, 1, 1)

    def increment(self, time):
        return time.replace(year=time.year+1)

    def get_font(self, time_period):
        return get_default_font(8)


class StripMonth(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s" % (abbreviated_name_of_month(time.month), time.year)
        return abbreviated_name_of_month(time.month)

    def start(self, time):
        return datetime(time.year, time.month, 1)

    def increment(self, time):
        return time + timedelta(calendar.monthrange(time.year, time.month)[1])

    def get_font(self, time_period):
        return get_default_font(8)


class StripDay(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s" % (time.day, abbreviated_name_of_month(time.month), time.year)
        return str(time.day)

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)

    def get_font(self, time_period):
        if (time_period.start_time.weekday() in (5, 6)):
                return get_default_font(8, True)
        else:
            return get_default_font(8)


class StripWeek(Strip):

    def __init__(self, config):
        Strip.__init__(self)
        self.config = config

    def label(self, time, major=False):
        if major:
            # Example: Week 23 (1-7 Jan 2009)
            first_weekday = self.start(time)
            next_first_weekday = self.increment(first_weekday)
            last_weekday = next_first_weekday - timedelta(days=1)
            range_string = self._time_range_string(first_weekday, last_weekday)
            if self.config.week_start == "monday":
                return (_("Week") + " %s (%s)") % (time.isocalendar()[1], range_string)
            else:
                # It is sunday (don't know what to do about week numbers here)
                return range_string
        # This strip should never be used as minor
        return ""

    def start(self, time):
        stripped_date = datetime(time.year, time.month, time.day)
        if self.config.week_start == "monday":
            days_to_subtract = stripped_date.weekday()
        else:
            # It is sunday
            days_to_subtract = (stripped_date.weekday() + 1) % 7
        return stripped_date - timedelta(days=days_to_subtract)

    def increment(self, time):
        return time + timedelta(7)

    def get_font(self, time_period):
        return get_default_font(8)

    def _time_range_string(self, time1, time2):
        """
        Examples:

        * 1-7 Jun 2009
        * 28 Jun-3 Jul 2009
        * 28 Jun 08-3 Jul 2009
        """
        if time1.year == time2.year:
            if time1.month == time2.month:
                return "%s-%s %s %s" % (time1.day, time2.day,
                                        abbreviated_name_of_month(time1.month),
                                        time1.year)
            return "%s %s-%s %s %s" % (time1.day,
                                       abbreviated_name_of_month(time1.month),
                                       time2.day,
                                       abbreviated_name_of_month(time2.month),
                                       time1.year)
        return "%s %s %s-%s %s %s" % (time1.day,
                                      abbreviated_name_of_month(time1.month),
                                      time1.year,
                                      time2.day,
                                      abbreviated_name_of_month(time2.month),
                                      time2.year)


class StripWeekday(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s %s" % (abbreviated_name_of_weekday(time.weekday()),
                                    time.day,
                                    abbreviated_name_of_month(time.month),
                                    time.year)
        return abbreviated_name_of_weekday(time.weekday())

    def start(self, time):
        return datetime(time.year, time.month, time.day)

    def increment(self, time):
        return time + timedelta(1)

    def get_font(self, time_period):
        return get_default_font(8)


class StripHour(Strip):

    def label(self, time, major=False):
        if major:
            return "%s %s %s %s" % (time.day, abbreviated_name_of_month(time.month),
                                    time.year, time.hour)
        return str(time.hour)

    def start(self, time):
        return datetime(time.year, time.month, time.day, time.hour)

    def increment(self, time):
        return time + timedelta(hours=1)

    def get_font(self, time_period):
        return get_default_font(8)


def microseconds_to_delta(microsecs):
    """Return a timedelta representing the given number of microseconds."""
    return timedelta(microseconds=microsecs)


def delta_to_microseconds(delta):
    """Return the number of microseconds that the timedelta represents."""
    return (delta.days * US_PER_DAY +
            delta.seconds * US_PER_SEC +
            delta.microseconds)


def move_period_num_days(period, num):
    delta = timedelta(days=1) * num
    start_time = period.start_time + delta
    end_time = period.end_time + delta
    return TimePeriod(period.time_type, start_time, end_time)


def move_period_num_weeks(period, num):
    delta = timedelta(weeks=1) * num
    start_time = period.start_time + delta
    end_time = period.end_time + delta
    return TimePeriod(period.time_type, start_time, end_time)


def move_period_num_months(period, num):
    try:
        delta = num
        years = abs(delta) / 12
        if num < 0:
            years = -years
        delta = delta - 12 * years
        if delta < 0:
            start_month = period.start_time.month + 12 + delta
            end_month = period.end_time.month + 12 + delta
            if start_month > 12:
                start_month -=12
                end_month -=12
            if start_month > period.start_time.month:
                years -= 1
        else:
            start_month = period.start_time.month + delta
            end_month = period.start_time.month + delta
            if start_month > 12:
                start_month -=12
                end_month -=12
                years += 1
        start_year = period.start_time.year + years
        end_year = period.start_time.year + years
        start_time = period.start_time.replace(year=start_year, month=start_month)
        end_time = period.end_time.replace(year=end_year, month=end_month)
        return TimePeriod(period.time_type, start_time, end_time)
    except ValueError:
        return None


def move_period_num_years(period, num):
    try:
        delta = num
        start_year = period.start_time.year
        end_year = period.end_time.year
        start_time = period.start_time.replace(year=start_year + delta)
        end_time = period.end_time.replace(year=end_year + delta)
        return TimePeriod(period.time_type, start_time, end_time)
    except ValueError:
        return None
