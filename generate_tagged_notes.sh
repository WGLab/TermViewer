#!/bin/bash

#define filepaths
UMLS_DICT=
NOTES=
PREPROCESSED_NOTES=
METAMAP_OUT=
CTAKES_OUT=
TAGGED_NOTES=

METAMAP_DIR=
CTAKES_DIR=
CURR_DIR=$(pwd -P)

#PREPROCESSING
for file in $NOTES/*.txt
do
  tr -s '\n' < $file  |  sed 's/^[ \t]*//;s/[ \t]*$//'  | sed '/^$/d' > $PREPROCESSED_NOTES/$(basename $file)
done
echo $NOTES has been preprocessed and saved to $PREPROCESSED_NOTES

#CTAKES
cd $CTAKES_DIR
bin/runClinicalPipeline.sh -i $PREPROCESSED_NOTES --xmiOut $CTAKES_OUT --key 7b9a3776-3c09-4a40-9426-269e001d2026
echo cTakes has run on $PREPROCESSED_NOTES and outputs have been saved to $CTAKES_OUT

#METAMAP
#start MM servers
cd $METAMAP_DIR
./bin/skrmedpostctl start
./bin/wsdserverctl start
#run MM on each file
for file in $PREPROCESSED_NOTES/*.txt
do
  metamap -y -@ reslnvvhpc041.research.chop.edu -S reslnvvhpc041.research.chop.edu -R HPO -V USAbase --JSONf 2 $file $METAMAP_OUT/$(basename $file .txt).json
done
#stop MM servers
./bin/skrmedpostctl stop
./bin/wsdserverctl stop
echo MetaMap has run on $PREPROCESSED_NOTES and outputs have been saved to $METAMAP_OUT

#OUTPUT
cd $HOME
python3 generate_tags.py $UMLS_DICT $PREPROCESSED_NOTES $CTAKES_OUT $METAMAP_OUT $TAGGED_NOTES
echo Tagged notes have been saved to $TAGGED_NOTES to view use TermViewer
