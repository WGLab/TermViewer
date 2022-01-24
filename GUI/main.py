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

# TODO: Make this editable in a config file for readability
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
        if word in ctakes_dict:
            ne_list.append({"py/object": "document.NamedEntity",
                            "type": "MetaMap and cTakes",
                            "text": "general",
                            "identifier": mm_dict[word]["umls_id"],
                            "offset": word[0],
                            "length": word[1],
                            "description": "*",
                            "algorithm": "MetaMap and cTakes"})
        else:
            ne_list.append({"py/object": "document.NamedEntity",
                            "type": "MetaMap",
                            "text": "general",
                            "identifier": mm_dict[word]["umls_id"],
                            "offset": word[0],
                            "length": word[1],
                            "description": "*",
                            "algorithm": "MetaMap"})
    for word in ctakes_dict:
        if word not in mm_dict:
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
                                # print(utt_pos)
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

# Load files and create jsons
readUMLSDict(umls_fp)
# Run on multiple or single file
if single_file:
    createJSON(txt_fp, mm_fp, ctakes_fp, storage_fp, test_filename)
else:
    files = [x.split('\\')[-1] for x in glob.glob(txt_fp + '/*.txt')]
    for file in files:
        createJSON(txt_fp, mm_fp, ctakes_fp, storage_fp, file)
