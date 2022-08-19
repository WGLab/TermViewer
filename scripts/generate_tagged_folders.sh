#!/bin/bash -x

#define filepaths
# Location of umls term dictionary (MRCONSO.RRF)
UMLS_DICT=/home/nixona2/nixona2/MRCONSO.RRF
# Location of input note folders (directories containing txt files)
NOTES=/home/nixona2/nixona2/patients/
# Output location for preprocessed notes
PREPROCESSED_NOTES=/home/nixona2/scripted_preprocess/
# Output location for MetaMap
METAMAP_OUT=/home/nixona2/scripted_mm/
# Output location for cTakes
CTAKES_OUT=/home/nixona2/scripted_ctakes/
# Output location for final tagged notes (.JSON format)
TAGGED_NOTES=/home/nixona2/scripted_final/

# Home directory of MetaMap installation
METAMAP_DIR=/home/nixona2/public_mm/
# Home directory of cTakes installation
CTAKES_DIR=/home/nixona2/Documents/apache-ctakes-4.0.0.1/
CURR_DIR=$(pwd -P)

##Iterate through subdirectories
for DIR in $NOTES/*/
  do
    DIR=${DIR%*/}
    DIR=${DIR##*/}

    ##PREPROCESSING
    mkdir $PREPROCESSED_NOTES/$DIR
    for file in $NOTES/$DIR/*.txt
    do
      tr -s '\n' < $file  |  sed 's/^[ \t]*//;s/[ \t]*$//'  | sed '/^$/d' > $PREPROCESSED_NOTES/$DIR/$(basename $file)
    done
    echo $NOTES/$DIR has been preprocessed and saved to $PREPROCESSED_NOTES/$DIR

    ##CTAKES
    mkdir $CTAKES_OUT/$DIR
    cd $CTAKES_DIR
    export CTAKES_HOME=$CTAKES_DIR
    bin/runClinicalPipeline.sh -i $PREPROCESSED_NOTES/$DIR --xmiOut $CTAKES_OUT/$DIR --key 7b9a3776-3c09-4a40-9426-269e001d2026
    echo cTakes has run on $PREPROCESSED_NOTES/$DIR and outputs have been saved to $CTAKES_OUT/$DIR

    ##METAMAP
    ##start MM servers
    mkdir $METAMAP_OUT/$DIR
    cd $METAMAP_DIR
    ./bin/skrmedpostctl start
    ./bin/wsdserverctl start
    ##run MM on each file
    for file in $PREPROCESSED_NOTES/$DIR/*.txt
    do
      metamap -y -@ reslnvvhpc041.research.chop.edu -S reslnvvhpc041.research.chop.edu -R HPO -V USAbase --JSONf 2 $file $METAMAP_OUT/$DIR/$(basename $file .txt).json
    done
    ##stop MM servers
    ./bin/skrmedpostctl stop
    ./bin/wsdserverctl stop
    echo MetaMap has run on $PREPROCESSED_NOTES/$DIR and outputs have been saved to $METAMAP_OUT/$DIR

    ##OUTPUT
    cd $CURR_DIR
    python3 generate_tags.py $UMLS_DICT $PREPROCESSED_NOTES/$DIR $CTAKES_OUT/$DIR $METAMAP_OUT/$DIR $TAGGED_NOTES $DIR
    echo Tagged notes have been saved to $TAGGED_NOTES/$DIR.json to view using TermViewer
  done


