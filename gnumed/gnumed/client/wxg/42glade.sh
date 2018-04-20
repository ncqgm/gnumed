#!/bin/bash

export PYTHONPATH="/usr/lib/python2.7/dist-packages/wxp4/:${PYTHONPATH:+$PYTHONPATH}"
wxglade $@
