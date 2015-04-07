#!/bin/bash

echo "git gc --aggressive" &> $0.log
git gc --aggressive &>> $0.log
echo "git repack -a -d" &>> $0.log
git repack -a -d &>> $0.log
echo "git prune-packed" &>> $0.log
git prune-packed &>> $0.log
echo "git fsck --full --unreachable --dangling --strict --verbose" &>> $0.log
git fsck --full --unreachable --dangling --strict --verbose &>> $0.log
less $0.log
