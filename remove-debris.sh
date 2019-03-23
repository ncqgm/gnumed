#!/bin/bash

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.py~' -exec rm -v '{}' ';'
find ./ -name 'wxg*.wxg~' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./ -name '*.tgz' -exec rm -v '{}' ';'
find ./ -name '*.bz2' -exec rm -v '{}' ';'
find ./ -name '*-gnumed.mo' -exec rm -v '{}' ';'
find ./ -type d -name '__pycache__' -exec rmdir -v '{}' ';'
find ./ -type d -name '.mypy_cache' -exec rmdir -v '{}' ';'
