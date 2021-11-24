import tkinter
from tkinter import *
from tkinter import filedialog

mm_words = {"impaction", "diabetes", "Down Syndrome"}
ctakes_words = {"vascular", "cornea", "Down Syndrome"}
shared_words = []
total_mmcount = 0
total_ctakescount = 0
total_count = 0
ss_count = 0
dd_count = 0

# functions
def openFile():
    tf = filedialog.askopenfilename(
        initialdir="C:/Users/MainFrame/Desktop/",
        title="Open Text file",
        filetypes=(("Text Files", "*.txt"),)
    )
    pathh.insert(END, tf)
    tf = open(tf)
    file_cont = tf.read()
    txtarea.insert(END, file_cont)

    tf.close()
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
                            count=count, regexp=regexp)
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

def update_mmdict():
    pass
    # tf = filedialog.askopenfilename(
    #     initialdir="C:/Users/MainFrame/Desktop/",
    #     title="Open Meta Map Output file",
    #     filetypes=(("Text Files", "*.json"),)
    # )
    # pathh.insert(END, tf)
    # tf = open(tf)
    # file_cont = tf.read()
    #
    # #PARSE FILE
    # txtarea.insert(END, file_cont)
    #
    # tf.close()
    # update_display()

def update_ctakesdict():
    pass
    # tf = filedialog.askopenfilename(
    #     initialdir="C:/Users/MainFrame/Desktop/",
    #     title="Open CTakes Output file",
    #     filetypes=(("Text Files", "*.xmi"),)
    # )
    # pathh.insert(END, tf)
    # tf = open(tf)
    # file_cont = tf.read()
    # txtarea.insert(END, file_cont)
    #
    # tf.close()
    # update_display()

def saveFile():
    tf = filedialog.asksaveasfile(
        mode='w',

        title="Save file",
        defaultextension=".txt"
    )
    tf.config(mode='w')

    pathh.insert(END, tf)
    data = str(txtarea.get(1.0, END))
    tf.write(data)

    tf.close()


ws = Tk()
ws.title("Term Viewer")
ws.geometry("1000x800")
ws['bg'] = '#2a636e'

# adding frame
frame = Frame(ws)
frame.pack(pady=10)

# adding scrollbars 
ver_sb = Scrollbar(frame, orient=VERTICAL)
ver_sb.pack(side=RIGHT, fill=BOTH)

hor_sb = Scrollbar(frame, orient=HORIZONTAL)
hor_sb.pack(side=BOTTOM, fill=BOTH)

# adding writing space
txtarea = Text(frame, width=120, height=40)
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
    command=update_mmdict()
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Load CTakes",
    command=update_ctakesdict()
).pack(side=LEFT, expand=True, fill=X, padx=20)

Button(
    ws,
    text="Exit",
    command=lambda: ws.destroy()
).pack(side=LEFT, expand=True, fill=X, padx=20, pady=20)

ws.mainloop()