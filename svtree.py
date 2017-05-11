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

# initalize list of subvolume objects
import re
class Subvolume(object):
    def __init__(self, subvolid, parent, path):
        self.subvolid = subvolid
        self.parent = parent
        if path[:9] != "<FS_TREE>":
            self.path = "<FS_TREE>/"+path
        else:
            self.path = path
        self.children = []
        self.name = re.search(r"[^\/ ]+$",self.path).group(0)
        self.parent_path = ""

subvolumes=[Subvolume('5',None,"<FS_TREE>")]

subvolid_re = re.compile(r"ID (\d+)")
path_re = re.compile(r"path ([\S\<\>]*)")
parent_re = re.compile(r"parent (\d+)")

for line in btrfs_result_lines:
    subvolid = subvolid_re.search(line).group(1)
    parent = parent_re.search(line).group(1)
    path = path_re.search(line).group(1)
    subvolumes.append(Subvolume(subvolid, parent, path))

# populate children and parent path attributes
for child_subvolume in subvolumes:
    for parent_subvolume in subvolumes:
        if parent_subvolume.subvolid == child_subvolume.parent:
            parent_subvolume.children.append(child_subvolume.subvolid)
            child_subvolume.parent_path = parent_subvolume.path
            break

## print subvolume objects (debug)
#for subvolume in subvolumes:
#    print(subvolume.__dict__)

# define recusrive tree-ing function
def find_subvol(subvolid):
    global subvolumes
    for subvolume in subvolumes:
        if subvolume.subvolid == subvolid:
            return subvolume

def make_tree(subvolume):
    tree = ["|-- "+subvolume.path.replace(subvolume.parent_path,'')]
    if subvolume.children == []:
        return tree
    else:
        for child in subvolume.children:
            tree.extend(make_tree(find_subvol(child)))
        tree = ["|   "+item for item in tree]
        return tree

#print result
print("\n".join(make_tree(find_subvol('5'))))

