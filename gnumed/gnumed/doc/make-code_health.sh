#!/bin/bash

DIRS="../client/pycommon ../client/business ../client/wxpython"

echo "=== Code - problems (pyflakes3) ==========" > source-coding_errors.log
pyflakes3 ${DIRS} &>> source-coding_errors.log

echo "=== Code - maintainability (radon mi, lower = better) ==========" > source-maintainability.log
radon mi ${DIRS} | egrep '\-\s[^AB]$' &>> source-maintainability.log

echo "=== Code - cyclic complexity (radon cc, lower = better) ==========" > source-cyclic_complexity.log
radon cc ${DIRS} | egrep '(\-\s[^AB])|(.py)$' &>> source-cyclic_complexity.log
