import json
import glob
import xml.etree.ElementTree as et
import sys

# TODO: Make this editable in a config file for readability?
# Stores file path for each directory and the file names of the notes (extensions are replaced to get mm/ctakes files)
# Location of notes
txt_fp = "C:/Users/nixona2/Documents/test_notes/notes_pre/"
# Location of MetaMap output files (JSON format)
mm_fp = "C:/Users/nixona2/Documents/test_notes/mm_pre/"
# Location of cTakes files (XMI format)
ctakes_fp = "C:/Users/nixona2/Documents/test_notes/ctakes_pre/"
# Location of tagged note output (JSON format)
storage_fp = "C:/Users/nixona2/Documents/test_notes/out_pre/"
# Location of umls term dictionary (MRCONSO.RRF)
umls_fp = "C:/Users/nixona2/Documents/MRCONSO.RRF"

# Set to true to test on a single file
single_file = False
test_filename = "10147920"

# Dictionary for UMLS terms
umls_conv = {}

# Reads MRCONSO.RRF containing UMLS terms into dictionary
def readUMLSDict(fp):
    global umls_conv
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for l in lines:
        entry = l.split('|')
        if entry[11] == 'HPO':
            umls_conv[entry[0]] = {"HPO ID": entry[13], "Description": entry[14]}


# Reads MetaMap output file and note, returns dictionary of HPO terms mapped to note
def read_mm(fp, txt_f):
    mm_dict = {}
    with open(fp, 'r') as f:
        file_cont = f.read()
    note = json.loads(file_cont)
    # Navigate json structure
    doc_pos = 0
    for doc in note["AllDocuments"]:
        utt_pos = 0
        for utterance in doc["Document"]["Utterances"]:
            for phrase in utterance["Phrases"]:
                if phrase["Mappings"]:
                    for mapping in phrase["Mappings"]:
                        for mc in mapping["MappingCandidates"]:
                            if mc["Negated"] !="1":
                                # Add matched words to return
                                umls_id = mc["CandidateCUI"]
                                begin = doc_pos + int(mc["ConceptPIs"][0]["StartPos"])
                                length = int(mc["ConceptPIs"][0]["Length"])
                                end = begin + length
                                if umls_id in umls_conv:
                                    mm_dict[(begin, length)] = {"umls_id": umls_id,
                                                                "word": txt_f[begin:end].lower(),
                                                                "hpo_id": umls_conv[umls_id]['HPO ID'],
                                                                "hpo_term": umls_conv[umls_id]['Description']}
            #Track position of utterance
            if int(utterance["UttNum"]) == 1:
                utt_pos += int(utterance["UttStartPos"])
            utt_pos += int(utterance["UttLength"])
        doc_pos += 2 + utt_pos
    return mm_dict


# Opens a xmi file from ctakes and parses it to extract words
def read_ctakes(f, txt_f):
    ctakes_dict = {}
    tree = et.parse(f)
    # namespace for xml file
    names = {'textsem': 'http:///org/apache/ctakes/typesystem/type/textsem.ecore',
             'refsem': 'http:///org/apache/ctakes/typesystem/type/refsem.ecore',
             'xmi': 'http://www.omg.org/XMI'}
    # Find all relevant entries
    d = tree.findall('.//textsem:DiseaseDisorderMention', names)
    s = tree.findall('.//textsem:SignSymptomMention', names)
    all_terms = d + s
    for p in all_terms:
        if p.attrib['polarity'] != "-1":
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
                                                    "hpo_id": umls_conv[r]["HPO ID"],
                                                    "hpo_term": umls_conv[r]["Description"]}
    return ctakes_dict

# Creates JSON file that can be uploaded into Term Viewer
def createJSON(txt_fp, mm_fp, ctakes_fp, out_fp, doc_name):
    # load text file
    with open(txt_fp + doc_name + ".txt", 'r') as f:
        file_content = f.read()
    # load mm
    mm_dict = read_mm(mm_fp + doc_name + ".json", file_content)
    # load ctakes
    ctakes_dict = read_ctakes(ctakes_fp + doc_name + ".txt.xmi", file_content)
    ne_list = []
    for word in mm_dict:
        if word in ctakes_dict:
            ne_list.append({"py/object": "document.NamedEntity",
                            "type": "MetaMap and cTakes",
                            "text": "general",
                            "identifier": mm_dict[word]["hpo_id"],
                            "offset": word[0],
                            "length": word[1],
                            "description": mm_dict[word]["hpo_term"],
                            "algorithm": "MetaMap and cTakes"})
        else:
            ne_list.append({"py/object": "document.NamedEntity",
                            "type": "MetaMap",
                            "text": "general",
                            "identifier": mm_dict[word]["hpo_id"],
                            "offset": word[0],
                            "length": word[1],
                            "description": mm_dict[word]["hpo_term"],
                            "algorithm": "MetaMap"})
    for word in ctakes_dict:
        if word not in mm_dict:
            ne_list.append({"py/object": "document.NamedEntity",
                            "type": "CTakes",
                            "text": "general",
                            "identifier": ctakes_dict[word]["hpo_id"],
                            "offset": word[0],
                            "length": word[1],
                            "description": ctakes_dict[word]["hpo_term"],
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

def createEntry(txt_fp, mm_fp, ctakes_fp, doc_name):
    # load text file
    with open(txt_fp + doc_name + ".txt", 'r') as f:
        file_content = f.read()
    # load mm
    mm_dict = read_mm(mm_fp + doc_name + ".json", file_content)
    # load ctakes
    ctakes_dict = read_ctakes(ctakes_fp + doc_name + ".txt.xmi", file_content)
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
    result =  {"py/object": "document.Document",
               "note_val": "unknown",
               "note_read": "false",
               "data_struct_version": 1.0,
               "source_file": txt_fp + doc_name + ".txt",
               "doc_id": doc_name,
               "pmid": "",
               "pmcid": "",
               "publisher_item_identifier": "*",
               "doi": "",
               "license": "***",
               "title": "Patient Note: " + txt_fp + doc_name + ".txt",
               "abstract": "",
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
               "mesh_list": []}

    return result
    # with open(out_fp + doc_name + ".json", 'w') as f:
    #     json.dump(output, f)

print(sys.argv)
#Check for commandline arguments
if len(sys.argv) == 6:
    print("LOADING ARGS")	
    umls_fp = sys.argv[1]
    txt_fp = sys.argv[2]
    ctakes_fp = sys.argv[3]
    mm_fp = sys.argv[4]
    storage_fp = sys.argv[5]

print("RUNNING COMMAND")
# Load files and create jsons
readUMLSDict(umls_fp)
# Run on multiple or single file
if single_file:
    createJSON(txt_fp, mm_fp, ctakes_fp, storage_fp, test_filename)
else:
    files = [x.split('/')[-1][:-4] for x in glob.glob(txt_fp + '/*.txt')]
    output = []
    for file in files:
        print(file)
        output.append(createEntry(txt_fp, mm_fp, ctakes_fp, file))
    with open(storage_fp + "FolderOutput" + ".json", 'w') as f:
        json.dump(output, f)
