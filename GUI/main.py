import tkinter
from tkinter import *
from tkinter import filedialog
import json
import glob
import xml.etree.ElementTree as et

mm_dict = {}
ctakes_dict = {}
mm_words = set()  # {"impaction", "diabetes", "Down Syndrome"}
ctakes_words = set()  # {"vascular", "cornea", "Down Syndrome"}
shared_words = set()
total_mmcount = 0
total_ctakescount = 0
total_count = 0
ss_count = 0
dd_count = 0

txt_fp = "C:/Users/nixona2/Documents/test_notes/10147920.txt"
txt_files = []
mm_fp = ""
ctakes_fp = ""
currentFile = 0

notation_dict = {}


def nextFile():
    global currentFile, mm_words, ctakes_words
    notation_dict[txt_files[currentFile]] = annotation.get()
    print(notation_dict)
    currentFile += 1
    if currentFile < len(txt_files):
        new_fp = txt_fp + '/' + txt_files[currentFile]
        new_mm_fp = mm_fp + '/' + txt_files[currentFile][:-4] + '.json'
        new_ctakes_fp = ctakes_fp + '/' + txt_files[currentFile][:-4] + '.xmi'
        print(new_fp)
        print(new_mm_fp)
        print(new_ctakes_fp)
        tf = open(new_fp)
        file_cont = tf.read()
        txtarea.delete(1.0, END)
        pathh.delete(0, END)
        txtarea.insert(END, file_cont)
        pathh.insert(END, new_fp)
        tf.close()
        mm_words = set(read_json(new_mm_fp))
        ctakes_words = set(read_ctakes(new_ctakes_fp, new_fp))
        update_display()


def prevFile():
    global currentFile, mm_words, ctakes_words
    currentFile -= 1
    if currentFile >= 0:
        new_fp = txt_fp + '/' + txt_files[currentFile]
        new_mm_fp = mm_fp + '/' + txt_files[currentFile][:-4] + '.json'
        new_ctakes_fp = ctakes_fp + '/' + txt_files[currentFile][:-4] + '.xmi'
        print(new_fp)
        print(new_mm_fp)
        print(new_ctakes_fp)
        tf = open(new_fp)
        file_cont = tf.read()
        txtarea.delete(1.0, END)
        pathh.delete(0, END)
        txtarea.insert(END, file_cont)
        pathh.insert(END, new_fp)
        tf.close()
        mm_words = set(read_json(new_mm_fp))
        ctakes_words = set(read_ctakes(new_ctakes_fp, new_fp))
        update_display()


# functions
def openFile():
    global txt_fp, txt_files
    txt = filedialog.askopenfilename(
        initialdir="C:/Users/MainFrame/Desktop/",
        title="Open Text file",
        filetypes=(("Text Files", "*.txt"),)
    )
    pathh.insert(END, txt)
    tf = open(txt)
    file_cont = tf.read()
    txtarea.insert(END, file_cont)
    tf.close()
    txt_fp = '/'.join(txt.split('/')[:-1])
    txt_files = [x.split('\\')[-1] for x in glob.glob(txt_fp + '/*.txt')]
    print("Text filepath: " + txt_fp)
    print("List of files", txt_files)
    update_display()


def highlight_word(word, tag, start="1.0", end="end",
                   regexp=False):
    start = txtarea.index(start)
    end = txtarea.index(end)
    txtarea.mark_set("matchStart", start)
    txtarea.mark_set("matchEnd", start)
    txtarea.mark_set("searchLimit", end)

    count = tkinter.IntVar()
    while True:
        index = txtarea.search(word, "matchEnd", "searchLimit",
                               count=count, regexp=regexp, nocase=True)
        if index == "": break
        if count.get() == 0: break
        txtarea.mark_set("matchStart", index)
        txtarea.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
        txtarea.tag_add(tag, "matchStart", "matchEnd")


def update_display():
    for word in mm_words.intersection(ctakes_words):
        highlight_word(word, "both")
    for word in mm_words.difference(ctakes_words):
        highlight_word(word, "mm")
    for word in ctakes_words.difference(mm_words):
        highlight_word(word, "ctakes")


