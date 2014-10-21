/**
 * Sort functions based on their names.
 * Store all ajaxes calls in a array so they can be aborted via onbeforeunload(ajaxarray.abort)
 * Inconsistent functionnameingscheme
 * 
 * Logging:
 * Change logging to store in array.
 * - Display only a max amount on webpage. 5 rows or something
 * - Add a link to show entire log in new window!
 *
 * Check if DevTools exists
 * - Do a GetVersion and check that it is the right one.
 * - If it is not or the pass is wrong, lock functions.
 * - If it does not exist, lock functions.
 * - DevtoolsExist = false;
 *
 *
 * Add /library/sections/1/refresh?force=1 link to each section..
 * Add option to refetch section data after deletion.
 
 *
 * Rating is for sorting of results i think...
 * Add ShowRatingKey (Only the number and not the entire key string)
 * Add ShowKey (Entire Key)
 * Add SeasonRatingKey
 * Add SeasonKey (Entire Key)
 * Store requested page and use that for "go back" feature?.. But how.... Multiple steps etc.
 * Add special search for shows. Search in title of show and episode.
 *
 * Only works in Chrome!
 * IE fails.
 *
 *
 *                      Add function to check that log_to_console is available. Move these things to a combined function.
 *                      Clean up log_to_console calls.
 *
 * 
 */


//Define some variables
var sections = []; // Holds all the available sections
var section_contents = []; // Holds the contents of the currently selected section.
var current_page = 0; // Always default to 0

var presentable_contents = []; // Holds the contents after they have gone through the options-machine.
var searchstring = "";
var log = [];
var log_show_amount = 5;

var selected_section = 0;

var providerarray = [];
providerarray[0] = "com.plexapp.agents.opensubtitles.xml";
providerarray[1] = "com.plexapp.agents.podnapisi.xml";

var delete_subtitle_array_queue = [];
var delete_subtitle_array_completed = [];


// Called to check for duplicates in providers xml files.
function check_duplicates(item_number) {
	for(i=0;i<providerarray.length;i++) {
		plexpath = PathToPlexMediaFolder.replace(/\\/g,"/");
		var pathToProviderXML = plexpath + "/Media/localhost/" + section_contents[item_number].hash.substr(0,1) + "/" + section_contents[item_number].hash.substr(1) + ".bundle/Contents/Subtitle Contributions/"+providerarray[i];
		console.log("Fetching XML from: " + pathToProviderXML);
		
		$.ajax({
				type: "GET",
				url: baseurl + utility + "?Func=PathExists&Secret="+Secret+"&Path="+pathToProviderXML,
				dataType: "text",
				success: function(data) {
					if(data == "true") {
						$.ajax({
							type: "GET",
							url: baseurl + utility + "?Func=GetXMLFile&Secret="+Secret+"&Path="+pathToProviderXML,
							dataType: "xml",
							success: function(data) {
								//xmlString = (new XMLSerializer()).serializeToString(data);
								//console.log(xmlString);

								var found = [];
								$(data).find("Subtitle").each(function() {
									//console.log("Checking : " + $(this).attr("name"));
									var Subtitle_one_name = $(this).attr("name");
									var Subtitle_one_media = $(this).attr("media");

									$(data).find("Subtitle").each(function() {
										var locationOfsid_two = $(this).attr("name").indexOf("/sid");
										var locationOfsid_one = $(this).attr("name").indexOf("/sid");
										if($(this).attr("name") != Subtitle_one_name) {

											if($(this).attr("name").substring(0,locationOfsid_two) == Subtitle_one_name.substring(0,locationOfsid_one)) {
												if(found.indexOf($(this).attr("media")) == -1) {
													found.push($(this).attr("media"));
													//console.log("Double!!!! " + $(this).attr("name")  + " ::: " + Subtitle_one_name);
												}

											}

										}
									});
									for (x=0;x<section_contents[item_number].subtitles.length;x++) {
										for (y=0;y<found.length;y++) {
											//console.log("Comparing: " + section_contents[item_number].subtitles[x].title + " [AND] " + found[y]);
											if(section_contents[item_number].subtitles[x].title.indexOf("_"+found[y]) != -1) {
												//console.log("Highlighted " + section_contents[item_number].subtitles[x].title + " as duplicate");
												section_contents[item_number].subtitles[x].isDuplicate = true;
											}
										}
									}
									// Go through the subtitles for supplied video, search for a filename that is the same as the media stored in found array.
								});

							},
							error: function(data, status, statusText, responsText) {
								console.log("Error in check_duplicates: " + statusText);
							},
						});
					}
				},
			});
	}
}

function check_exists(item_number) {
 /* For each subtitle for the item_number (movie that is)
  * check if that subtitles file exists
  */
	console.log(" Am i even here???? With item_number: " + item_number + " number of subtitles: " + section_contents[item_number].subtitles.length);
	for (i=0;i<section_contents[item_number].subtitles.length;i++) {
		subtitle = section_contents[item_number].subtitles[i];
		path = subtitle.url.replace(/\\/g,"/");
		console.log("checking to see if: " + path);
		if (path.indexOf("media:") == -1) {
			// it's a local file
			path = path.substr(7);
			
		 } else if (path.indexOf("file:") == -1) {
			// it's a agent file
			path = PathToPlexMediaFolder+append+path.substr(8);
		 }
		 
		if(path.length>0) { 
			$.ajax({
				type: "GET",
				url: baseurl + utility + "?Func=PathExists&Secret="+Secret+"&Path="+path,
				dataType: "text",
				subtitleIndex: i,
				success: function(data) {
					console.log("Subtitle: " + section_contents[item_number].subtitles[this.subtitleIndex].title + " exists: " + data);
					if(data == "false") {
						section_contents[item_number].subtitles[this.subtitleIndex].exists = false;
					}
				},
				error: function(data, status, statusText, responsText) {
					console.log("Error in check_exists: " + statusText);
				},
			});
		}
	}
}


