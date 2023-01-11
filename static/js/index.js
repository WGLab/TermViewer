"use strict";

var docID = 0;
let passageID = 0;
let totalDocs = 0;

let enableTagEdit = true;
let inputFileString = '';
let inputJsonObject = '';
let highlightedNamedEntityTypeDict = new Object();
let allNamedEntityTypeDict = new Object();
let allNamedEntityTypeList = [];
let segOffsetList = [];
let tagList = [];

function allEntitesAreReviewed() {
    for (let entityId = 0; entityId < inputJsonObject[docID].passage_list[passageID].named_entity_list.length; entityId++) {
        let entityType = inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].type;
        if (!(entityType in highlightedNamedEntityTypeDict)) { continue; }
        if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'unknown') {
            return false;
        }
    }
    return true;
}

function buttonPrevClicked() {

    if (passageID > 0) {
        passageID -= 1;
	    updateScore();
        display1PassageInMainBox();
    } else if (docID > 0) {
        docID -= 1;
        passageID = inputJsonObject[docID].passage_list.length - 1;
        updateScore();
        display1PassageInMainBox();
    } else {
        alert("This is the first passage!");
    }
}

function buttonResetClicked() {
    if (confirm("You annotations on THIS passage will be removed. You annotations on other passages will not be affected. Are you sure to continue? ")) {
        inputJsonObject[docID].passage_list[passageID].named_entity_list = JSON.parse(JSON.stringify(inputJsonObject[docID].passage_list[passageID].backup_named_entity_list));
        display1PassageInMainBox();
    }
}

function buttonNextClicked() {

	console.log("next clicked");

    if (passageID + 1 < inputJsonObject[docID].passage_list.length) {
        passageID += 1;
        updateScore();
        display1PassageInMainBox();
    } else if (docID + 1 < inputJsonObject.length) {
        docID += 1;
        passageID = 0;
	    updateScore();
        display1PassageInMainBox();
    } else {
        alert("This is the last passage!");
    }
}

function buttonSaveClicked() {
   //  download(inputJsonObject, 'named_entity_annotation.json', 'text/plain');

	let json = buildAnnotatedFile();
	json = [json]
	let blob1 = new Blob(json, { type: "text/plain;charset=utf-8" });

	let url = window.URL || window.webkitURL;
	let link = url.createObjectURL(blob1);
	let a = document.createElement("a");
	a.download = "text1.txt";
	a.href = link;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
}

function buildAnnotatedFile() {

	let note_path = inputJsonObject[docID].source_file;
	let evaluator = document.getElementById('name').value;

	// remove first element and reverse order
	let segOffsetList_shifted = segOffsetList.slice(1);
	let segOffsetList_reversed = segOffsetList_shifted.slice().reverse();

	// convert to array to enable editing
	let j = inputJsonObject[docID].passage_list[0].passage_text;
	j = j.split("");

	$.ajaxSetup({
    		async: false
	});

	for(let i=0; i<segOffsetList_reversed.length; i+=2){
        	$.getJSON($SCRIPT_ROOT + '/get_tag_score', {
        		path: note_path,
        		evaluator: evaluator,
        		offset: segOffsetList_reversed[i+1],
        		tag_length: segOffsetList_reversed[i]
    	}, function(response) {
        	console.log(response.score);
        	if(response.score == 1){
            	j.splice(segOffsetList_reversed[i+1],0, "+++");
            	j.splice(segOffsetList_reversed[i]+1,0, "+++");
            	console.log("+");
        }
        else if(response.score == 0){
            	j.splice(segOffsetList_reversed[i+1],0, "---");
            	j.splice(segOffsetList_reversed[i]+1,0, "---");
            	console.log("-");
        }
        console.log('GET successful');
    		});

	}

	$.ajaxSetup({
    		async: true
	});

	j = j.join("");
	return j;
}

function download(content, fileName, contentType) {
   // const a = document.createElement("a");
   // a.href = URL.createObjectURL(new Blob([JSON.stringify(content, null, 2)], { type: contentType }));
   // a.setAttribute("download", fileName);
   // document.body.appendChild(a);
   // a.click();
   // document.body.removeChild(a);
}



