from datetime import timedelta, tzinfo, datetime, time

class Proxy(object):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

class cDocumentType(Proxy):
    pass

class cPersonName(Proxy):
    pass

class cPerson(Proxy):
    pass

class cDocument(Proxy):
    pass

class cInboxMessage(Proxy):
    pass

class cDocumentPart(Proxy):
    pass

class TimeDelta(timedelta):
    """ TODO: pyjamas doesn't have datetime.timedelta.  fake it.
    """
    def __init__(self, days=0, seconds=0, microseconds=0,
                    milliseconds=0, minutes=0, hours=0, weeks=0):
        timedelta.__init__(self, days, seconds, microseconds,
                    milliseconds, minutes, hours, weeks)

ZERO = TimeDelta(0)

class FixedOffsetTimezone(tzinfo):
    """Fixed offset in minutes east from UTC.

    This is exactly the implementation__ found in Python 2.3.x documentation,
    with a small change to the `!__init__()` method to allow for pickling
    and a default name in the form ``sHH:MM`` (``s`` is the sign.).

    .. __: http://docs.python.org/library/datetime.html#datetime-tzinfo
    """
    _name = None
    _offset = ZERO

    def __init__(self, offset=None, name=None):
        if offset is not None:
            self._offset = timedelta(days=offset.days,
                                              seconds=offset.seconds)
        if name is not None:
            self._name = name

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        if self._name is not None:
            return self._name
        else:
            seconds = self._offset.seconds + self._offset.days * 86400
            hours, seconds = divmod(seconds, 3600)
            minutes = seconds/60
            if minutes:
                return "%+03d:%d" % (hours, minutes)
            else:
                return "%+03d" % hours

    def dst(self, dt):
        return ZERO


class Time(time):
    def __init__(self, **kwargs):
        hour = kwargs.get('hour')
        minute = kwargs.get('minute')
        second = kwargs.get('second')
        microsecond = kwargs.get('microsecond')
        tzinfo = kwargs.get('tzinfo', None)
        time.__init__(self, hour, minute, second, microsecond, tzinfo)

class DateTime(datetime):
    def __init__(self, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')
        day = kwargs.get('day')
        hour = kwargs.get('hour')
        minute = kwargs.get('minute')
        second = kwargs.get('second')
        microsecond = kwargs.get('microsecond')
        tzinfo = kwargs.get('tzinfo', None)
        datetime.__init__(self, year, month, day, hour, minute, second,
                                microsecond, tzinfo)