// This is the inital function. This is called upon page loading to populate the sections table with the available sections.
function list_sections() {
	start_timer();
	$("#LibraryBox table").html(loadingScreen);
	$("input[name=items_per_page]").val(items_per_page);
	$.ajax({
		type: "GET",
		url: baseurl + "/library/sections",
		dataType: "xml",
		global: false,
		success: function(data) {
			//xmlString = (new XMLSerializer()).serializeToString(data);
			//log_to_console(xmlString);
			$("#LibraryBox table").html("");
			$(data).find("Directory").each(function() {
				targetFunction = false;
				if ($(this).attr("type") == "movie") {
					targetFunction = "list_movies";
				} else if ($(this).attr("type") == "show") {
					targetFunction = "list_shows_and_seasons";
				}

				if (targetFunction !== false) {
					$("#LibraryBox table").append("<tr class='hovering'><td class='mainText'><span class='link' onclick='" + targetFunction + "(" + $(this).attr("key") + ", this);'>" + $(this).attr("title") + "</span></td></tr>");
					section = {
						key: $(this).attr("key"),
						title: $(this).attr("title"),
						type: $(this).attr("type"),
						refreshing: false
					};
					sections.push(section);
				}
			});
			end_timer();
			log_add("Finished loading sections.");
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		},
	});
}

function list_movies(LibraryKey, TriggeringElement) {
	start_timer();
	fetchSettings();
	reset_variables();
	if(TriggeringElement !== false) {
		current_section = get_section_info(LibraryKey);
		update_section_box(current_section.key, TriggeringElement);
		targetURL = "/library/sections/" + current_section.key + "/all";
		log_to_console("Loading section: " + current_section.title);
	} else {
		targetURL = LibraryKey + "/all";
		log_to_console("Loading section key: " + targetURL);		
	}

	subtitles = [];

	$.ajax({
		type: "GET",
		async: true,
		url: baseurl + targetURL,
		dataType: "xml",
		success: function(data) {
			xmlString = (new XMLSerializer()).serializeToString(data);
			log_to_console(xmlString);

			$(data).find("Video").each(function() {
				//log_to_console("For each Video: " + $(this).attr("title"));
				// For each item in the section, call the key+"/tree"
				item = new Video();
				item.title = $(this).attr("title");
				item.key = $(this).attr("key");
				item.type = $(this).attr("type");
				item.id = $(this).attr("ratingKey");

				section_contents.push(item);
				//log_to_console(section_contents[section_contents.length - 1].title);
				ajax_get_item_tree(section_contents.length - 1);
				ajax_get_active_subtitle(section_contents.length - 1);
			});
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		},
	});
}

function list_shows_and_seasons(LibraryKey, TriggeringElement) {
	start_timer();
	fetchSettings();
	reset_variables();
	
	if(TriggeringElement !== false) {
		current_section = get_section_info(LibraryKey);
		update_section_box(current_section.key, TriggeringElement);
		targetURL = "/library/sections/" + current_section.key + "/all";
		log_to_console("Loading section: " + current_section.title);
	} else {
		targetURL = LibraryKey + "/all";
		log_to_console("Loading section key: " + targetURL);		
	}

	$.ajax({
		type: "GET",
		async: true,
		url: baseurl + targetURL,
		dataType: "xml",
		success: function(data) {
			xmlString = (new XMLSerializer()).serializeToString(data);
			log_to_console(xmlString);
	
			console.log("Outside of find!");
			$(data).find("Directory").each(function() {
				console.log("Inside of Find!");
				//log_to_console("For each Video: " + $(this).attr("title"));
				// For each item in the section, call the key+"/tree"
				item = new Video();
				item.title = $(this).attr("title");
				item.key = $(this).attr("key");
				
				if(item.key.indexOf("allLeaves") == -1) {
					item.type = $(this).attr("type");
				} else {
					item.type = "season";
				}
				console.log(item);
				section_contents.push(item);
				//log_to_console(section_contents[section_contents.length - 1].title);
				//ajax_get_item_tree(section_contents.length - 1);
			});
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		},
	});	
}

