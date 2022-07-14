# TermViewer
Repository for NLP project filtering medical notes

This project consists of two main componentns: 

scripts: contains the programs that will generate tagged notes. tagged notes are formatted as JSON files and include the note as well as information about the HPO terms found in those notes using MetaMap and cTakes
Flask App: a web application that allows you to load tagged JSON files from a server to visualize the various terms being extracted from each note and classify them as good/bad. All confidential information remains on the server but can be accessed by clients elsewhere in order to annotate large sets of note data   

## Running Scripts
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

## Running Web App

After the script has finished executing the results can be visualized by running the web application 

To begin navigate to the TermViewer directory on your server. Make sure you have miniconda or anaconda installed (if not, you can go to [here](https://docs.conda.io/en/latest/miniconda.html) to download the appropriate version and install). Then create a new environment using the .yml file from the repository and the following command: 

```
conda env create --name [envname] -f viewerenv.yml
```

Afterwards activate the environment. Before running the webapp make sure to execute the following step.   

```
conda activate [envname]
```

Now with your preferred editing tool navigate to init_db.py and modify/add SQL statements to add the paths of the generated JSON files from the previous step into the notes database. 

After the database initialization has been edited to include the files that you have created then run 

```
python init_db.py
```

Now your SQLite database has been initialized and can store scores for each document. This step only has to be run once. 

NOTE: After the db has been created do not run this again or all saved values will be deleted when the tables are created from scratch again.

Once the database is ready you can start the webapp 

```
flask run
```

The console will print out the address the application is running on (usually localhost:5000). You can either view it directly or set up port tunneling to view from another device. 

You should see the following screen asking for an evaluator name and with a dropdown containing the list of patient notesets that you have stored in the notes table of the database. Scores are stored based on evaluator and note so enter a name to access the annotations specific to you and then select a noteset to navigate. 

![Main Page](https://user-images.githubusercontent.com/13920834/155355724-bdff8f3a-7e40-489f-9699-b3be1bd8b788.png)

Select which labels you would like to view and click 'Confirm Selection'

![Select Labels](https://user-images.githubusercontent.com/13920834/155356136-3a4f1de0-28b7-40bd-9c91-92cedeef958f.png)

Any HPO terms that were detected by MetaMap, cTakes, or both will now be overlaid onto the original note for easy analysis. You can navigate through individual notes in a patient's noteset using the next/previous buttons. The button next to 'Is this a good note?' Displays whether or not the note has been annotated as good or bad or if it has not received a score yet. Clicking on the button automatically updates the annotation value on the database.

![Annotations](https://user-images.githubusercontent.com/13920834/155356857-08ea90d4-d477-4e95-92eb-021ba21e5600.png)

