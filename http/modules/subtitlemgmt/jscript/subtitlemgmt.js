/*
Required:
Hook module to webtools.functions namespace.
Create a object with the same name as the modules file.
Required property of the object is (with examples):
start : function() {webtools.log('This module has started');},
hasoptions: true/false,

if hasoptions is true, a link in the options menu will apear that points to modulename.show_options();

Every function has to be inside the modules namespace.
*/

webtools.functions.subtitlemgmt = {
	start: function() {
		webtools.longermodulestart = true;
		this.loadmorejavascripts.start();
	},
	loadmorejavascripts: new asynchelper(true, false),
	get_section_list: new asynchelper(true, false),
	moduledirectory: '/modules/subtitlemgmt/',
	secret: '',
	sections: [],
	options: {},
	save_options: function() {},
	show_options: function() {},
	hasoptions: true,
	items_per_page_max: 50,
	items_per_page_min: 5,
	selected_section: {
		key: 0,
		title: '',
		contents: [],
		totalsize: 0,
		currentpage: 0,
		parents_key: [],
		parents_title: [],
		contentstype: ''
	},
	calculate_pages: function() {},
	pagelist: [],
	set_pageToShow: function() {},
	fetch_section_type_show: function() {},
	fetch_show_seasons: function() {},
	fetch_season_episodes: function() {},
	fetch_section_type_movies: function() {},
	display_show: function() {},
	display_season: function() {},
	display_episodes: function () { },
	view_subtitle: function () { },
    search_shows: function() { },
	subtitle_select_all: function() {},
	subtitle_delete_confirm: function() {},
	subtitle_delete: function() {},
	upload_dialog: function() {},
	check_visibility: function() {},
	subtitle_ajax_calls: [],
	fetchSubtitle: function() {}
};
// Alias:
var subtitlemgmt = webtools.functions.subtitlemgmt;

// Loads the rest of the required javascriptfiles that holds some functions we use.
subtitlemgmt.loadmorejavascripts.inline([
	function(callback) {

		$.ajax({
			url: subtitlemgmt.moduledirectory + 'jscript/functions_video.js',
			cache: false,
			dataType: 'script',
			global: false,
			success: function() {
				callback();
			},
			error: function(data) {
				//console.log(data);
				subtitlemgmt.loadmorejavascripts.abort('Error, unable to find ' + subtitlemgmt.moduledirectory + 'jscript/functions_video.js');
			}
		});
	},
	function(callback) {
		$.ajax({
			url: subtitlemgmt.moduledirectory + 'jscript/functions_shows.js',
			cache: false,
			dataType: 'script',
			global: false,
			success: function() {
				callback();
			},
			error: function(data) {
				//console.log(data);
				subtitlemgmt.loadmorejavascripts.abort('Error, unable to find ' + subtitlemgmt.moduledirectory + 'jscript/functions_shows.js');
			}
		});
	}
]);

subtitlemgmt.loadmorejavascripts.completefunction = function() {

	$('#ModuleMenu').html('<a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">Libraries<span class="caret"></span></a><ul class="dropdown-menu" role="menu" id="SectionMenu"><li><a class="customlink" onclick="javascript:subtitlemgmt.get_section_list.start();">Refresh Sections</a></li></ul>');
	$('#ContentHeader').html('Welcome to Subtitle Management');
	var body = ['This is an unofficial manager for subtitles.',
		'Usage is on your own risk!</b>',
		'',
		'Current features:',
		'<ul><li>List all subtitles for a movie/tv show in your library. Both local (next to the movie in it\'s folder or one subfolder) and in the agents folder.</li><li>View the subtitle and see it\'s contents to determine what to delete.</li><li>Delete selected sidecar from the harddrive.</li><li>Options for output.</li></ul>',
		'To get started, select one of your Libraries via the Libraries menu at the top.'
	];
	$('#ContentBody').html(body.join('<br>'));
	subtitlemgmt.get_section_list.start();

	// Listen to an event of showing the options dialog so we can make sure it's values are correct.
	$("input[name=items_per_page]").focusout(function() {

		if (!$.isNumeric($("input[name=items_per_page]").val())) {
			$("input[name=items_per_page]").addClass('bg-danger');
			$('#OptionsModalAlert').html('The items per page can only be numeric');
			$('#OptionsModalAlert').show();
			return false;
		}

		if (($("input[name=items_per_page]").val() < subtitlemgmt.items_per_page_min) || ($("input[name=items_per_page]").val() > subtitlemgmt.items_per_page_max)) {
			$("input[name=items_per_page]").addClass('bg-danger');
			$('#OptionsModalAlert').html('The items per page can only be between: ' + subtitlemgmt.items_per_page_min + ' and ' + subtitlemgmt.items_per_page_max);
			$('#OptionsModalAlert').show();
		} else {
			$('#OptionsModalAlert').hide();
			$("input[name=items_per_page]").removeClass('bg-danger');
		}
	});


};