function ajax_get_item_tree(item_number) {
	//log_to_console(section_contents[item_number].key);
	$.ajax({
		type: "GET",
		url: baseurl + section_contents[item_number].key + "/tree",
		dataType: "xml",
		success: function(data) {
			// For the current item
			//xmlString = (new XMLSerializer()).serializeToString(data);
			//log_to_console(xmlString);
			$(data).find("MediaPart").each(function() {
				//section_contents[item_number].id = $(this).attr("id");
				section_contents[item_number].hash = $(this).attr("hash");
			});

			$(data).find("MediaStream").each(function() {
				if ($(this).attr("type") == "3") {
					subtitle = new Subtitle();
					subtitle.id = $(this).attr("id");
					subtitle.codec = $(this).attr("codec");
					subtitle.language = $(this).attr("language");
					if(typeof $(this).attr("url") != 'undefined') {
						subtitle.url = $(this).attr("url");
						subtitle.title = subtitle.url.substring(subtitle.url.lastIndexOf("/")+1);
						
						if($(this).attr("url").indexOf("media://") == -1) {
							subtitle.local = true;
						}
					} else {
						subtitle.title = "Integrated Subtitle";
						subtitle.integrated = true;
					}
					
					if (subtitle.language === undefined) {
						language = "-";
					} else {
						language = subtitle.language;
					}

					section_contents[item_number].subtitles.push(subtitle);
				}
			});
			check_duplicates(item_number);
			check_exists(item_number);
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		},
		complete: function() {
			log_to_console("second ajax complete");
			return true;
		}
	});
}

function ajax_get_active_subtitle(item_number) {
log_to_console("Searching for active subtitle for : " + section_contents[item_number].title);
$.ajax({
		type: "GET",
		url: baseurl + section_contents[item_number].key,
		dataType: "xml",
		success: function(data) {
			// For the current item
			//xmlString = (new XMLSerializer()).serializeToString(data);
			//log_to_console(xmlString);
			$(data).find("Stream").each(function() {
				if ( ($(this).attr("streamType") == "3") && ($(this).attr("selected") == "1") )  {	
					log_to_console("Found a active subtitle for : " + section_contents[item_number].title + " with ID: " + $(this).attr("id"));
					section_contents[item_number].active_subtitle_id = $(this).attr("id");
				}
			});
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		}
	});
}

//////////////////////////////////////
// Generic functions
//////////////////////////////////////

/**
 * This function takes the name of the option and it's value and sends it to the bundlepart. Saving it in settings.js for later.
 */
function save_option(option_name,option_value,number) {
	
	console.log("Saving Options for number: " + number);
	$.ajax({
		type: "GET",
		url: baseurl + utility + "?Func=SetPref&Secret="+Secret+"&Pref="+option_name[number]+"&Value="+option_value[number],
		dataType: "text",
		global: false,
		success: function(data) {
			console.log(data);
			if(data == "ok") {
				log_add("Successfully saved setting: ("+ number +")" + option_name[number] + " as: " + option_value[number]);
			} else {
				log_add("Failed saving setting: ("+ number +")" + option_name[number] + " as: " + option_value[number]);
			}
			var new_number = number + 1;
			if(new_number < option_name.length) {	
				save_option(option_name,option_value,new_number);
			}
		},
		error: function(data, status, statusText, responsText) {
			alert(statusText);
		}
	});
}

/**
 * This function is used to fetch the options and triggering a refresh of the display.
 */
function Options() {

	var option_name_array = [];
	var option_value_array = [];
	
	items_per_page = $("input[name=items_per_page]").val();
	option_name_array.push("items_per_page");
	option_value_array.push($("input[name=items_per_page]").val());
	//save_option("items_per_page",$("input[name=items_per_page]").val());
	
	
	options_hide_integrated = Boolean($("input[name=Option_HideIntegrated]").prop("checked"));
	//save_option("options_hide_integrated",$("input[name=Option_HideIntegrated]").prop("checked"));
	option_name_array.push("options_hide_integrated");
	option_value_array.push($("input[name=Option_HideIntegrated]").prop("checked"));
	
	
	options_hide_local = Boolean($("input[name=Option_HideLocal]").prop("checked"));
	//save_option("options_hide_local",$("input[name=Option_HideLocal]").prop("checked"));
	option_name_array.push("options_hide_local");
	option_value_array.push($("input[name=Option_HideLocal]").prop("checked"));
	
	
	options_hide_empty_subtitles = Boolean($("input[name=Option_HideEmptySubtitles]").prop("checked"));
	//save_option("options_hide_empty_subtitles",$("input[name=Option_HideEmptySubtitles]").prop("checked"));
	option_name_array.push("options_hide_empty_subtitles");
	option_value_array.push($("input[name=Option_HideEmptySubtitles]").prop("checked"));
	
	
	options_only_multiple = Boolean($("input[name=Option_ShowOnlyMultiple]").prop("checked"));
	//save_option("options_only_multiple",$("input[name=Option_ShowOnlyMultiple]").prop("checked"));
	option_name_array.push("options_only_multiple");
	option_value_array.push($("input[name=Option_ShowOnlyMultiple]").prop("checked"));
	
	options_auto_select_duplicate = Boolean($("input[name=Option_Autoselect]").prop("checked"));
	option_name_array.push("options_auto_select_duplicate");
	option_value_array.push($("input[name=Option_Autoselect]").prop("checked"));
		
	save_option(option_name_array,option_value_array,0);

	if(section_contents.length>0) {
		list_section_contents(0);
	}
	log_add("Options Saved!");	
	
	return false;
}

/**
 * This will be used for viewing the subtitle
 */