function loadInputJsonFile(event) {

    document.getElementById('namedEntityTypeSelection').innerHTML = '';
    document.getElementById('showColor').innerHTML = '';
    document.getElementById('mainRegion').innerHTML = '';
    document.getElementById('start_btn').style.display = 'none';

    docID = 0;
    passageID = 0;

    inputFileString = '';
    inputJsonObject = '';
    highlightedNamedEntityTypeDict = new Object();
    allNamedEntityTypeDict = new Object();
    allNamedEntityTypeList = [];

    var file_path = document.getElementById("patient_file").value;

    $.getJSON($SCRIPT_ROOT + '/get_file', {
        path: file_path
        }, function(response) {
            console.log('GET successful, file received');	
            inputJsonObject = JSON.parse(response.result);
            preprocessingInputJsonObject(inputJsonObject);
        });


}

function preprocessingInputJsonObject(inputJsonObject) {

    totalDocs = inputJsonObject.length
    console.log("Total Docs read as: " + totalDocs)
    console.log("Length: " + inputJsonObject.length)

    for (let i = 0; i < inputJsonObject.length; i++) // i: docID 
    {
        for (let j = 0; j < inputJsonObject[i].passage_list.length; j++) // j: passageID
        {
            for (let k = 0; k < inputJsonObject[i].passage_list[j].named_entity_list.length; k++) {
                if (inputJsonObject[i].passage_list[j].named_entity_list[k].status == undefined) {
                    inputJsonObject[i].passage_list[j].named_entity_list[k].status = 'unknown';
                }
                // count number of named entities in each type

                if (inputJsonObject[i].passage_list[j].named_entity_list[k].type == 'DNAMutation') {
                    inputJsonObject[i].passage_list[j].named_entity_list[k].type = 'SNP/Indel';
                }
                if (inputJsonObject[i].passage_list[j].named_entity_list[k].type == 'ProteinMutation') {
                    inputJsonObject[i].passage_list[j].named_entity_list[k].type = 'SNP/Indel';
                }
                if (inputJsonObject[i].passage_list[j].named_entity_list[k].type == 'SNP') {
                    inputJsonObject[i].passage_list[j].named_entity_list[k].type = 'SNP/Indel';
                }
                if (allNamedEntityTypeDict[inputJsonObject[i].passage_list[j].named_entity_list[k].type]) {
                    if (inputJsonObject[i].passage_list[j].named_entity_list[k].status != 'deleted') {
                        allNamedEntityTypeDict[inputJsonObject[i].passage_list[j].named_entity_list[k].type] += 1;
                    }
                } else {
                    allNamedEntityTypeDict[inputJsonObject[i].passage_list[j].named_entity_list[k].type] = 1;
                }

                // calculate start and end position

                if ('start' in inputJsonObject[i].passage_list[j].named_entity_list[k] && 'end' in inputJsonObject[i].passage_list[j].named_entity_list[k]) {
                    continue;
                } else if ('offset' in inputJsonObject[i].passage_list[j].named_entity_list[k]) {
                    inputJsonObject[i].passage_list[j].named_entity_list[k].start = inputJsonObject[i].passage_list[j].named_entity_list[k].offset - inputJsonObject[i].passage_list[j].offset;
                    inputJsonObject[i].passage_list[j].named_entity_list[k].end = inputJsonObject[i].passage_list[j].named_entity_list[k].start + inputJsonObject[i].passage_list[j].named_entity_list[k].length;
                } else {
                    alert('ERROR! unknown position of named entities!');
                }

            }
            // sort named entities by start position
            inputJsonObject[i].passage_list[j].named_entity_list.sort(compareStartPosition);
            inputJsonObject[i].passage_list[j].backup_named_entity_list = JSON.parse(JSON.stringify(inputJsonObject[i].passage_list[j].named_entity_list));
        }
    }
    if (!("MetaMap" in allNamedEntityTypeDict)) {
        allNamedEntityTypeDict["MetaMap"] = 0;
    }
    if (!("CTakes" in allNamedEntityTypeDict)) {
        allNamedEntityTypeDict["CTakes"] = 0;
    }

    if (!("MetaMap and cTakes" in allNamedEntityTypeDict)) {
        allNamedEntityTypeDict["MetaMap and cTakes"] = 0;
    }


    let type;
    let count;
    let namedEntityTypeSelectionInfo = "<h3>Please check the named entity types that you want to highlight: </h3>";
    for (type in allNamedEntityTypeDict) {
        allNamedEntityTypeList.push(type);
    }

    for (let i = 0; i < allNamedEntityTypeList.length; i++) {
        type = allNamedEntityTypeList[i];
        count = allNamedEntityTypeDict[type];
        namedEntityTypeSelectionInfo += `<label class="checkboxLabel"><input type="checkbox" class="largeCheckbox" name="selectNamedEntityTypes" checked>${type} (count: ${count} )</label><br>`;

    }

    namedEntityTypeSelectionInfo += '<br><button type="button" id = "buttonConfirmSelection" onclick="confirmSelection()" >Confirm selection</button> &nbsp; &nbsp;'
    namedEntityTypeSelectionInfo += '<button type="button" id = "buttonResetSelection" onclick="resetSelection()" >Clear</button><br><br>'

    document.getElementById('namedEntityTypeSelection').innerHTML = namedEntityTypeSelectionInfo;
}