subtitlemgmt.get_section_list.inline([
	function(callback) {
		webtools.loading();
		//Name:SettingsFetch
		$.ajax({
			///webtools2?module=settings&function=getSettings
			url: '/webtools2',
			data: {
				'module': 'settings',
				'function': 'getSettings'
			},
			cache: false,
			dataType: 'JSON',
			success: function(data) {
				subtitlemgmt.options = data;
				callback('SettingsFetch:Success');
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed fetching the settings from the server.', data);
				subtitlemgmt.get_section_list.abort('Error: ' + data.statusText);
			}
		});
	},
	function(callback) {
		//Name:SectionFetch
		// Fetch sections and list them.
		$.ajax({
			url: '/webtools2',
			data: {
				'module': 'pms',
				'function': 'getSectionsList'
			},
			cache: false,
			dataType: 'JSON',
			success: function(data) {
				$('#SectionMenu').html('');
				//console.log(JSON.stringify(data));
				data.forEach(function(currentsection) {
					// Example: {"type":"movie","key":"1","title":"Home Videos"}                    
					var targetFunction = false;
					if (currentsection.type == 'movie') {
						targetFunction = 'subtitlemgmt.fetch_section_type_movies(' + currentsection.key + ',0);';
					} else if (currentsection.type == 'show') {
						targetFunction = 'subtitlemgmt.fetch_section_type_show(' + currentsection.key + ',0);';
					}

					if (targetFunction !== false) {
						$('#SectionMenu').append('<li><a class="customlink" onclick="javascript:' + targetFunction + '">' + currentsection.title + '</a></li>');
						subtitlemgmt.sections.push(currentsection);
					}
				});
				$('#SectionMenu').append('<li><a class="customlink" onclick="javascript:subtitlemgmt.get_section_list.start();">Refresh List of Libraries</a></li>');
				$('.modal').modal('hide');
				callback('SectionFetch:Success');
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed fetching the sections from the server.', data);
				subtitlemgmt.get_section_list.abort('Error: ' + data.statusText);
			}

		});
	}
], function(result) {
	webtools.log(result);
});

