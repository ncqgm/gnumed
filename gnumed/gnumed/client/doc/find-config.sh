#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

# where to look for files
BASE="../"

find ${BASE} -follow -name '*.py' -print0 | xargs -0 grep "option\\s*=\\s*u*'.*'" > current-options.lst

# | grep -v "cfg\.get"
