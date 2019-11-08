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


from timelinelib.canvas.data.timeperiod import TimePeriod


class Eras(object):
    """
    The list of all eras defined for a timeline.

    Contains function for cloning of the whole list which is a
    necessary operation for undo/redo operations.
    """

    def __init__(self, now_func, eras=None):
        self.now_func = now_func
        if eras is None:
            self._eras = []
        else:
            self._eras = eras

    def get_all(self):
        return sorted(self._eras)

    def get_all_periods(self):

        def get_key(e):
            return e.get_time_period().start_time

        def merge_colors(c1, c2):
            return (
                (c1[0] + c2[0]) // 2,
                (c1[1] + c2[1]) // 2,
                (c1[2] + c2[2]) // 2
            )

        def create_overlapping_era(e0, e1, start, end):
            era = e1.duplicate()
            era.set_time_period(TimePeriod(start, end))
            era.set_color(merge_colors(e0.get_color(), e1.get_color()))
            era.set_name("%s + %s" % (e0.get_name(), e1.get_name()))
            return era

        def get_start_and_end_times(e0, e1):
            e0start = e0.get_time_period().start_time
            e0end = e0.get_time_period().end_time
            e1start = e1.get_time_period().start_time
            e1end = e1.get_time_period().end_time
            return e0start, e0end, e1start, e1end

        def return_era_for_overlapping_type_1(e0, e1):
            e0start, e0end, e1start, e1end = get_start_and_end_times(e0, e1)
            era = create_overlapping_era(e0, e1, e1start, e0end)
            e0.set_time_period(TimePeriod(e0start, e1start))
            e1.set_time_period(TimePeriod(e0end, e1end))
            return era

        def return_era_for_overlapping_type_2(e0, e1):
            e0start, e0end, _, e1end = get_start_and_end_times(e0, e1)
            era = create_overlapping_era(e0, e1, e0start, e0end)
            self.all_eras.remove(e0)
            e1.set_time_period(TimePeriod(e0end, e1end))
            return era

        def return_era_for_overlapping_type_3(e0, e1):
            return return_era_for_overlapping_type_2(e1, e0)

        def return_era_for_overlapping_type_4(e0, e1):
            _, _, e1start, e1end = get_start_and_end_times(e0, e1)
            era = create_overlapping_era(e0, e1, e1start, e1end)
            self.all_eras.remove(e0)
            self.all_eras.remove(e1)
            return era

        def return_era_for_overlapping_type_5(e0, e1):
            e0start, _, e1start, e1end = get_start_and_end_times(e0, e1)
            era = create_overlapping_era(e0, e1, e1start, e1end)
            e0.set_time_period(TimePeriod(e0start, e1start))
            self.all_eras.remove(e1)
            return era

        def return_era_for_overlapping_type_6(e0, e1):
            e0start, e0end, e1start, e1end = get_start_and_end_times(e0, e1)
            era = create_overlapping_era(e0, e1, e1start, e1end)
            e0.set_time_period(TimePeriod(e0start, e1start))
            e1.set_time_period(TimePeriod(e1end, e0end))
            e1.set_name(e0.get_name())
            e1.set_color(e0.get_color())
            return era

        def clone_all_eras():
            return [e.duplicate() for e in self.get_all()]

        overlap_func = (None,
                        return_era_for_overlapping_type_1,
                        return_era_for_overlapping_type_2,
                        return_era_for_overlapping_type_3,
                        return_era_for_overlapping_type_4,
                        return_era_for_overlapping_type_5,
                        return_era_for_overlapping_type_6)

        def create_overlapping_era_and_remove_hidden_eras():
            """
            self.all_eras is always sorted by Era start time.
            This method finds the first pair of Era's that overlaps.
            If such a pair is found, a overlapping Era is created and added
            to the the self.all_eras list. If any or both of the original
            Era's are hidden by the overlapping Era, they are removed from
            the self.all_eras list.
            When one overlapping pair has been found and processed the
            function returns False, after updating the self.all_eras list
            If no overlapping pairs of Era's are found the function retuns
            True.
            """
            e0 = self.all_eras[0]
            for e1 in self.all_eras[1:]:
                strategy = e0.overlapping(e1)
                if strategy > 0:
                    self.all_eras.append(overlap_func[strategy](e0, e1))
                    self.all_eras = sorted(self.all_eras, key=get_key)
                    return False
                else:
                    e0 = e1
            return True

        def adjust_all_eras_for_ends_today():
            for era in self.all_eras:
                if era.ends_today():
                    era.set_time_period(TimePeriod(era.get_time_period().start_time, self.now_func()))

        def remove_eras_with_no_duration():
            self.all_eras = [e for e in self.all_eras if e.is_period()]

        self.all_eras = clone_all_eras()
        adjust_all_eras_for_ends_today()
        remove_eras_with_no_duration()
        if self.all_eras == []:
            return []
        while True:
            if len(self.all_eras) > 0:
                done = create_overlapping_era_and_remove_hidden_eras()
            else:
                done = True
            if done:
                return self.all_eras
