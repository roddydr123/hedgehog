#!/bin/bash

MATRIX="/mnt/c/users/david/documents/triumf/projects/3drm-design/hedgehog/cones/matrix"

for i in {1..21..1}
do
 printf -v j "%02d" $i
 scp -i ~/.ssh/id_rsa droddy@fluka02.triumf.ca:/group/pifnif/david/dataset4/$i/plot05.dat $MATRIX/fullblock$j.txt
done