function read_subtitle(path) {
 // Add correction for local subtitles.
 
 // Handle differently depending on if it's a agent or local.
 // check if it begins with media:// or file://
 

 if (path.indexOf("media:") == -1) {
	// it's a local file
	path = path.substr(7);
	
 } else if (path.indexOf("file:") == -1) {
	// it's a agent file
	path = PathToPlexMediaFolder+append+path.substr(8);
 }

	var temporaryWindow = window.open('view_sub.html');
	$.ajax({
		type: "GET",
		url: baseurl + utility + "?Func=ShowSRT&Secret="+Secret+"&FileName="+path,
		dataType: "text",
		success: function(data) {
			// For the current item
			//xmlString = (new XMLSerializer()).serializeToString(data);
			//log_to_console(xmlString);
			
			var content = "<div id='Log' class='VideoBox'><div class='VideoHeadline'>Viewing: \""+path+"\"</div>";

			content += "<div class='VideoSubtitle'><textarea class='EditText' wrap='off' readonly>"+data+"</textarea></div>";
			
			content += "</div>";
			setTimeout(function() {$(temporaryWindow.document.body).html(content);},1000);
		},
		error: function(data, status, statusText, responsText) {
			alert(data + statusText);
		},
		complete: function() {
			log_to_console("second ajax complete");
			return true;
		}
	});
	
}
/**
 * Refreshes result with the search.
 */
function Search() {
	if($("input[name=searchstring]").val().length === 0) {
		searchstring = "";
		list_section_contents(0);		
	} else if($("input[name=searchstring]").val().length > 2) {
		searchstring = $("input[name=searchstring]").val();
		list_section_contents(0);
		log_add("Searching for '"+searchstring+"' in titles.");
	} else {
		log_add("Minimum of 3 characters for searching.");
	}
}

function list_section_contents(show_page) {
	$("#MainBox").html("");
	prepare_output();
	current_page = show_page;
	pages_output(show_page);
	start_value = show_page * items_per_page;
	end_value = (parseInt(start_value) + parseInt(items_per_page));
	if (end_value > presentable_contents.length) {
		end_value = presentable_contents.length;
	}
	log_to_console("Start Value: " + start_value);
	log_to_console("End Value: " + end_value);
	for (i = start_value; i < end_value; i++) {
		item = presentable_contents[i];
		if(item.hide === false) {
			newEntry = "";
			if ( (item.type == "movie") || (item.type == "episode") ) {
				newEntry = "<div class='VideoBox'><div class='VideoHeadline'>" + item.title + "</div>";

				for (x = 0; x < item.subtitles.length; x++) {
					subtitle = item.subtitles[x];
					active = "";
					addClass = false;
					checkbox = "";
					exists = "";
					view = "";
					show_subtitle = true; // Asume everything can be shown
					
					//Check if the current subtitle has a language defined.	
					if (subtitle.language === undefined) {
						language = "-";
					} else {
						language = subtitle.language;
					}
					if (subtitle.integrated === false) {
						selected = "";
						subtitle.url = subtitle.url.replace(/\\/g,"/");
						
						view = "<span class='link' onclick='read_subtitle(\""+subtitle.url+"\")'>View</span>";
						
						if( (subtitle.isDuplicate === true) && (options_auto_select_duplicate === true) ) {
							selected = "checked=checked";
						}
						checkbox = "<input type='checkbox' name='subtitle-"+item.id+"' value='"+item.id+":"+subtitle.id+":"+subtitle.title+"' "+selected+">";
					}
					
					if (subtitle.id == item.active_subtitle_id) {
						active = "Selected subtitle in Plex";
						addClass = "Active";
					}
					console.log(" Subtitle exists: " + subtitle.exists);
					if (subtitle.exists === false) {
						exists = "This has been removed from Plex. Please refresh library";
						addClass = "Removed";
					}

					if (subtitle.hide === false) {
						//newEntry += "<div class='VideoSubtitle'><table cellpadding=0 cellspacing=0 style='width: 100%'><tr class='hovering'><td class='mainText'><span class='link' onclick='getXML(\""+item.key+"\",\"#MainBox\",0);'>"+item.key+"</span> | "+item.id+item.title+"</td></tr></table></div></div>";
						newEntry += "<div class='VideoSubtitle "+addClass+"'>";
						newEntry += "<table class='Max' cellspacing=0 cellpadding=0><tr><td class='small mainText'>" + checkbox + "</td><td class='small mainText'>" + subtitle.codec + "</td><td class='small mainText'>" + language + "</td><td class='mainText'>" + subtitle.title + "</td><td class='small mainText'>" + view + "</td></tr>";
						if (addClass !== false) {
							newEntry +=  "<tr><td></td><td></td><td></td><td class='mainText'>Message: " + active + exists + "</td></tr>";
						}
						
						newEntry += "</table></div>";
		
					}
				}
				newEntry += "<div class='VideoBottom'><button class='btn btn-default btn-xs' onclick=\"subtitle_select_all('subtitle-"+item.id+"', true)\">Select All</button> <button class='btn btn-default btn-xs' onclick=\"subtitle_select_all('subtitle-"+item.id+"', false)\">Clear Selection</button> <button class='btn btn-default btn-xs' onclick=\"delete_subtitle_confirm('subtitle-"+item.id+"');\">Delete Selected</button></div></div>";
			} else if (item.type == "show") {
				newEntry = "<div class='VideoBox'><div class='VideoHeadline'><span class='link' onclick='list_shows_and_seasons(\""+item.key+"\",false);'>" + item.title + "(" + item.type + ")</span></div></div>";
			} else if (item.type == "season") {
				newEntry = "<div class='VideoBox'><div class='VideoHeadline'><span class='link' onclick='list_movies(\""+item.key+"\",false);'>" + item.title + "(" + item.type + ")</span></div></div>";
			}
			$("#MainBox").append(newEntry);
		}
	}
	$("input[name=searchbutton]").removeAttr("disabled");
}

