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


import os.path
import shutil
import tempfile

from timelinelib.test.cases.unit import UnitTestCase


class TmpDirTestCase(UnitTestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def read(self, name):
        with open(self.get_tmp_path(name)) as f:
            return f.read()

    def get_tmp_path(self, name):
        return os.path.join(self.tmp_dir, name)