subtitlemgmt.save_options = function() {
	if (!$.isNumeric($("input[name=items_per_page]").val())) {
		$("input[name=items_per_page]").addClass('bg-danger');
		$('#OptionsModalAlert').html('The items per page can only be numeric');
		$('#OptionsModalAlert').show();
		return false;
	}
	// Make sure that the value is an integer.
	$("input[name=items_per_page]").val(Math.round($("input[name=items_per_page]").val()));


	if (($("input[name=items_per_page]").val() < subtitlemgmt.items_per_page_min) || ($("input[name=items_per_page]").val() > subtitlemgmt.items_per_page_max)) {
		$("input[name=items_per_page]").addClass('bg-danger');
		$('#OptionsModalAlert').html('The items per page can only be between: ' + subtitlemgmt.items_per_page_min + ' and ' + subtitlemgmt.items_per_page_max);
		$('#OptionsModalAlert').show();
		return false;
	} else {
		$('#OptionsModalAlert').hide();
		$("input[name=items_per_page]").removeClass('bg-danger');
	}

	subtitlemgmt.options.items_per_page = $("input[name=items_per_page]").val();
	subtitlemgmt.options.options_auto_select_duplicate = $("input[name=options_auto_select_duplicate]").prop("checked");
	subtitlemgmt.options.options_hide_empty_subtitles = $("input[name=options_hide_empty_subtitles]").prop("checked");
	subtitlemgmt.options.options_hide_integrated = $("input[name=options_hide_integrated]").prop("checked");
	subtitlemgmt.options.options_hide_withoutsubs = $("input[name=options_hide_withoutsubs]").prop("checked");
	subtitlemgmt.options.options_hide_local = $("input[name=options_hide_local]").prop("checked");
	subtitlemgmt.options.options_only_multiple = $("input[name=options_only_multiple]").prop("checked");
	subtitlemgmt.options.debug = $("input[name=debug]").prop("checked");

	var save_options_to_server = new asynchelper(false, true);
	save_options_to_server.inline([
		function(callback) {
			var optionkeys = [];
			for (var key in subtitlemgmt.options) {
				optionkeys.push(key);
				save_options_to_server.functionsarray.push(function(callback, optionkeys) {
					var currentkey = optionkeys.shift();
					$.ajax({
						url: '/webtools2?module=settings&function=putSetting&name=' + currentkey + '&value=' + subtitlemgmt.options[currentkey],
						cache: false,
						type: 'PUT',
						dataType: 'text',
						success: function(data) {
							webtools.log('Options saved successfully.');
							callback('Successfully saved ' + currentkey, optionkeys);
						},
						error: function(data) {
							webtools.log('Options has not been saved due to an error.');
							callback('Failed saving ' + currentkey, optionkeys);
						}
					});

				});

			}
			callback('Fetched Optionkeys', optionkeys);
		}
	], function(result) {
		webtools.log(result);
		$('.modal').modal('hide');
	});
}

subtitlemgmt.calculate_pages = function() {
	console.log('PAGE CALL');
/* CAN BELOW BE MOVED TO SEPERATE FUNCTOIN TO BE REUSED */
		var functiontocall = '';
		if (subtitlemgmt.selected_section.contentstype == 'video') {
			functiontocall = 'subtitlemgmt.fetch_section_type_movies';
		} else if (subtitlemgmt.selected_section.contentstype == 'shows') {
			functiontocall = 'subtitlemgmt.fetch_section_type_show';
		} else if (subtitlemgmt.selected_section.contentstype == 'seasons') {
			//functiontocall = 'fetch_show_seasons';
			functiontocall = 'subtitlemgmt.display_season';
		} else if (subtitlemgmt.selected_section.contentstype == 'episodes') {
			functiontocall = 'subtitlemgmt.display_episodes';
		}

		var pages = '';

		// LIST BEGIN
		pages = pages + "<span class='page-selector-list'><ul class='pagination pagination-sm'>";

		for (var i=0; i<subtitlemgmt.pagelist.length;i++) {
			if (i == subtitlemgmt.selected_section.currentpage) {
				pages = pages + '<li class="active"><span data-toggle="tooltip" title="' + subtitlemgmt.pagelist[i].key + ', Items: ' + subtitlemgmt.pagelist[i].size + '" onclick="subtitlemgmt.set_pageToShow(' + i + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + i + ');">' + subtitlemgmt.pagelist[i].displaykey + '</span></li>';
			} else {
				pages = pages + '<li><span data-toggle="tooltip" title="' + subtitlemgmt.pagelist[i].key + ', Items: ' + subtitlemgmt.pagelist[i].size + '" onclick="subtitlemgmt.set_pageToShow(' + i + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + i + ');">' + subtitlemgmt.pagelist[i].displaykey + '</span></li>';
			}

		}
		pages = pages + "</ul></span>";
		// LIST END

		// DROPDOWN BEGIN
		pages = pages + "<span class='page-selector-dropdown'><ul class='pagination pagination-sm '>";
		if ((subtitlemgmt.selected_section.currentpage - 1) >= 0) {
			pages = pages + '<li><span onclick="subtitlemgmt.set_pageToShow(' + (subtitlemgmt.selected_section.currentpage - 1) + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + (subtitlemgmt.selected_section.currentpage - 1) + ');">Previous</span></li>';
		}

		pages = pages + '<li><span><select id="pagenr" onChange="subtitlemgmt.set_pageToShow($(\'#pagenr\').val());' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',$(\'#pagenr\').val());">';
		for (var i=0; i<subtitlemgmt.pagelist.length;i++) {
				if (i == subtitlemgmt.selected_section.currentpage) {
					pages = pages + '<option selected value="' + i + '">' + subtitlemgmt.pagelist[i].displaykey;
				} else {
					pages = pages + '<option value="' + i + '">' + subtitlemgmt.pagelist[i].displaykey;
				}

		}
		pages = pages + '</select></span></li>';
		if ((subtitlemgmt.selected_section.currentpage + 1) < subtitlemgmt.pagelist.length) {
			pages = pages + '<li><span onclick="subtitlemgmt.set_pageToShow(' + (subtitlemgmt.selected_section.currentpage + 1) + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + (subtitlemgmt.selected_section.currentpage + 1) + ');">Next</span></li>';
		}
		pages = pages + "</ul></span>";
		// DROPDOWN END

		$("#navfoot").html(pages);
		/* END OF PAGING THAT MIGHT BE ABLE TO BE MOVED TO SEPERATE FUNCTION */
}

