# nlp_notes
Repository for NLP project filtering medical notes

GUI folder contains an interface that allows you to load notes and their corresponding CTakes or MetaMap output files to visualize the appearance of various terms being extracted from each note.  

To run this program clone this repository and execute the following line of code in the terminal or run GUI/main.py in a Python IDE

```
python3 GUI/main.py
```

Before you begin it is important that all notes are stored in one directory as txt files, all MetaMap output files are stored together in another directory in json format, and all cTakes output files are stored together in another directory in xmi format. 

When the program begins you should see the following screen:

![Main Page](https://github.com/WGLab/nlp_notes/blob/main/GUI/docs/images/main.PNG)

The Good/Bad buttons on the right hand side let you annotate each loaded file as either a good note or a bad note, these annotations are stored locally every time you hit Previous/Next and saved when you hit Exit
 
To view documents first click 'Open File' and navigate to one text file in the directory containing ALL the notes that you want to go through.

![File Explorer](https://github.com/WGLab/nlp_notes/blob/main/GUI/docs/images/fileexplorer.PNG)

Then click 'Load MetaMap' and navigate to one json file in the directory containing ALL the MetaMap outputs generated from your notes. Make sure that the name before the .json extension of your MetaMap output files matches exactly with the names of the .txt files containing the note content. 

![MetaMap](https://github.com/WGLab/nlp_notes/blob/main/GUI/docs/images/mm.PNG)

Click 'Load cTakes' and navigate to one xmi file in the directory containing ALL the cTakes outputs generated from your notes. Make sure that the name before the .xmi extension of your cTakes output files matches exactly with the names of the .txt files containing the note content. 

![cTakes](https://github.com/WGLab/nlp_notes/blob/main/GUI/docs/images/ctakes.PNG) 

Once all the files are loaded you should see an output like the one below. 

ORANGE - indicates a term was identified by MetaMap 
YELLOW - indicates a term was identified by cTakes
GREEN - indicates a term was identified by both MetaMap and cTakes 

![Loaded Main Page](https://github.com/WGLab/nlp_notes/blob/main/GUI/docs/images/loaded.PNG) 