function subtitle_select_all(checkboxname, toggle) {
	$.each($("input[name="+checkboxname+"]"), function() {
		$(this).prop("checked",toggle);
	});
}

function subtitle_delete(checkboxname) {
	$.each($("input[name="+checkboxname+"]:checked"), function() {
		
		media_id = $(this).val().substring(0,$(this).val().indexOf(":"));
		subtitle_id = $(this).val().substring($(this).val().indexOf(":")+1);
		console.log("SubtitleID: " + subtitle_id + " media_id: " + media_id);
	});	
}

/********************************************************************************************************************
 * This section handles deletion of subtitles
 ********************************************************************************************************************/
 function delete_subtitle_confirm(checkboxname) {
	if($("input[name="+checkboxname+"]:checked").length>0) {
		$("#myModal .modal-title").html("Delete Subtitles?"); // Set custom content to body of Modal
		var ModalBody = "Are you sure you want to delete the selected subtitles: <br>";
			
			$.each($("input[name="+checkboxname+"]:checked"), function() {	
			subtitle_info = $(this).val().split(":");	
				ModalBody+= subtitle_info[2] + "<br>";
			});	
		
		$("#myModal .modal-body").html(ModalBody); // Set custom content to body of Modal
		$("#myModal .modal-footer").html('<button type="button" class="btn btn-default" onclick="delete_subtitle(\''+checkboxname+'\')">Yes, delete them</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>'); // Set custom content to body of Modal

		$("#myModal").modal({keyboard: false, backdrop:false, show: true});
	}
  }
  
  function delete_subtitle_ajax(item_number) {
	complete = ((delete_subtitle_array_completed.length / delete_subtitle_array_queue.length)*100);
	$("#progress td ").html("<div class='progress'><div class='progress-bar' role='progressbar' aria-valuenow='"+complete+"' aria-valuemin='0' aria-valuemax='100' style='width: "+complete+"%;'>"+Math.round(complete)+"%</div></div>");
	
	
	if(delete_subtitle_array_queue.length>item_number) {
		current_sub = delete_subtitle_array_queue[item_number];
		subtitle_info = current_sub.split(":");		
		$("#myModal #"+subtitle_info[1]+" td:last-child").html('Deleting...');
		
		$.ajax({
			type: "GET",
			url: baseurl + utility + "?Func=DelSub&Secret="+Secret+"&MediaID="+subtitle_info[0]+"&SubFileID="+subtitle_info[1],
			dataType: "text",
			success: function(data) {		
				if(data == "ok") {
					if(delete_subtitle_array_queue.length>item_number) {
						item_number = item_number + 1;
						delete_subtitle_array_completed.push(delete_subtitle_array_queue[item_number]);	
						
						// Go through all items in section_contents searching for the current "movie"
						for (si=0; si<section_contents.length;si++) {
							video = section_contents[si];
							console.log("video.id: " + video.id + " searching for: " + subtitle_info[0]);
							if (video.id == subtitle_info[0]) {
								for (sx=0; sx<video.subtitles.length;sx++) {
									subtitle = video.subtitles[sx];
									console.log("subtitle.id: " + subtitle.id + " searching for: " + subtitle_info[1]);
									if (subtitle.id == subtitle_info[1]) {
										log_to_console("Found subtitle that has been deleted."+subtitle_info[2]);
										subtitle.exists = false;
									}
								}
							}
						}
						$("#myModal #"+subtitle_info[1]+" td:last-child").html('Success');
						delete_subtitle_ajax(item_number);
					} else {
						list_section_contents(current_page);
						delete_subtitle_array_queue = [];
						delete_subtitle_array_completed = [];
					  
						$("#myModal .modal-footer").html('Refresh section in Plex? <button type="button" class="btn btn-default" onclick="force_refresh();">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>'); // Set custom content to body of Modal
					}	
				} else {
					$("#myModal #"+subtitle_info[1]+" td:last-child").html('Failed');
					if(delete_subtitle_array_queue.length>item_number) {
						item_number = item_number + 1;
						delete_subtitle_array_completed.push(delete_subtitle_array_queue[item_number]);	
						delete_subtitle_ajax(item_number);
					} else {
						list_section_contents(current_page);
						delete_subtitle_array_queue = [];
						delete_subtitle_array_completed = [];
					  
						$("#myModal .modal-footer").html('Refresh section in Plex? <button type="button" class="btn btn-default" onclick="force_refresh();">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>'); // Set custom content to body of Modal
					}
				}
			},
			error: function(data, status, statusText, responsText) {
				console.log("Error in deleting subtitle: " + statusText);
			},
		});
	} else {
		list_section_contents(current_page);
		delete_subtitle_array_queue = [];
		delete_subtitle_array_completed = [];
		$("#myModal .modal-footer").html('Refresh section in Plex? <button type="button" class="btn btn-default" onclick="force_refresh();">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>'); // Set custom content to body of Modal
	}
	
	
	
	// Replace setTimeout with an AJAX call
	/*
	setTimeout(function() {
		//alert("here also.");
		// This section is the complete: part of the ajax call.
		if(delete_subtitle_array_queue.length>item_number) {
			item_number = item_number + 1;
			delete_subtitle_array_completed.push(delete_subtitle_array_queue[item_number]);	
			
			// Go through all items in section_contents searching for the current "movie"
			for (si=0; si<section_contents.length;si++) {
				video = section_contents[si];
				console.log("video.id: " + video.id + " searching for: " + subtitle_info[0]);
				if (video.id == subtitle_info[0]) {
					for (sx=0; sx<video.subtitles.length;sx++) {
						subtitle = video.subtitles[sx];
						console.log("subtitle.id: " + subtitle.id + " searching for: " + subtitle_info[1]);
						if (subtitle.id == subtitle_info[1]) {
							log_to_console("Found subtitle that has been deleted."+subtitle_info[2]);
							subtitle.exists = false;
						}
					}
				}
			}
			$("#myModal #"+subtitle_info[1]+" td:last-child").html('Success');
			delete_subtitle_ajax(item_number);
		} else {
		list_section_contents(current_page);
		  delete_subtitle_array_queue = [];
		  delete_subtitle_array_completed = [];
		  
		  $("#myModal .modal-footer").html('Refresh section in Plex? <button type="button" class="btn btn-default" onclick="force_refresh();">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>'); // Set custom content to body of Modal
		}
	}, 1000);
	*/
  }
  
  
  
  function delete_subtitle(checkboxname) {
	$("#myModal .modal-title").html("Deleting Subtitles"); // Set custom content to body of Modal
	var ModalBody = "<table class='table Max'><tr><td>Subtitle</td><td class='long'>Status</td></tr>";
		
	$.each($("input[name="+checkboxname+"]:checked"), function() {	
		delete_subtitle_array_queue.push($(this).val());
		subtitle_info = $(this).val().split(":");
		ModalBody += "<tr id='"+subtitle_info[1]+"'><td class='mainText'>"+subtitle_info[2]+"</td><td class='mainText'>Waiting</td></tr>";
	});	
	
	complete = ((delete_subtitle_array_completed.length / delete_subtitle_array_queue.length)*100);
	ModalBody += "<tr id='progress'><td class='mainText' colspan='2'><div class='progress'><div class='progress-bar' role='progressbar' aria-valuenow='"+complete+"' aria-valuemin='0' aria-valuemax='100' style='width: "+complete+"%;'>"+Math.round(complete)+"%</div></div></td></tr>";
	ModalBody += "</table>";
	$("#myModal .modal-body").html(ModalBody); // Set custom content to body of Modal
	$("#myModal .modal-footer").html('<button type="button" class="btn btn-default">Waiting...</button>'); // Set custom content to body of Modal
	
	delete_subtitle_ajax(0);
  }
  
  /********************************************************************************************************************
   * END OF SUBTITLE DELETE
   ********************************************************************************************************************/
