//
// InputPairMap object
//

/**
 * Manages a two-way map between paired radio buttons and text fields. Used by
 * event handlers on these fields to check/focus their sister fields when they
 * are checked/focused.
 */
function InputPairMap() {
	this.texts = new Object();
	this.radios = new Object();
}

InputPairMap.prototype = {
		/** Add a (radio button, text field) pair. */
		addPair : function(radioId, textId) {
			this.texts[textId] = radioId;
			this.radios[radioId] = textId;
		},
		
		/** Get object whose keys contain the text fields. */
		getTexts : function() { return this.texts; },
		/** Get object whose keys contain the radio buttons. */
		getRadios : function() { return this.radios; },
		
		/**
		 * Get the DOM text input element associated with the radio button with
		 * the given ID.
		 */
		getTextByRadioId : function(radioId) {
			return document.getElementById(this.radios[radioId]);
		},
		/**
		 * Get the DOM radio button element associated with the text input with
		 * the given ID.
		 */
		getRadioByTextId : function(textId) {
			return document.getElementById(this.texts[textId]);
		}
	};


//
// Setup
//

// Create global input pair map
var inputPairs = new InputPairMap();
inputPairs.addPair('id_input_source_dataset',  'id_input');
inputPairs.addPair('id_input_source_path',     'id_input_path');
inputPairs.addPair('id_input_source_upload',   'id_input_file');
inputPairs.addPair('id_input_source_input',    'id_input_text');
inputPairs.addPair('id_mapper_source_upload',  'id_mapper_file');
inputPairs.addPair('id_mapper_source_input',   'id_mapper');
inputPairs.addPair('id_reducer_source_upload', 'id_reducer_file');
inputPairs.addPair('id_reducer_source_input',  'id_reducer');


/**
 * Set up events for paired radio and text form elements. Must be called after
 * page is loaded in order for the elements to be found in the DOM tree.
 */
function setupEvents() {
	// Setup events on all radio objects
	for ( var radioId in inputPairs.getRadios() ) {
		var radio = document.getElementById(radioId);
		radio.onchange = onRadioChange;
	}
	
	// Setup events on all text objects
	for ( var textId in inputPairs.getTexts() ) {
		var textElem = document.getElementById(textId);
		
		// No event handler gives us exactly the behavior we want, but onfocus is
		// probably the best option
		textElem.onfocus = onTextFocus;
	}        
	
	// Setup event for tabs on inputRaw
	document.getElementById('id_input_text').onkeydown = captureTab;
	
	// Setup collapse events on all collapsable elements
	var collapsableElems = document.getElementsByClassName("collapsable");
	setupCollapsableElems(collapsableElems);
}

// Register setupEvents() for page load, also calling any previously-defined
// handler
var oldOnLoad = (window.onload) ? window.onload : function() { };
window.onload = function() { oldOnLoad(); setupEvents(); };

// Need this to make a new closure below
function makeClickHandler(id) {
	return function() { collapse(id); return false; }
}

function setupCollapsableElems(collapsableElems) {
	for (var i=0; i<collapsableElems.length; i++)
	{
		var elem = collapsableElems[i];
		var id = elem.id;
		var header = elem.getElementsByTagName("header")[0];
		var headerContents = header.childNodes[0];
		
		var anchor = document.createElement("a");
		anchor.setAttribute('href', '#');
		anchor.onclick = makeClickHandler(id);
		
		var img = document.createElement("img");
		img.setAttribute('src', mediaURL + "triangleUncollapsed.png");
		
		anchor.appendChild(img);
		anchor.appendChild(headerContents.cloneNode(true));
		header.replaceChild(anchor, headerContents);
	}
}


//
// Event handlers
//

/**
 * Event handler that focuses a radio button's corresponding text field if the
 * radio button is selected.
 */
function onRadioChange() {
	if (this.checked == true)
	{
		var textElem = inputPairs.getTextByRadioId(this.id);
		textElem.focus();
		textElem.select();
	}
}

/** Event handler that selects a text field's corresponding radio button. */
function onTextFocus() {
	inputPairs.getRadioByTextId(this.id).checked = true;
}

function captureTab(e) {
	// Get event object on IE
	if (!e)
		e = window.event;
	
	if (e.keyCode != 9)
		return true;
	else {
		// Get target element
		if (e.target)	// Mozilla
			targ = e.target;
		else if (e.srcElement) // Microsoft
			targ = e.srcElement;
		
		// Fix Safari text node bug
		if (targ.nodeType == 3)
			targ = targ.parentNode;
		
		// Replace selection with tab character
		if (targ.selectionStart || targ.selectionStart == '0') { // Mozilla
			var startPos = targ.selectionStart;
			var endPos = targ.selectionEnd;
			targ.value = targ.value.substring(0, startPos)
				+ "\t"
				+ targ.value.substring(endPos, targ.value.length);
			
			// Place cursor after tab
			targ.setSelectionRange(startPos + 1, startPos + 1);
		}
		else if (document.selection) { // Microsoft
			targ.focus();
			var range = document.selection.createRange();
			range.text = "\t";
			
			// Place cursor after tab
			range.collapse(false).select();
		}
		else { // Fallback
			targ.value += "\t";
		}

		return false;
	}
}

function collapse(id) {
        var section = document.getElementById(id);
        var content = section.getElementsByClassName("content")[0];
        var imgElement = section.getElementsByTagName("header")[0].getElementsByTagName("img")[0];
        
        var url = imgElement.getAttribute('src');
        var urlArray=url.split("/");
        var newUrl = "";
        for (i=0;i<=urlArray.length-2;i++)
                newUrl += urlArray[i] + "/";
        
	var sectionClasses = section.getAttribute("class");
	sectionClasses = sectionClasses ? sectionClasses : "";
        if(sectionClasses.indexOf("collapsed") != -1)
        {
		section.setAttribute("class",
			sectionClasses.replace("collapsed", ''));
                newUrl += "triangleUncollapsed.png";
        }
        else
        {
		section.setAttribute("class", sectionClasses + " collapsed");
                newUrl += "triangleCollapsed.png";
        }
        imgElement.setAttribute('src',newUrl);
        return false;
}
