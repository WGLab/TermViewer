#!/bin/bash

for file in ~/nixona2/preprocessed_test/*.txt
do
  metamap -y -@ reslnvvhpc041.research.chop.edu -S reslnvvhpc041.research.chop.edu -R HPO -V USAbase --JSONf 2 $file ~/mm_preprocessed/$(basename $file .txt).json
done
echo Metamap has completed running