/**
 * force_refresh()
 * Ajax-call to start the forced refresh of the current section.
 * Ajax-call to fetch data from /library/sections
 * Find Key="section_key", check refreshing, store in variable, output to log
 * set timer to check for variable change
 */
 
 function force_refresh() {
	$("#myModal").modal('hide');
	$.ajax({
			type: "GET",
			url: baseurl + "/library/sections/"+ selected_section +"/refresh?force=1",
			dataType: "text",
			global: false,
			success: function(data) {
				
				setTimeout(function() {
					section = get_section_info(selected_section);
					log_add("Started forced refresh in Plex on section: " + section.title);
					section.refreshing = true;
					force_refresh_verify()},3000);						
			},
			error: function(data, status, statusText, responsText) {
				log_to_console(data + statusText);
			},
			complete: function() {
				log_to_console("Initiated forced-refresh on section with key: " + selected_section);
				return true;
			}
		});	
 }
 
 function force_refresh_verify() {
 //section = get_section_info(section_key);
 	$.ajax({
			type: "GET",
			url: baseurl + "/library/sections/",
			dataType: "xml",
			global: false,
			success: function(data) {
				
				$(data).find("Directory ").each(function() {
					/*
					if(first_run === true) {
						if ($(this).attr("key") == section.key){
							
							if($(this).attr("refreshing") == "1") {
								log_add("Started forced refresh in Plex on section: " + section.title);
								console.log("[true]Calling force_refresh after 2 seconds, with false");
								setTimeout(function() {force_refresh_verify(false, section_key)},2000);
							} else {
								console.log("[true]Calling force_refresh after 2 seconds, with true. We did not yet see that we started it.");
								setTimeout(function() {force_refresh_verify(true, section_key)},2000);
							}
						}
					} else {
						if ($(this).attr("key") == section.key) {
							if($(this).attr("refreshing") == "0") {
								log_add("Section refresh in Plex completed on: " + section.title);
								log_to_console("Section refresh in Plex completed on: " + section.title);
							} else {
								console.log("[false]Calling force_refresh after 2 seconds, with false");
								setTimeout(function() {force_refresh_verify(false, section_key)},2000);
							}
						}
					}
					*/
					section = get_section_info($(this).attr("key"));
					if(section.refreshing === true) {
						if($(this).attr("refreshing") == "0") {
								log_add("Section refresh in Plex completed on: " + section.title + ". Extra information may still be downloading from the Internet");
								log_to_console("Section refresh in Plex completed on: " + section.title);
								section.refreshing = false;
						}	
					}			
				});
				
				for (i = 0; i < sections.length; i++) {
					if (sections[i].refreshing === true) {
						setTimeout(function() {force_refresh_verify()},2000);
						break;
					}
				}
			},
			error: function(data, status, statusText, responsText) {
				log_to_console(data + statusText);
			},
			complete: function() {
				log_to_console("Verified forced-refresh on key: " + selected_section + " and title: " + section.title);
				return true;
			}
		});	
}
/**
 * This function counts the items to be displayed and shows any pagin if needed.
 */