subtitlemgmt.show_options = function() {

	// Define the default view of options for SubtitleMGMT.
	$('#myModalLabel').html('Preferences');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button> <button type="button" class="btn btn-default" onclick="webtools.save_options();">Save Options</button>');


	$('#OptionsModalAlert').hide();
	var options = ['<tr><td><input type="checkbox" name="options_hide_local"></td><td>Hide local subtitles</td></tr>',
		'<tr><td><input type="checkbox" name="options_hide_integrated"></td><td>Hide integrated subtitles</td></tr>',
		'<tr><td><input type="checkbox" name="options_hide_withoutsubs"></td><td>Hide media without subs</td></tr>',
		'<tr><td><input type="checkbox" name="options_only_multiple"></td><td>Show only multiple subtitles/language</td></tr>',
		'<tr><td><input type="checkbox" name="debug"></td><td>Show debug in logs</td></tr>',
		'<tr><td><input type="text" name="items_per_page" size="2"></td><td>Items per page <span id="items_per_page_max_min"></span></td></tr>'
	]

	$('#OptionsTable').html(options.join('<br>'));

	$("input[name=debug]").prop("checked", subtitlemgmt.options.debug);
	$("input[name=options_hide_integrated]").prop("checked", subtitlemgmt.options.options_hide_integrated);
	$("input[name=options_hide_withoutsubs]").prop("checked", subtitlemgmt.options.options_hide_withoutsubs);
	$("input[name=options_hide_local]").prop("checked", subtitlemgmt.options.options_hide_local);
	$("input[name=options_hide_empty_subtitles]").prop("checked", subtitlemgmt.options.options_hide_empty_subtitles);
	$("input[name=options_only_multiple]").prop("checked", subtitlemgmt.options.options_only_multiple);
	$("input[name=options_auto_select_duplicate]").prop("checked", subtitlemgmt.options.options_auto_select_duplicate);
	$("input[name=items_per_page]").val(subtitlemgmt.options.items_per_page);
	$("#items_per_page_max_min").html('(Max: ' + subtitlemgmt.items_per_page_max + '. Min: ' + subtitlemgmt.items_per_page_min + ')');
	$('#myModal').modal('show');
}

subtitlemgmt.set_pageToShow = function(pageToShow) {
	subtitlemgmt.selected_section.currentpage = Number(pageToShow);
}

