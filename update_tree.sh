#!/bin/bash

./remove-debris.sh

echo "updating python client source from VCS (currently git)"
git pull -v | tee git-pull.log