function resetSelection() {
    clearHTMLAfterResetSelection();
    let checkboxSelectNamedEntityTypes = document.getElementsByName("selectNamedEntityTypes");
    for (let i = 0; i < checkboxSelectNamedEntityTypes.length; i++) {
        if (checkboxSelectNamedEntityTypes[i].checked) {
            checkboxSelectNamedEntityTypes[i].checked = false;
        }
    }
}

function confirmSelection() {
    let checkboxSelectNamedEntityTypes = document.getElementsByName("selectNamedEntityTypes");
    let numCheckedItems = 0;
    let type;
    for (let i = 0; i < checkboxSelectNamedEntityTypes.length; i++) {
        if (checkboxSelectNamedEntityTypes[i].checked) {
            numCheckedItems += 1;
        }
    }
    if (numCheckedItems > 7) {
        alert("You can select at most 7 types!");
        return
    }
    if (numCheckedItems == 0) {
        alert("You must select at least one type!");
        return
    }

    highlightedNamedEntityTypeDict = new Object();
    for (let i = 0; i < checkboxSelectNamedEntityTypes.length; i++) {
        type = allNamedEntityTypeList[i];
        if (checkboxSelectNamedEntityTypes[i].checked) {
            highlightedNamedEntityTypeDict[type] = 1;
        }
    }

    showColorForNamedEntities();
    initMainRegion();
    console.log('Finished Initiating');
    display1PassageInMainBox();
    return;
}


function showColorForNamedEntities() {

    let typeId = 0;
    let entityType;
    for (entityType in highlightedNamedEntityTypeDict) {
        highlightedNamedEntityTypeDict[entityType] = typeId;
        typeId += 1;
    }

}

//Get score from server and use it to create tag
function updateScore() {
    let note_path = inputJsonObject[docID].source_file;
    let evaluator = document.getElementById('name').value;

    $.getJSON($SCRIPT_ROOT + '/get_score', {
        path: note_path,
        evaluator: evaluator
        }, function(response) {
	    console.log(response.score);
            console.log('GET successful');
            displayDocumentInfo(response.score)
        });
}

function updateTagScore(entityId, offset, length) {
    let note_path = inputJsonObject[docID].source_file;
    let evaluator = document.getElementById('name').value;

    $.getJSON($SCRIPT_ROOT + '/get_tag_score', {
        path: note_path,
        evaluator: evaluator,
        offset: offset,
        tag_length: length
        }, function(response) {
	    console.log(response.score);
            console.log('GET successful');
            displayTagInfo(entityId, offset, length, response.score)
        });
}

