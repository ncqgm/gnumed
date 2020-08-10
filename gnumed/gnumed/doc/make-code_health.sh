#!/bin/bash

DIRS="../client/pycommon ../client/business ../client/wxpython"

pyflakes3 ${DIRS} &> source-coding_errors.log
radon mi ${DIRS} | egrep '\-\s[^AB]$' &> source-maintainability.log
radon cc ${DIRS} | egrep '(\-\s[^AB])|(.py)$' &> source-cyclic_complexity.log
