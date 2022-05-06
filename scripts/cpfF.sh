#!/bin/bash
# copies the given file from the cluster to the data folder

scp -i ~/.ssh/id_rsa droddy@fluka02.triumf.ca:/group/pifnif/david/$1/$2 $2