function initMainRegion() {
    docID = 0;
    passageID = 0;

    let mainRegionHTML = '<br>';


    mainRegionHTML += '<button class="largeButton" id="buttonPrev" onclick="buttonPrevClicked()">&#10094;   Previous passage</button> &nbsp;&nbsp;';
   // mainRegionHTML += '<button class="largeButton " id="buttonReset" onclick="buttonResetClicked()">Reset passage</button> &nbsp;&nbsp;';
    mainRegionHTML += '<button class="largeButton" id="buttonNext" onclick="buttonNextClicked()" >Next passage  &#10095;</button><br><br>';
    mainRegionHTML += '&nbsp;&nbsp; <button class="largeButton" id="buttonNext" onclick="buttonSaveClicked()" >Save</button><br><br>';
    mainRegionHTML += '<strong><span id="docTitle"></span></strong><br><br>';
    //Create tag
    mainRegionHTML += '<strong> Is this a good note? </strong>';
    mainRegionHTML += '<div id="docLabel"></div>';
   
    console.log('Initiating main region');

    mainRegionHTML += '<pre><div id="mainBox" class="mainbox">Here is the main text</div></pre>';
    mainRegionHTML += '<div id="labelNamedEntities"></div>'
    mainRegionHTML += '<br><br>showing passage <span id="passageID" class="docInfoSpan" >0</span> of document <span id="docID" class="docInfoSpan" >0</span> out of <span id="totalDocs" class="docInfoSpan" >0</span>.';
    //mainRegionHTML += '&nbsp;&nbsp;&nbsp;&nbsp;PMID: <span id="pmid" class="docInfoSpan" >N.A.</span>&nbsp;&nbsp;&nbsp;&nbsp;PMCID: <span id="pmcid" class="docInfoSpan" >N.A.</span></p>';
    document.getElementById('mainRegion').innerHTML = mainRegionHTML;
    //Gets score and displays doc info
    updateScore();
}

function displayDocumentInfo(score) {
    document.getElementById('docTitle').innerHTML = inputJsonObject[docID].title;
    document.getElementById('passageID').innerHTML = (passageID + 1).toString();
    document.getElementById('docID').innerHTML = (docID + 1).toString();
    document.getElementById('totalDocs').innerHTML = (totalDocs + 1).toString();

    let labelHTML = "";

    if (score == 0) {
        labelHTML += `<span id="docAnnotation" onclick="changeDocStatus(${docID}, ${score})" class="yesNoUnk noLabel">N</span></div><br><br>`;
    } else if (score == 1) {
        labelHTML += `<span id="docAnnotation" onclick="changeDocStatus(${docID}, ${score})" class="yesNoUnk yesLabel">Y</span></div><br><br>`;
    } else {
		score = -1

		console.log('GOT UNKNOWN VAL')
        labelHTML += `<span id="docAnnotation" onclick="changeDocStatus(${docID}, ${score})" class="yesNoUnk unkLabel">?</span></div><br><br>`;
    }

    document.getElementById('docLabel').innerHTML = labelHTML;
}

function clearHTMLAfterResetSelection() {
    document.getElementById('showColor').innerHTML = '';
    document.getElementById('mainRegion').innerHTML = '';
}

function compareStartPosition(a, b) {
    if (a.start > b.start) return 1;
    if (b.start > a.start) return -1;
}

function displayTagInfo(id, entityStartPos, entityEndPos, score) {
    let yesNoLabel = '';
    if (score == 0) {
        yesNoLabel = `N`;
    } else if (score == 1) {
        yesNoLabel = `Y`;
    } else {
		score = -1

		console.log('GOT UNKNOWN VAL')
        yesNoLabel = `?`;
    }
    console.log(`tag_${id}`);
	console.log(`start ${entityStartPos}`)
	console.log(`end ${entityEndPos}`)
	console.log(`score ${score}`)
    document.getElementById(`tag_${id}`).innerHTML = `<span onclick="changeEntityStatus(${id}, ${entityStartPos}, ${entityEndPos}, ${score})" class="yesNoUnk unkLabel">${yesNoLabel}</span>`;
}