subtitlemgmt.upload_dialog = function(videokey) {
	webtools.log('Requesting getParts for movie/episode with key: ' + videokey);
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Upload Subtitle');
	$('#myModalBody').html('Fetching info about video/episode.');
	$('#myModalFoot').html('<button type="button" disabled class="btn btn-default" onclick="subtitlemgmt.upload();">Upload</button> <button disabled type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	$('#myModal').modal('show');
	
	$.ajax({
		url: '/webtools2?module=pms&function=getParts&key=' + videokey,
		type: 'GET',
		dataType: 'JSON',
		success: function(data) {
			webtools.log('Received getParts' + JSON.stringify(data));
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Upload Subtitle');
		
	
			//Example return of above:  /home/cabox/workspace/dummylibraries/movies/10 Things I Hate About You (1999)/10 Things I Hate About You (1999).mp4
			var subtitleform = [
				'<form enctype="multipart/form-data" method="post" id="subtitleupload" onSubmit="return false;">',
				'<table class="table table-bordered" id="subtitleuploadtable">',
				'<tr><td colspan=2>If a file exists with the selected language and file extension, it will be overwritten.</td></tr>',
				'<tr><td>Subtitle:</td><td><input id="localFile" name="localFile" type="file"></td></tr>',
				'<tr><td>Language:</td><td><select id="subtitlelanguage">{list}</select></td></tr>',
				'<tr><td>Subtitle target file:</td><td><select id="targetfile">{targetfile}</select><br>Note: Hover over files in above selection to see full path.</td></tr>',
				'</table></form>',
			];
			subtitleform = subtitleform.join('\n')

			var languagelist = [];
			for (var key in webtools.languagecodes) {
				languagelist.push('<option value="' + key + '">' + webtools.languagecodes[key] + ' (.' + key + ')');
			}
			
			var targetfile = [];
			for (var tkey in data) {
				var toshow = '';
				if (data[tkey].indexOf('\\') != '-1') {
					toshow = data[tkey].substring(data[tkey].lastIndexOf('\\') +1);
				} else {
					toshow = data[tkey].substring(data[tkey].lastIndexOf('/') +1);
				}
				targetfile.push('<option value="' + data[tkey] + '" title="' + data[tkey] + '">' + toshow);
			}
			
			subtitleform = subtitleform.replace('{list}', languagelist.join('\n'));
			subtitleform = subtitleform.replace('{targetfile}', targetfile.join('\n'));
			
			$('#myModalBody').html(subtitleform);
			$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="subtitlemgmt.upload();">Upload</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
			$('#myModal').modal('show');
		},
		error: function() {
			webtools.log('Error occured while requesting getParts for video/episode: ' + videokey);
		}
	})

}

subtitlemgmt.upload = function() {
	webtools.log('Initiating upload procedure of : ' + $('#localFile').val());	
	var uploadfileextension = $('#localFile').val();
	var targetfile = $('#targetfile').val();
	var language = $('#subtitlelanguage').val();
	
	uploadfileextension = uploadfileextension.substring(uploadfileextension.lastIndexOf('.'));
	
	var newfilename = targetfile.substring(0, targetfile.lastIndexOf('.')) + '.' + language + uploadfileextension;
	webtools.log('Remote filename will be: ' + newfilename);

	var form = document.forms.namedItem("subtitleupload");
	var formobject = new FormData(form)

	$('#myModalBody').html('Uploading file...');
	$('#myModalFoot').html('<button disabled type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	
	var functiontocall = '';
	if (subtitlemgmt.selected_section.contentstype == 'video') {
		functiontocall = 'subtitlemgmt.fetch_section_type_movies';
	} else if (subtitlemgmt.selected_section.contentstype == 'episodes') {
		functiontocall = 'subtitlemgmt.display_episodes';
	}
	
	formobject.append("remoteFile", newfilename);
	$.ajax({
		url: '/webtools2?module=pms&function=uploadFile',
		type: 'POST',
		data: formobject,
		processData: false, // tell jQuery not to process the data
		contentType: false, // tell jQuery not to set contentType
		success: function(data) {
			webtools.log('Upload of ' + newfilename + ' was sucessfull.');
			$('#myModalBody').html('Successfully uploaded the file:<br>' + newfilename);
			$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="subtitlemgmt.set_pageToShow(' + subtitlemgmt.selected_section.currentpage + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + subtitlemgmt.selected_section.currentpage + ');">Refresh Page</button>');
		},
		error: function(data) {
			webtools.log('Error occured while uploading: ' + data.responseText);
			$('#myModalBody').html('Failed to upload the file: <br>' + data.responseText);
			$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');

		}
	});


}