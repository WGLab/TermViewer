# nlp_notes
Repository for NLP project filtering medical notes

scripts: contains the programs that will generate tagged notes, tagged notes are formatted as JSON files and include the note as well as information about the HPO terms found in those notes using MetaMap and cTakes
GUI: contains a web application that allows you to load tagged JSON files to visualize the various terms being extracted from each note.  

To use this program you will need to have installed MetaMap and cTakes to the machine where your notes are stored.

To begin clone this repository and open to scripts/generate_tagged_notes.sh 

Modify the file paths to the appropriate locations on your machine

NOTE: All file paths must be pointing to existing directories so make sure to create empty output folders if they do not already exist 

![Specify Filepaths](https://github.com/WGLab/nlp_notes/blob/main/docs/images/filepaths.PNG)

From the scripts folder run
```
./generate_tagged_notes.sh 
```

This script will preprocess all input notes in the specified folder, run MetaMap and cTakes, and then create a final JSON file containing information from both outputs

After the script has finished executing you can open GUI/ner.html to visualize the results

It should open the following screen on your default browser

Click 'Choose File' and navigate to the output folder you specified earlier to load a JSON file containing a tagged note 

![Main Page](https://github.com/WGLab/nlp_notes/blob/main/docs/images/main.PNG)

Select which labels you would like to view and click 'Confirm Selection'

![Select Labels](https://github.com/WGLab/nlp_notes/blob/main/docs/images/labels.PNG)

Any HPO terms that were detected by MetaMap, cTakes, or both will now be overlaid onto the original note for easy analysis