function display1PassageInMainBox() {

    let passageText = inputJsonObject[docID].passage_list[passageID].passage_text;
    let highlightedText = '';
    let plainTextStartPos = 0;
    let plainTextEndPos;
    let entityStartPos;
    let entityEndPos;
    let plainText;
    let entityText;
    let segId = 0;
    let entityType;
    let typeId;
    let entityTooltip;
    segOffsetList = [];
    for (let entityId = 0; entityId < inputJsonObject[docID].passage_list[passageID].named_entity_list.length; entityId++) {
        entityType = inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].type;
        if (!(entityType in highlightedNamedEntityTypeDict)) { continue; }
        if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'deleted') { continue; }

        entityStartPos = inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].start;
        entityEndPos = inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].end;
        plainTextEndPos = entityStartPos;
        if (plainTextEndPos < plainTextStartPos) {
            plainTextEndPos = plainTextStartPos;
        }

        typeId = highlightedNamedEntityTypeDict[entityType];
        plainText = passageText.substring(plainTextStartPos, plainTextEndPos);
        highlightedText += `<span id="seg_${segId}">${plainText}</span>`;
        segId += 1;
        segOffsetList.push(plainTextStartPos);
        entityText = passageText.substring(entityStartPos, entityEndPos);
        entityTooltip = inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].identifier;
	let yesNoLabel = '';

        if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'false') {
            yesNoLabel = `<span onclick="changeEntityStatus(${entityId}, del=false)" class="yesNoUnk noLabel">N</span>`;
        } else if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'true') {
           yesNoLabel = `<span onclick="changeEntityStatus(${entityId}, del=false)" class="yesNoUnk yesLabel">Y</span>`;
        } else {
            yesNoLabel = `<span onclick="changeEntityStatus(${entityId}, del=false)" class="yesNoUnk unkLabel">?</span>`;
        }

       let trash_button = `<i class="fa fa-trash trashButton" onclick="changeEntityStatus(${entityId}, del=true)"></i>`;

//        if(enableTagEdit){
//            yesNoLabel = `<span onclick="changeEntityStatus(${entityId}, ${entityStartPos}, ${entityEndPos})" class="yesNoUnk unkLabel">?</span>`;
//            highlightedText += `<mark class="namedEntity color${typeId}" id="seg_${segId}"><span id="tag_${entityId}"></span>${entityText}</mark>`;
//            updateTagScore(entityId, entityStartPos, entityEndPos);
//        } else {
           // highlightedText += `<mark class="namedEntity color${typeId} tooltip" id="seg_${segId}">${entityText}<span class="tooltiptext">${entityTooltip}</span></mark>`;
//        }
        //highlightedText += `<mark class="namedEntity color${typeId} tooltip" id="seg_${segId}">${entityText}<span class="tooltiptext">${entityTooltip}</span></mark>`;
	highlightedText += `<mark class="namedEntity color${typeId}" id="seg_${segId}">${yesNoLabel}${entityText}${trash_button}</mark>`;
	segId += 1;
        segOffsetList.push(entityStartPos);

        plainTextStartPos = entityEndPos;
        if (entityEndPos > passageText.length) {
            alert('ERROR! end position of named entity is larger than text length!')
            return;
        }

    }
    if (plainTextStartPos < passageText.length) {
        plainText = passageText.substring(plainTextStartPos);
        highlightedText += `<span id="seg_${segId}">${plainText}</span>`;
        segOffsetList.push(plainTextStartPos);
        segId += 1;
    }
    document.getElementById('mainBox').innerHTML = highlightedText;
    console.log(highlightedText);
    displayLabelButtons();
}

function displayLabelButtons() {

    let typeId;
    let entityType;
    document.getElementById('labelNamedEntities').innerHTML = '<h3>All tags are from the sources below:</h3>';
    for (entityType in highlightedNamedEntityTypeDict) {
        typeId = highlightedNamedEntityTypeDict[entityType];
        document.getElementById('labelNamedEntities').innerHTML += `<button class="namedEntityButton color${typeId}" id="buttonLabelNamedEntity${typeId}" >${entityType}</button> &nbsp; &nbsp; &nbsp; &nbsp;`;
    }

}

