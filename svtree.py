#!/usr/bin/env python

#check inputs
import sys

if len(sys.argv) == 1:
    raise SyntaxError('Target argument required')
elif len(sys.argv)> 2 :
    raise SyntaxError('Only one target allowed')

import os
if os.getuid() != 0:
    raise PermissionError('Must be root to run svtree')

# run btrfs sbuvolume list
import subprocess
btrfs_command = ("btrfs subvolume list -p -a --sort path "+str(sys.argv[1])).split(" ")
btrfs_result = subprocess.run(btrfs_command, stdout=subprocess.PIPE)
btrfs_result_lines=btrfs_result.stdout.decode('utf-8').splitlines()

# make list of subvolume objects
subvolumes=[]

class Subvolume(object):
    def __init__(self, subvolid, path):
        self.subvolid = subvolid
        self.parent = parent
        self.path = path
        self.children = []

import re
subvolid_re = re.compile(r"ID (\d+)")
path_re = re.compile(r"path ([\S\<\>]*)")
parent_re = re.compile(r"parent (\d+)")

for line in btrfs_result_lines:
    subvolid = subvolid_re.search(line).group(1)
    parent = parent_re.search(line).group(1)
    path = path_re.search(line).group(1)
    subvolumes.append(Subvolume(subvolid, path))

# populate children
for child_subvolume in subvolumes:
    for parent_subvolume in subvolumes:
        if parent_subvolume.subvolid == child_subvolume.parent:
            break
    parent_subvolume.children.append(child_subvolume.subvolid)

# print subvolume objects
for subvolume in subvolumes:
    print(subvolume.__dict__)