function pages_output(show_page) {
	$("#PageBar").html("");
	var numberOfPages = presentable_contents.length / items_per_page;
	var pages = "";
	if (numberOfPages > 1) {
		pages = "WebTools V." + Version + "\t<ul class='pagination pagination-sm'>";

		for (i = 0; i < numberOfPages; i++) {
			if (i == show_page) {
				pages = pages + "<li class='active'> <span onclick='list_section_contents(" + i + ");'>" + (i + 1) + "</span></li>";
			} else {
				pages = pages + "<li> <span onclick='list_section_contents(" + i + ");'>" + (i + 1) + "</span></li>";
			}

		}
		$("#PageBar").html(pages + "</ul>");
	}
}

// Returns the sectionobject for the requested one.
function get_section_info(LibraryKey) {
	for (i = 0; i < sections.length; i++) {
		if (sections[i].key == LibraryKey) {
			return sections[i];
		}
	}
}

function reset_variables() {
	show_page = 0; // Default so we start at first page.
	section_contents = []; // Empty the array with items.
	searchstring = "";
}

// This section updates the sectionsbox to highlight what has been selected and to show the proper searchbox.
function update_section_box(LibraryKey, TriggeringElement) {
	selected_section = LibraryKey; // is this usefull?
	$("#MainBox").html(loadingScreen);
	$("#PageBar").html("");
	$("#LibraryBox span").removeClass("Bold");
	$(TriggeringElement).addClass("Bold");

	SearchBox = "<div class='VideoHeadline'>Search " + $(TriggeringElement).html() + "</div>";
	SearchBox += "<div class='VideoSubtitle'><input type='text' value='"+searchstring+"' name='searchstring'></div>";
	SearchBox += "<div class='VideoSubtitle'><input type='submit' name='searchbutton' class='btn btn-default btn-xs' value='Search'></div>";

	$("#SearchBox").html(SearchBox);
	$("#SearchBox").addClass("VideoBox");
	$("input[name=searchbutton]").attr("disabled", "disabled");
}


/**
 * This function is used to prepare the output with regards to the selected options.
 * This is ONLY things that affect paging
 * This is needed to be able to calculate the pages correctly while still having the original data available.
 */
function prepare_output() {	
	presentable_contents = [];
	
	console.log("Length of section_contents: " + section_contents.length);	
	for (i=0; i<section_contents.length;i++) {
		item = section_contents[i];
		discovered_languages = [];
		
		// Asume everything can be added.
		item.hide = false;
		
		// If there is no searchstring, continue
		if(searchstring.length > 2) {
			log_to_console(item.title.toLowerCase().indexOf(searchstring.toLowerCase()));
			// If the searchstring is not found, then do not add it.
			if(item.title.toLowerCase().indexOf(searchstring.toLowerCase()) == -1) {
				item.hide = true;
			}
		}


		if(item.subtitles  !== undefined) {
			for (x=0;x<item.subtitles.length;x++) {
				// Reset hide status to false for current subtitle.
				
				item.subtitles[x].hide = false;
				if( (options_hide_local === true) && (item.subtitles[x].local === true) ) {
					log_to_console("Subtitle that matched: " + item.subtitles[x].title);
					item.subtitles[x].hide = true;
				}

				if( (options_hide_integrated === true) && (item.subtitles[x].integrated === true) ) {
					log_to_console("Subtitle that matched: " + item.subtitles[x].title);
					item.subtitles[x].hide = true;
				}
				
				if(item.subtitles[x].hide === false) {
					if(discovered_languages.length === 0) {
						log_to_console("discovered_languages was empty. Will add the current language");
						discovered_languages[0] = [item.subtitles[x].language,1];
					} else {
						added = false;
						for (y=0;y<discovered_languages.length;y++) {
							log_to_console("There is something in the discovered_languages array...");
							if(discovered_languages[y][0] == item.subtitles[x].language) {
								log_to_console("Found a match for an already existing language! " + discovered_languages[y][0] + " matched " + item.subtitles[x].language);
								discovered_languages[y][1]++;
								added = true;
							}
						}

						if(added === false) {
							log_to_console("We didn't find a match afterall, we have to add to position: " + discovered_languages.length);
							discovered_languages[discovered_languages.length] = [item.subtitles[x].language,1];	
						}
					}
				}
			}
		
			/*
			 Count items in array with specific value.. 
			 for each item in array
				store value in new array
		
			*/
			
			for (y=0;y<discovered_languages.length;y++) {
				log_to_console(item.title + "Language: " + discovered_languages[y][0]);
				log_to_console(item.title + "Number of occurences: " + discovered_languages[y][1]);	
			}
			
			// Lets check if we should show it or not if we have multiple subtitles
			if(options_only_multiple === true) {
				for (x=0;x<item.subtitles.length;x++) {
					for (y=0;y<discovered_languages.length;y++) {
						if(discovered_languages[y][0] == item.subtitles[x].language) {
							if(discovered_languages[y][1] < 2) {
								item.subtitles[x].hide = true;
							}
						}
					}
				}
			}
			
			
			if (options_hide_empty_subtitles === true) {
				console.log("Hide everything that hasn't got a subtitle");
				if( (item.type == "show") || (item.type == "season") ) {
					console.log("Found item of type: " + item.type + ". not hiding it.");
				} else {
					console.log("Found item of type: " + item.type + ". Hiding it.");
					// Now, we asume everything will be hidden.
					item.hide = true;
				
					for (x=0;x<item.subtitles.length;x++) {

						// If there is a subtitle that is set to show, we have to show this video
						if (item.subtitles[x].hide === false){
							item.hide = false;
						}
					}
				}
				
			}	
		}		
		// If we are alowed to add it, do so.
		if(item.hide === false) {
			log_to_console("Adding item in presentable_contents: " + item.title);
				presentable_contents.push(item);
		}
	}
	log_to_console("length of presentable_contents: " + presentable_contents.length);
 }