def read_json(fp):
    file = open(fp)
    file_cont = file.read()
    note = json.loads(file_cont)
    terms = []

    for doc in note["AllDocuments"]:
        for utterance in doc["Document"]["Utterances"]:
            for phrase in utterance["Phrases"]:
                if phrase["Mappings"]:
                    for mapping in phrase["Mappings"]:
                        for mc in mapping["MappingCandidates"]:
                            if mc["Negated"] != 1:
                                terms.append(" ".join(mc["MatchedWords"]))
    return terms


def read_ctakes(f, txt_f):
    global ctakes_dict
    tree = et.parse(f)
    d = tree.findall('.//{http:///org/apache/ctakes/typesystem/type/textsem.ecore}DiseaseDisorderMention')
    s = tree.findall('.//{http:///org/apache/ctakes/typesystem/type/textsem.ecore}SignSymptomMention')
    all_terms = d + s
    f = open(txt_f, "r")
    f = f.read()
    terms = []
    for p in all_terms:
        if p.attrib['polarity'] != -1:
            begin = int(p.attrib['begin'])
            end = int(p.attrib['end'])
            # ctakes_dict[(begin, end)] = {"umls_id": "not found"}
            terms.append(f[begin:end].lower())
    return terms


def update_mmdict():
    global mm_fp
    global mm_words
    mm = filedialog.askopenfilename(
        initialdir="C:/Users/MainFrame/Desktop/",
        title="Open Meta Map Output file",
        filetypes=(("Text Files", "*.json"),)
    )
    mm_fp = '/'.join(mm.split('/')[:-1])
    mm_words = set(read_json(mm))
    update_display()


def update_ctakesdict():
    global ctakes_fp
    global ctakes_words
    ctakes = filedialog.askopenfilename(
        initialdir="C:/Users/MainFrame/Desktop/",
        title="Open CTakes Output file",
        filetypes=(("Text Files", "*.xmi"),)
    )
    ctakes_fp = '/'.join(ctakes.split('/')[:-1])
    ctakes_words = set(read_ctakes(ctakes, txt_fp + '/' + ctakes.split('/')[-1][:-4] + '.txt'))
    update_display()


def saveFile():
    tf = filedialog.asksaveasfilename(
        #mode='w',
        title="Save file",
        defaultextension=".json"
    )
    with open(tf, "w") as outfile:
        json.dump(notation_dict, outfile)
    ws.destroy()


ws = Tk()
ws.title("Term Viewer")
ws.geometry("800x600")
ws['bg'] = '#2a636e'

# adding frame
frame = Frame(ws)
frame.pack(pady=10)

# adding scrollbars 
ver_sb = Scrollbar(frame, orient=VERTICAL)
ver_sb.pack(side=RIGHT, fill=BOTH)

hor_sb = Scrollbar(frame, orient=HORIZONTAL)
hor_sb.pack(side=BOTTOM, fill=BOTH)

# Add annotation
values = {"Bad": "0",
          "Good": "1"}
annotation = IntVar(ws)
#annotation.set(OPTIONS[0])

for (text, value) in values.items():
    Radiobutton(frame, text=text, variable=annotation,
                value=value, indicator=0,
                background="grey").pack(ipadx = 20, ipady=5, side=RIGHT)

#w = OptionMenu(frame, annotation, *OPTIONS)
#w.pack()

Button(
    ws,
    text="Previous",
    command=prevFile
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Next",
    command=nextFile
).pack(side=LEFT, expand=True, fill=X, padx=20)

# adding writing space
txtarea = Text(frame, width=80, height=30)
txtarea.pack(side=LEFT)
txtarea.tag_configure("mm", background="#ffd5ab")
txtarea.tag_configure("ctakes", background="#ffffab")
txtarea.tag_configure("both", background="#afffab")

# binding scrollbar with text area
txtarea.config(yscrollcommand=ver_sb.set)
ver_sb.config(command=txtarea.yview)

txtarea.config(xscrollcommand=hor_sb.set)
hor_sb.config(command=txtarea.xview)

# adding path showing box
pathh = Entry(ws)
pathh.pack(expand=True, fill=X, padx=10)

# adding buttons 
Button(
    ws,
    text="Open File",
    command=openFile
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Load Meta Map",
    command=update_mmdict
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Load CTakes",
    command=update_ctakesdict
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Exit",
    command=lambda: saveFile()
).pack(side=LEFT, expand=True, fill=X, padx=20, pady=20)

ws.mainloop()
