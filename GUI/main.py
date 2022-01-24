import tkinter
from tkinter import *
from tkinter import filedialog
import json
import glob
import xml.etree.ElementTree as et

# Dictionaries to be used for storing words as (start_location, stop_location) : {CUID, matching_term}
mm_dict = {}
ctakes_dict = {}

# Sets to store matching words and find which terms agree between ctakes and metamap
mm_words = set()  # {"impaction", "diabetes", "Down Syndrome"}
ctakes_words = set()  # {"vascular", "cornea", "Down Syndrome"}
shared_words = set()

# Some summary count statistics (not implemented yet but could be useful for analysis)
total_mmcount = 0
total_ctakescount = 0
total_count = 0
ss_count = 0  # Signs and Symptoms
dd_count = 0  # Diseases and Disorders

# Stores file path for each directory and the file names of the notes (extensions are replaced to get mm/ctakes files)
txt_fp = "C:/Users/nixona2/Documents/test_notes/text/"
txt_files = []
mm_fp = "C:/Users/nixona2/Documents/test_notes/mm/"
ctakes_fp = "C:/Users/nixona2/Documents/test_notes/ctakes/"
storage_fp = "C:/Users/nixona2/Documents/test_notes/test_out/"
umls_fp = "C:/Users/nixona2/Documents/MRCONSO.RRF"
filenames = []
test_filename = "10147920"
single_file = True
# Index in txt_files of current file being displayed
currentFile = 0

# Stores notations (Good/Bad) for each note to be written out on close
notation_dict = {}
umls_conv = {}


