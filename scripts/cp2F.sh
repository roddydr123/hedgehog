#!/bin/bash
# copies the given file from the hedgehog files folder to the fluka cluster

scp -i ~/.ssh/id_rsa /mnt/c/users/david/Documents/TRIUMF/projects/3drm-design/files/$1.inp droddy@fluka02.triumf.ca:/group/pifnif/david/$1.inp
