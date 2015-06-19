// Store the variables used globally throughout the application.
var globalvariables = {
    secret: '',
    sections: [],
    options: {},
    items_per_page_max: 50,
    items_per_page_min: 5
}

// Store information about the current section that we are displaying.
var selected_section = {
    key: 0,
    title: '',
    contents: [],
    totalsize: 0,
    currentpage: 0,
    parents_key: [],
    parents_title: [],
    contentstype: ''
}

var get_section_list = new asynchelper(true,false);
get_section_list.inline([
    function(callback) {
        //Name:VersionFetch
        $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
        // Fetch version and generate the key
        $.ajax({
                url: '/webtools/version',
                cache: false,
                dataType: 'JSON',
                success: function(data) {
                    globalvariables.secret = $.md5(data.version);
                    callback('VersionFetch:Success');
                },
                error: function(data) {
                    display_error('Failed fetching the version from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_section_list.abort('Error: ' + data.statusText);
                }
            });
    },
    function(callback) {
        //Name:SettingsFetch
        $.ajax({
            url: '/webtools/settings',
            cache: false,
            dataType: 'JSON',
            headers: {'Mysecret':globalvariables.secret},
            success: function(data) {
                globalvariables.options = data;
                
                
                callback('SettingsFetch:Success');
            },
            error: function(data) {
                display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
                              +'<br>Errorinfo:'
                              +'<br>Requested URL: ' + this.url
                              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                $('#LoadingModal').modal('hide');
                get_section_list.abort('Error: ' + data.statusText);
            }
        });    
    },
    function(callback) {
        //Name:SectionFetch
        // Fetch sections and list them.
        $.ajax({
            url: '/webtools/sections',
            cache: false,
            dataType: 'JSON',
            headers: {'Mysecret':globalvariables.secret},
            success: function(data) {
                $('#SectionMenu').html('');
                //console.log(JSON.stringify(data));
                data.forEach(function(currentsection) {
                    // Example: {"type":"movie","key":"1","title":"Home Videos"}                    
                    var targetFunction = false;
                    if (currentsection.type == 'movie') {
                        targetFunction = 'fetch_section_type_movies('+currentsection.key+',0);';
                    } else if (currentsection.type == 'show') {
                        targetFunction = 'fetch_section_type_show('+currentsection.key+',0);';
                    }

                    if (targetFunction !== false) {
                        $('#SectionMenu').append('<li><a class="customlink" onclick="javascript:' + targetFunction + '">' + currentsection.title + '</a></li>');
                        globalvariables.sections.push(currentsection);
                    }    
                });
                $('#SectionMenu').append('<li><a class="customlink" onclick="javascript:get_section_list.start();">Refresh Sections</a></li>');
			    $('#LoadingModal').modal('hide');
                callback('SectionFetch:Success');
            },
            error: function(data) {
                display_error('Failed fetching the sections from the server. Please restart the server.<br>'
                                +'<br>Errorinfo:'
                                +'<br>Requested URL: ' + this.url
                                +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                $('#LoadingModal').modal('hide');
                get_section_list.abort('Error: ' + data.statusText);
            }
            
        });
    }
], function(result) {
    webtools_log(0,result);
    //console.log(result);
});

function display_show() {
    calculate_pages();
    $('#LoadingBody').html('Applying filters and preparing output.');   
    $('#ContentHeader').html(selected_section.title);
    $('#ContentBody').html('');
    var newEntry = ['<table class="table table-bordered">']
    selected_section.contents.forEach(function(content) {
        console.log(content);
        newEntry.push('<tr><td><a class="customlink" onclick="javascript:fetch_show_seasons(' + content.key + ',0)">' + content.title + '</a></td></tr>');                        
    });
    newEntry.push('</table>');
    $("#ContentBody").append(newEntry.join('\n'));
    $('#LoadingModal').modal('hide');
}

function display_season() {
    calculate_pages();
    $('#LoadingBody').html('Applying filters and preparing output.');
    
    $('#ContentHeader').html('<a class="customlink" onclick="javascript:fetch_section_type_show(' + selected_section.parents_key[0] + ',0)">' + selected_section.parents_title[0] + '</a> /' + selected_section.title);
    $('#ContentBody').html('');
    var newEntry = ['<table class="table table-bordered">']
    var end = ((selected_section.currentpage*globalvariables.options.items_per_page) + globalvariables.options.items_per_page);
    if (end > selected_section.contents.length) {
        end = selected_section.contents.length
    }
    for (var i=(selected_section.currentpage*globalvariables.options.items_per_page); i<end;i++) {
        newEntry.push('<tr><td><a class="customlink" onclick="javascript:fetch_season_episodes(' + selected_section.contents[i].key + ',0)">' + selected_section.contents[i].title + '</a></td><td>Episodes in season: ' + selected_section.contents[i].size + '</td></tr>');                        
    
    }
    newEntry.push('</table>');
    $("#ContentBody").append(newEntry.join('\n'));
    $('#LoadingModal').modal('hide');   
}

function display_episodes() {
    /*
        Go through all the options and modify the output accordingly.
    */
    
    var end = ((selected_section.currentpage*globalvariables.options.items_per_page) + globalvariables.options.items_per_page);
    if (end > selected_section.contents.length) {
        end = selected_section.contents.length;
    }
    
    var start = (selected_section.currentpage*globalvariables.options.items_per_page);
    if (start >= selected_section.contents.length) {
        start = 0;
    }
    
    //selected_section.prepared_content
    calculate_pages();
    
    $('#LoadingBody').html('Applying filters and preparing output.');
    $('#ContentHeader').html(selected_section.title);
    $('#ContentBody').html('');
    //console.log('Start from item: ' + (globalvariables.options.items_per_page*selected_section.currentpage));
    //console.log('Show number of items from that point: ' + ((Number(globalvariables.options.items_per_page*selected_section.currentpage))+Number(globalvariables.options.items_per_page)));  
    
    for (var i=start; i<end; i++) {    
        
        // Options Time!
        var discoveredlanguages = [];
        selected_section.contents[i].subtitles.forEach(function(subtitle) {
            if (discoveredlanguages.length == 0) {
                discoveredlanguages.push([subtitle.languageCode,1]);   
            } else {
                added = false;
                for (l = 0; l<discoveredlanguages.length; l++) {
                    if (discoveredlanguages[l][0] == subtitle.languageCode) {
                        discoveredlanguages[l][1] += 1;
                        added = true;
                    }
                }
                if(added === false) {
                    //log_to_console("We didn't find a match afterall, we have to add to position: " + discovered_languages.length);
                    discoveredlanguages.push([subtitle.languageCode,1]);
                }
            }
        });
        // End of Options Time!

        var newEntry = ['<div class="panel panel-default">'];
        newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + selected_section.contents[i].title + '</h4></div>');
        newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');


        newEntry.push('<tr><th class="td-small">Lang.</th><th>Location</th><th>Codec</th><th></th></tr>');
        var anysubtitleadded = false;
        selected_section.contents[i].subtitles.forEach(function(subtitle) {
            var display_subtitle = true;
            var language = '';
            var selectedsubtitle = '';

            if (subtitle.languageCode != null) {
                if (typeof(languagecodes[subtitle.languageCode.toUpperCase()]) != 'undefined') {
                    language = '<img src="flags/blank.png" class="flag flag-'+languagecodes[subtitle.languageCode.toUpperCase()].toLowerCase()+'"/>';   
                }
            }

            if (subtitle.selected != null) {
                selectedsubtitle = ' class="bg-success"';
            }
            
            // Options filtering
            if (globalvariables.options.options_only_multiple) {
                display_subtitle = false;
                discoveredlanguages.forEach(function (language) {
                    if ( (language[0] == subtitle.languageCode) && (language[1] > 1) ) {
                        display_subtitle = true;
                    }
                });
            }
           
            if ( (globalvariables.options.options_hide_integrated) && (subtitle.location == 'Embedded') ) {
                display_subtitle = false;
            }

            if ( (globalvariables.options.options_hide_local) && (subtitle.location == 'Sidecar') ) {
                display_subtitle = false;
            }
            // End of options filtering

            if (display_subtitle) {
                anysubtitleadded = true;
                var view = '';
                if (subtitle.location == 'Sidecar') {
                    view = '<button class="btn btn-default btn-xs" onclick=\'view_subtitle('+selected_section.contents[i].key+','+subtitle.key+')\'>View</button>';
                }
                newEntry.push('<tr'+selectedsubtitle+'><td class="td-small">' + language + '</td><td>'+subtitle.location+'</td><td>'+subtitle.codec+'</td><td>'+view+'</td></tr>');
            }
        });


        if (anysubtitleadded == false) {
            newEntry.pop();
            newEntry.push('<tr><td>No subtitles that matched your filter. Video has a total of '+selected_section.contents[i].subtitles.length+' subtitles.</td></tr>');
        }
        newEntry.push('</table></div>');
        newEntry.push('<div class="panel-footer"><button disabled class="btn btn-default btn-xs" onclick=\'subtitle_select_all("subtitle-'+selected_section.contents[i].key+'", true)\'>Select All</button> <button disabled class="btn btn-default btn-xs" onclick=\'subtitle_select_all("subtitle-'+selected_section.contents[i].key+'", false)\'>Clear Selection</button> <button disabled class="btn btn-default btn-xs" onclick=\'function_loader("subtitle_delete_confirm",["subtitle-'+selected_section.contents[i].key+'"]);\'>Delete Selected</button></div>');
        newEntry.push('</div>');
        $("#ContentBody").append(newEntry.join('\n'));
    }
    
      
    $('#LoadingModal').modal('hide');    
}

// The only purpose of this is to display a modal with an error message.
function display_error(message) {
    $('#myModalLabel').html('An error occured.');
    $('#myModalBody').html(message);
    $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
    $('#myModal').modal('show');
}


function calculate_pages() {
    //$('#ContentFoot').html('');
    var NumberOfPages = Math.ceil(selected_section.totalsize/globalvariables.options.items_per_page);
    var pages = '';
    var functiontocall = '';
    if(selected_section.contentstype == 'video') {
        functiontocall = 'fetch_section_type_movies';
    } else if (selected_section.contentstype == 'shows') {
        functiontocall = 'fetch_section_type_show';
    } else if (selected_section.contentstype == 'seasons') {
        //functiontocall = 'fetch_show_seasons';
        functiontocall = 'display_season';
        NumberOfPages = Math.ceil(selected_section.contents.length/globalvariables.options.items_per_page);
    } else if (selected_section.contentstype == 'episodes') {
        functiontocall = 'display_episodes';
        NumberOfPages = Math.ceil(selected_section.contents.length/globalvariables.options.items_per_page);
    }
    
	if (NumberOfPages > 1) {
		pages = pages + "\t<ul class='pagination pagination-sm'>";
		
		for (i = 0; i < NumberOfPages; i++) {
			if (i == selected_section.currentpage) {
				pages = pages + '<li class="active"><span onclick="set_pageToShow('+i+');' + functiontocall+ '('+selected_section.key+','+i+');">' + (i + 1) + '</span></li>';
				} else {
				pages = pages + '<li><span onclick="set_pageToShow('+i+');' + functiontocall+ '('+selected_section.key+','+i+');">' + (i + 1) + '</span></li>';
			}
			
		}
		pages = pages + "</ul>";
	}
	$("#ContentFoot").html(pages);
    
}

function show_options() {   
    $('#OptionsModal').modal('show');
}


// The sole purpose of this is to update when user is pressing the change page button. This allows for a shortcut to the display functions insted of fetching data again.
function set_pageToShow(pageToShow) {
    selected_section.currentpage = pageToShow;
}

$(function(ready) {
    
    
    $("input[name=items_per_page]").focusout(function() {
        
        if (!$.isNumeric($("input[name=items_per_page]").val())) {
            $("input[name=items_per_page]").addClass('bg-danger');
            $('#OptionsModalAlert').html('The items per page can only be numeric');
            $('#OptionsModalAlert').show();
            return false;
        }


        if( ($("input[name=items_per_page]").val() < globalvariables.items_per_page_min) || ($("input[name=items_per_page]").val() > globalvariables.items_per_page_max) ) {
            $("input[name=items_per_page]").addClass('bg-danger');
            $('#OptionsModalAlert').html('The items per page can only be between: ' + globalvariables.items_per_page_min + ' and ' + globalvariables.items_per_page_max);
            $('#OptionsModalAlert').show();
        } else {
            $('#OptionsModalAlert').hide();
            $("input[name=items_per_page]").removeClass('bg-danger');
        }
    });
});

function save_options() {
    if (!$.isNumeric($("input[name=items_per_page]").val())) {
        $("input[name=items_per_page]").addClass('bg-danger');
        $('#OptionsModalAlert').html('The items per page can only be numeric');
        $('#OptionsModalAlert').show();
        return false;
    }
    
    if( ($("input[name=items_per_page]").val() < globalvariables.items_per_page_min) || ($("input[name=items_per_page]").val() > globalvariables.items_per_page_max) ) {
        $("input[name=items_per_page]").addClass('bg-danger');
        $('#OptionsModalAlert').html('The items per page can only be between: ' + globalvariables.items_per_page_min + ' and ' + globalvariables.items_per_page_max);
        $('#OptionsModalAlert').show();
        return false;
    } else {
        $('#OptionsModalAlert').hide();
        $("input[name=items_per_page]").removeClass('bg-danger');
    }
    globalvariables.options.items_per_page = $("input[name=items_per_page]").val(); 
    globalvariables.options.options_auto_select_duplicate = $("input[name=options_auto_select_duplicate]").prop("checked");
    globalvariables.options.options_hide_empty_subtitles = $("input[name=options_hide_empty_subtitles]").prop("checked");
    globalvariables.options.options_hide_integrated = $("input[name=options_hide_integrated]").prop("checked");
    globalvariables.options.options_hide_local = $("input[name=options_hide_local]").prop("checked");
    globalvariables.options.options_only_multiple = $("input[name=options_only_multiple]").prop("checked");
    
    var save_options_to_server = new asynchelper(false,true);
    save_options_to_server.inline([
        function(callback) {
            var optionkeys = [];
            for (var key in globalvariables.options) {
                optionkeys.push(key);  
                save_options_to_server.functionsarray.push(function (callback, optionkeys) {
                    var currentkey = optionkeys.shift();
                    $.ajax({
                        url: '/webtools/settings/'+ currentkey + '/' + globalvariables.options[currentkey],
                        cache: false,
                        type: 'PUT',
                        dataType: 'JSON',
                        headers: {'Mysecret':globalvariables.secret},
                        success: function(data) {
                            //console.log(data);
                            webtools_log(1,'Options saved successfully.');
                            callback('Successfully saved ' + currentkey, optionkeys);
                        },
                        error: function(data) {
                            //console.log(data);
                            webtools_log(1,'Options has not been saved due to an error.');
                            callback('Failed saving ' + currentkey, optionkeys);
                        }
                    });

                });

            }
            callback('Fetched Optionkeys', optionkeys);
        }
    ], function(result) {webtools_log(0,result);$('#OptionsModal').modal('hide');});
}



function webtools_log(Loglevel, LogEntry) {
    var CurrentLog = []
    
    if ( (typeof(sessionStorage['WebToolsLog']) != 'undefined') && (sessionStorage['WebToolsLog'].length > 0) ) {
        var CurrentLog = JSON.parse(sessionStorage['WebToolsLog']);
    }
    if (Loglevel > 0) {
        var currentdate = new Date();
        var hour = '0' + currentdate.getHours();
        var minutes = '0' + currentdate.getMinutes();
        var seconds = '0' + currentdate.getSeconds();
        hour = hour.substr(hour.length-2);
        minutes = minutes.substr(minutes.length-2);
        seconds = seconds.substr(seconds.length-2);
        
        CurrentLog.push(hour +':' + minutes +':' + seconds  +' - ' + LogEntry);
    }
    
    sessionStorage['WebToolsLog'] = JSON.stringify(CurrentLog);
    
    //console.log('Logfile:');
    //console.log(JSON.parse(sessionStorage['WebToolsLog']));
}

function show_log() {
    $('#ContentHeader').html('Logfile');  
    
    if ( (typeof(sessionStorage['WebToolsLog']) != 'undefined') && (sessionStorage['WebToolsLog'].length > 0) ) {
        var CurrentLog = JSON.parse(sessionStorage['WebToolsLog']);
    } else {
        var CurrentLog = ['No entries in the logfile.'];
    }
    $('#ContentBody').html(CurrentLog.join('<br>'));  
    $('#ContentFoot').html('<button class="btn btn-default btn-xs" onclick="clear_log();">Clear Log</button>');
}

function clear_log() {
    sessionStorage['WebToolsLog'] = [];
    $('#myModalLabel').html('Logfile');
    $('#myModalBody').html('Logfile has been cleared.');
    $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
    $('#myModal').modal('show');
}


function view_subtitle(mediaKey, subtitleKey) {
    $.ajax({
        url: '/webtools/subtitle/'+ mediaKey + '/' + subtitleKey,
        cache: false,
        type: 'GET',
        dataType: 'JSON',
        headers: {'Mysecret':globalvariables.secret},
        success: function(data) {
            var subtitle = '<table class="table table-bordered">';
            subtitle += '<tr><th>Row#</th><th>Line</th></tr>';
            for (i=0;i<data.length;i++) {
                subtitle += '<tr><td class="bg-warning">#'+(i+1) + '</td><td>' + data[i] + '</td></tr>';
            }
            subtitle += '</table>';
            
            $('#myModalLabel').html('Viewing Subtitle');
            $('#myModalBody').html(subtitle);
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            $('#myModal').modal('show');
        },
        error: function(data) {
            $('#myModalLabel').html('An error occured.');
            $('#myModalBody').html(data);
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            $('#myModal').modal('show');
        }
    });        
}