/**
 * This function adds the LogMessage to the Log array and correctly displays current information in the Log div, limited by log_show_amount
 */
function log_add(LogMessage) {
	
	$("#Log").html(""); 
	log.push(getDateTime() + " " + LogMessage);
	
	if(log.length>log_show_amount) {
		start = log.length - log_show_amount;
	} else {
		start = 0;
	}	
	
	$("#Log").append("<div class='VideoHeadline'>Log</div>");
	for (i=start;i<log.length;i++) {
		$("#Log").append("<div class='VideoSubtitle'>"+log[i]+"</div>");
	}
	$("#Log").append("<div class='VideoBottom'><button class='btn btn-default btn-xs' onclick='log_view()'>View complete log</button></div>");
}

function log_to_console(Message) {
	if ( (typeof(console) == "object") && ("console" in window) ) {
	
			try {
				   console.log(Message);
		   }
		   catch (e) {}
		   finally {
				   return;
		   }
	}
}

/**
 * This function displays the entire log generated through the current visit in a new window.
 */
function log_view() {
	var temporaryWindow = window.open('view_log.html');
	var content = "<div id='Log' class='VideoBox'><div class='VideoHeadline'>Log</div>";
	for (i=0;i<log.length;i++) {
		content += "<div class='VideoSubtitle'>"+log[i]+"</div>";
	}
	content += "</div>";
	setTimeout(function() {$(temporaryWindow.document.body).html(content);},1000);
}

/**
 * Do a refresh of displayed content after all ajaxes have done their thing.
 */
$(document).ajaxStop(function() {
	log_to_console("All ajax request completed.");
	list_section_contents(0);
	end_timer();
	log_add("Finished loading the section.");
});

/**
 * This function fetches the settings. This is to counter the caching of browser.
 */
function fetchSettings() {
  $.get('jscript/settings.js',function(data){
	  var perLine=data.split('\n');
	  var myVars=[];
	  for(i=0;i<perLine.length;i++)
	  {
		  var line=perLine[i].split(' ');
		  myVars[i]={
			  'variablename':line[1],
			  'variablevalue':line[3]
		  }
	  }
  
	  for(i=0;i<myVars.length;i++) {
		  if(myVars[i].variablename !== undefined) {
				if( (myVars[i].variablename == "Secret") || (myVars[i].variablename == "PMSUrl") || (myVars[i].variablename == "options_hide_integrated") || (myVars[i].variablename == "options_hide_local") || (myVars[i].variablename == "options_hide_empty_subtitles") || (myVars[i].variablename == "options_only_multiple") || (myVars[i].variablename == "options_auto_select_duplicate") || (myVars[i].variablename == "items_per_page") ) {
					console.log(myVars[i].variablevalue.substring(myVars[i].variablevalue.indexOf('"')+1,myVars[i].variablevalue.indexOf('";')));
					if(myVars[i].variablevalue.substring(myVars[i].variablevalue.indexOf('"')+1,myVars[i].variablevalue.indexOf('";')) == "true") {
						window[myVars[i].variablename] = true;						  
					} else if(myVars[i].variablevalue.substring(myVars[i].variablevalue.indexOf('"')+1,myVars[i].variablevalue.indexOf('";')) == "false") {
						window[myVars[i].variablename] = false;
					} else {
						window[myVars[i].variablename] = myVars[i].variablevalue.substring(myVars[i].variablevalue.indexOf('"')+1,myVars[i].variablevalue.indexOf('";'));		
					}
				}
		  }
	  }
  });
}
		  

// Force all ajax-calls to be non-cached.
//$.ajaxSetup({ cache: false });
//////////////////////////////////////
// "Classes"
//////////////////////////////////////
function Video() {
	this.active_subtitle_id = false;
	this.filename = "";
	this.hash = "";
	this.hide = false;
	this.id = "";
	this.key = "";
	this.showKey = false;
	this.showRatingKey = false;
	this.seasonKey = false;
	this.seasonRatingKey = false;
	this.subtitles = [];
	this.title = "";
	this.type = "";
}

function Subtitle() {
	this.codec = "";
	this.hide = false;
	this.id = "";
	this.integrated = false;
	this.language = "";
	this.local = false;
	this.isDuplicate = false;
	this.title = ""; // Is this needed?
	this.url = "";
	this.exists = true;
	
}