function changeDocStatus(docID, current_score) {

    var note_path = inputJsonObject[docID].source_file
    var evaluator = document.getElementById('name').value
    var new_score;

    if (current_score == 1) {
        new_score = 0;
    } else if (current_score == -1) {
        new_score = 1;
    } else if (current_score == 0) {
        new_score = -1;
    } else {
        alert('ERROR! unknown entity status!');
    }

    console.log(note_path);
    console.log(evaluator);
    console.log(new_score);
    
    $.getJSON($SCRIPT_ROOT + '/set_score', {
        path: note_path,
        evaluator: evaluator,
	    score: new_score
        }, function(response) {
            console.log('Updated Score');
 	        updateScore();
        });
}

function addNamedEntityAnnotation(entityType) {
    if (!(window.getSelection)) {
        alert('Please select text first');
        return;
    }

    let selectedTextString = window.getSelection().toString();

    if (selectedTextString.length < 1) {
        alert('Please select text first');
        return;
    }

    let range = window.getSelection().getRangeAt(0);
    let startContainerParentNodeID = range.startContainer.parentNode.id;
    let endContainerParentNodeID = range.endContainer.parentNode.id;

    if (startContainerParentNodeID.substring(0, 4) != "seg_" || endContainerParentNodeID.substring(0, 4) != "seg_") {
        alert('Selected text is NOT in outside the box');
        return;
    }

    let startSegID = parseInt(startContainerParentNodeID.substring(4));
    let endSegID = parseInt(endContainerParentNodeID.substring(4));

    let namedEntity = new Object();
    namedEntity.type = entityType;
    namedEntity.start = range.startOffset + segOffsetList[startSegID];
    namedEntity.end = range.endOffset + segOffsetList[endSegID];
    namedEntity.offset = parseInt(namedEntity.start) + parseInt(inputJsonObject[docID].passage_list[passageID].offset);
    namedEntity.text = inputJsonObject[docID].passage_list[passageID].passage_text.substring(namedEntity.start, namedEntity.end);
    namedEntity.status = 'true';
    namedEntity.algorithm = "manual_annotation";
    inputJsonObject[docID].passage_list[passageID].named_entity_list.push(namedEntity);
    inputJsonObject[docID].passage_list[passageID].named_entity_list.sort(compareStartPosition);
    display1PassageInMainBox();
}

//function changeEntityStatus(entityId, offset, length, current_score) {
//
//    var note_path = inputJsonObject[docID].source_file
//    var evaluator = document.getElementById('name').value
//    var new_score;

//    if (current_score == 1) {
//        new_score = 0;
//    } else if (current_score == -1) {
//        new_score = 1;
//    } else if (current_score == 0) {
//        new_score = -1;
//    } else {
//        alert('ERROR! unknown entity status!');
//    }

//    console.log(note_path);
//    console.log(evaluator);
//    console.log(new_score);
//    console.log(offset);
//    console.log(length);

//    $.getJSON($SCRIPT_ROOT + '/set_tag_score', {
//        path: note_path,
//        evaluator: evaluator,
//        offset: offset,
//        tag_length: length,
//	    score: new_score
//        }, function(response) {
//            console.log('Updated Score');
// 	        updateTagScore(entityId, offset, length);
//        });
//}

function changeEntityStatus(entityId, del = false) {
	if (del) {
        if (confirm("Are you sure to delete this entity? This action cannot be undone.")) {
            inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status = 'deleted';
} else {
            return;
        }
    } else if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'true') {
        inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status = 'false';
    } else if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'unknown') {
        inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status = 'true';
    } else if (inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status == 'false') {
        inputJsonObject[docID].passage_list[passageID].named_entity_list[entityId].status = 'unknown';
    } else {
       alert('ERROR! unknown entity status!');
    }

    display1PassageInMainBox();
    return;
}

document.getElementById('start_btn').addEventListener('click', loadInputJsonFile);
//document.getElementById('patient_file').addEventListener('change', loadInputJsonFile);