def readUMLSDict(umls_fp):
    global umls_conv
    with open(umls_fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for l in lines:
        # print(l)
        entry = l.split('|')
        if entry[11] == 'HPO':
            umls_conv[entry[0]] = {"HPO ID": entry[13], "Description": entry[14]}

def createJSON(txt_fp, mm_fp, ctakes_fp, out_fp, doc_name):
    # load text file
    file_content = ""
    with open(txt_fp + doc_name + ".txt", 'r') as f:
        file_content = f.read()
    # load mm
    read_mm(mm_fp + doc_name + ".json", file_content)
    # load ctakes
    read_ctakes(ctakes_fp + doc_name + ".xmi", file_content)
    ne_list = []
    for word in mm_dict:
        print(mm_dict[word])
        ne_list.append({"py/object": "document.NamedEntity",
                        "type": "MetaMap",
                        "text": "general",
                        "identifier": mm_dict[word]["umls_id"],
                        "offset": word[0],
                        "length": word[1],
                        "description": "*",
                        "algorithm": "MetaMap"})
    for word in ctakes_dict:
        print(ctakes_dict[word])
        ne_list.append({"py/object": "document.NamedEntity",
                        "type": "CTakes",
                        "text": "general",
                        "identifier": ctakes_dict[word]["umls_id"],
                        "offset": word[0],
                        "length": word[1],
                        "description": "*",
                        "algorithm": "MetaMap"})
    output = [{"py/object": "document.Document",
               "data_struct_version": 1.0,
               "source_file": "BioCXML/9464.bioc.xml",
               "doc_id": "4029977",
               "pmid": "24851142",
               "pmcid": "4029977",
               "publisher_item_identifier": "*",
               "doi": "10.1186/1897-4287-12-14",
               "license": "***",
               "title": "Patient Note",
               "abstract": "Note",
               "keyword": "",
               "authors": "",
               "subtitle": "*",
               "journal": "",
               "year": "",
               "entrez_pub_date": "*",
               "passage_list": [
                   {
                       "py/object": "document.Passage",
                       "section_type": "RESULTS",
                       "passage_type": "paragraph",
                       "offset": "0",
                       "passage_text": file_content,
                       "named_entity_list": ne_list}],
               "mesh_list": []}]
    with open(out_fp + doc_name + ".json", 'w') as f:
        json.dump(output, f)


# Loads next text file, corresponding MM and Ctakes files and updates displays
# Saves any annotation for the prior file before switching
# def nextFile():
#     global currentFile, mm_words, ctakes_words
#     notation_dict[txt_files[currentFile]] = annotation.get()
#     print(notation_dict)
#     currentFile += 1
#     if currentFile < len(txt_files):
#         new_fp = txt_fp + '/' + txt_files[currentFile]
#         new_mm_fp = mm_fp + '/' + txt_files[currentFile][:-4] + '.json'
#         new_ctakes_fp = ctakes_fp + '/' + txt_files[currentFile][:-4] + '.xmi'
#         print(new_fp)
#         print(new_mm_fp)
#         print(new_ctakes_fp)
#         tf = open(new_fp)
#         file_cont = tf.read()
#         txtarea.delete(1.0, END)
#         pathh.delete(0, END)
#         txtarea.insert(END, file_cont)
#         pathh.insert(END, new_fp)
#         tf.close()
#         mm_words = set(read_json(new_mm_fp))
#         ctakes_words = set(read_ctakes(new_ctakes_fp, new_fp))
#         update_display()

# Loads previous text file in txt_files list, corresponding MM and Ctakes files and updates displays
# Saves any annotation for the prior file before switching
# def prevFile():
#     global currentFile, mm_words, ctakes_words
#     currentFile -= 1
#     if currentFile >= 0:
#         new_fp = txt_fp + '/' + txt_files[currentFile]
#         new_mm_fp = mm_fp + '/' + txt_files[currentFile][:-4] + '.json'
#         new_ctakes_fp = ctakes_fp + '/' + txt_files[currentFile][:-4] + '.xmi'
#         print(new_fp)
#         print(new_mm_fp)
#         print(new_ctakes_fp)
#         tf = open(new_fp)
#         file_cont = tf.read()
#         txtarea.delete(1.0, END)
#         pathh.delete(0, END)
#         txtarea.insert(END, file_cont)
#         pathh.insert(END, new_fp)
#         tf.close()
#         mm_words = set(read_json(new_mm_fp))
#         ctakes_words = set(read_ctakes(new_ctakes_fp, new_fp))
#         update_display()


# Opens text file and stores the parent directory path as the txt_fp
# Loads all filenames in path into txt_files list

# def openFile():
#     global txt_fp, txt_files
#     txt = filedialog.askopenfilename(
#         initialdir="C:/Users/MainFrame/Desktop/",
#         title="Open Text file",
#         filetypes=(("Text Files", "*.txt"),)
#     )
#     pathh.insert(END, txt)
#     tf = open(txt)
#     file_cont = tf.read()
#     txtarea.insert(END, file_cont)
#     tf.close()
#     txt_fp = '/'.join(txt.split('/')[:-1])
#     txt_files = [x.split('\\')[-1] for x in glob.glob(txt_fp + '/*.txt')]
#     print("Text filepath: " + txt_fp)
#     print("List of files", txt_files)
#     update_display()

# Helper function to highlight words a specified tag color
# def highlight_word(word, tag, start="1.0", end="end",
#                    regexp=False):
#     start = txtarea.index(start)
#     end = txtarea.index(end)
#     txtarea.mark_set("matchStart", start)
#     txtarea.mark_set("matchEnd", start)
#     txtarea.mark_set("searchLimit", end)
#
#     count = tkinter.IntVar()
#     while True:
#         index = txtarea.search(word, "matchEnd", "searchLimit",
#                                count=count, regexp=regexp, nocase=True)
#         if index == "": break
#         if count.get() == 0: break
#         txtarea.mark_set("matchStart", index)
#         txtarea.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
#         txtarea.tag_add(tag, "matchStart", "matchEnd")

# Helper function to calculate where mm and ctakes agree/disagree and highlight each word in those sets accordingly
# def update_display():
#     for word in mm_words.intersection(ctakes_words):
#         highlight_word(word, "both")
#     for word in mm_words.difference(ctakes_words):
#         highlight_word(word, "mm")
#     for word in ctakes_words.difference(mm_words):
#         highlight_word(word, "ctakes")

# Opens a json file from MM and parses it to extract words
# TODO: Change to store start/end indices and CUID rather than words themselves

def read_mm(fp, txt_f):
    global mm_dict
    file = open(fp)
    file_cont = file.read()
    note = json.loads(file_cont)
    terms = []

    # Navigate json structure
    utt_pos = 0
    for doc in note["AllDocuments"]:
        for utterance in doc["Document"]["Utterances"]:
            # Find position of utterance
            for phrase in utterance["Phrases"]:
                if phrase["Mappings"]:
                    for mapping in phrase["Mappings"]:
                        for mc in mapping["MappingCandidates"]:
                            if mc["Negated"] != 1:
                                # Add matched words to return
                                umls_id = mc["CandidateCUI"]
                                terms.append(" ".join(mc["MatchedWords"]))
                                begin = utt_pos + int(mc["ConceptPIs"][0]["StartPos"])
                                length = int(mc["ConceptPIs"][0]["Length"])
                                end = begin + length
                                #print(utt_pos)
                                print(begin, end, umls_id, txt_f[begin:end].lower())
                                if umls_id in umls_conv:
                                    mm_dict[(begin, length)] = {"umls_id": umls_id,
                                                                "word": txt_f[begin:end].lower(),
                                                                "hpo id": umls_conv[umls_id]['HPO ID'],
                                                                "hpo term": umls_conv[umls_id]['Description']}
            if int(utterance["UttNum"]) == 1:
                utt_pos += int(utterance["UttStartPos"])
            utt_pos += int(utterance["UttLength"])
        utt_pos += 2
    return terms


# Opens a xmi file from ctakes and parses it to extract words
# TODO: Change to store start/end indices and CUID rather than words themselves

def read_ctakes(f, txt_f):
    global ctakes_dict
    tree = et.parse(f)
    # namespace for xml file
    names = {'textsem': 'http:///org/apache/ctakes/typesystem/type/textsem.ecore',
             'refsem': 'http:///org/apache/ctakes/typesystem/type/refsem.ecore',
             'xmi': 'http://www.omg.org/XMI'}
    # Find all relevant entries
    d = tree.findall('.//textsem:DiseaseDisorderMention', names)
    s = tree.findall('.//textsem:SignSymptomMention', names)
    all_terms = d + s
    terms = []
    for p in all_terms:
        if p.attrib['polarity'] != -1:
            # Find indices
            begin = int(p.attrib['begin'])
            end = int(p.attrib['end'])
            length = end - begin
            # Find CUI for UMLS term
            references = p.attrib['ontologyConceptArr'].split()
            umls_refs = set()
            for r in references:
                umls = tree.find('.//refsem:UmlsConcept[@xmi:id="' + r + '"]', names)
                umls_refs.add(umls.attrib['cui'])
            for r in umls_refs:
                if r in umls_conv:
                    ctakes_dict[(begin, length)] = {"umls_id": r, "word": txt_f[begin:end].lower(),
                                                    "hpo id": umls_conv[r]["HPO ID"],
                                                    "hpo term": umls_conv[r]["Description"]}
            # Extract word and add to return
            terms.append(txt_f[begin:end].lower())
    return terms


# Run on multiple or single file
readUMLSDict(umls_fp)
if single_file:
    createJSON(txt_fp, mm_fp, ctakes_fp, storage_fp, test_filename)
else:
    files = [x.split('\\')[-1] for x in glob.glob(txt_fp + '/*.txt')]
    for file in files:
        createJSON(txt_fp, mm_fp, ctakes_fp, storage_fp, file)

# Opens json file and stores the parent directory path as the mm_fp
# def update_mmdict():
#     global mm_fp
#     global mm_words
#     mm = filedialog.askopenfilename(
#         initialdir="C:/Users/MainFrame/Desktop/",
#         title="Open Meta Map Output file",
#         filetypes=(("Text Files", "*.json"),)
#     )
#     mm_fp = '/'.join(mm.split('/')[:-1])
#     mm_words = set(read_json(mm, txt_fp + '/' + mm.split('/')[-1][:-5] + '.txt'))
#     update_display()

# Opens xmi file and stores the parent directory path as the ctakes_fp to read all future xmi files from
# def update_ctakesdict():
#     global ctakes_fp
#     global ctakes_words
#     ctakes = filedialog.askopenfilename(
#         initialdir="C:/Users/MainFrame/Desktop/",
#         title="Open CTakes Output file",
#         filetypes=(("Text Files", "*.xmi"),)
#     )
#     ctakes_fp = '/'.join(ctakes.split('/')[:-1])
#     ctakes_words = set(read_ctakes(ctakes, txt_fp + '/' + ctakes.split('/')[-1][:-4] + '.txt'))
#     update_display()

# Saves note annotations (Good/Bad) as a json file before killing the program
# def saveFile():
#     tf = filedialog.asksaveasfilename(
#         #mode='w',
#         title="Save file",
#         defaultextension=".json"
#     )
#     with open(tf, "w") as outfile:
#         json.dump(notation_dict, outfile)
#     ws.destroy()


# #Creates GUI
# ws = Tk()
# ws.title("Term Viewer")
# ws.geometry("800x600")
# ws['bg'] = '#2a636e'
#
# # adding frame
# frame = Frame(ws)
# frame.pack(pady=10)
#
# # adding scrollbars
# ver_sb = Scrollbar(frame, orient=VERTICAL)
# ver_sb.pack(side=RIGHT, fill=BOTH)
#
# hor_sb = Scrollbar(frame, orient=HORIZONTAL)
# hor_sb.pack(side=BOTTOM, fill=BOTH)
#
# # Add annotation
# values = {"Bad": "0",
#           "Good": "1"}
# annotation = IntVar(ws)
# #annotation.set(OPTIONS[0])
#
# for (text, value) in values.items():
#     Radiobutton(frame, text=text, variable=annotation,
#                 value=value, indicator=0,
#                 background="grey").pack(ipadx = 20, ipady=5, side=RIGHT)
#
# #w = OptionMenu(frame, annotation, *OPTIONS)
# #w.pack()
#
# Button(
#     ws,
#     text="Previous",
#     command=prevFile
# ).pack(side=LEFT, expand=True, fill=X, padx=20)
#
# Button(
#     ws,
#     text="Next",
#     command=nextFile
# ).pack(side=LEFT, expand=True, fill=X, padx=20)
#
# # adding writing space
# txtarea = Text(frame, width=80, height=30)
# txtarea.pack(side=LEFT)
# txtarea.tag_configure("mm", background="#ffd5ab")
# txtarea.tag_configure("ctakes", background="#ffffab")
# txtarea.tag_configure("both", background="#afffab")
#
# # binding scrollbar with text area
# txtarea.config(yscrollcommand=ver_sb.set)
# ver_sb.config(command=txtarea.yview)
#
# txtarea.config(xscrollcommand=hor_sb.set)
# hor_sb.config(command=txtarea.xview)
#
# # adding path showing box
# pathh = Entry(ws)
# pathh.pack(expand=True, fill=X, padx=10)
#
# # adding buttons
# Button(
#     ws,
#     text="Open File",
#     command=openFile
# ).pack(side=LEFT, expand=True, fill=X, padx=20)
#
# Button(
#     ws,
#     text="Load Meta Map",
#     command=update_mmdict
# ).pack(side=LEFT, expand=True, fill=X, padx=20)
#
# Button(
#     ws,
#     text="Load CTakes",
#     command=update_ctakesdict
# ).pack(side=LEFT, expand=True, fill=X, padx=20)
#
# Button(
#     ws,
#     text="Exit",
#     command=lambda: saveFile()
# ).pack(side=LEFT, expand=True, fill=X, padx=20, pady=20)
#
# ws.mainloop()
