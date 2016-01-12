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
	set_pageToShow: function() {},
	fetch_section_type_show: function() {},
	fetch_show_seasons: function() {},
	fetch_season_episodes: function() {},
	fetch_section_type_movies: function() {},
	display_show: function() {},
	display_season: function() {},
	display_episodes: function() {},
	view_subtitle: function() {},
	subtitle_select_all: function() {},
	subtitle_delete_confirm: function() {},
	subtitle_delete: function() {}
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
				webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
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
				webtools.display_error('Failed fetching the sections from the server. Please restart the server.', data);
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
	//$('#ContentFoot').html('');
	var NumberOfPages = Math.ceil(subtitlemgmt.selected_section.totalsize / subtitlemgmt.options.items_per_page);
	var pages = '';
	var functiontocall = '';
	if (subtitlemgmt.selected_section.contentstype == 'video') {
		functiontocall = 'subtitlemgmt.fetch_section_type_movies';
	} else if (subtitlemgmt.selected_section.contentstype == 'shows') {
		functiontocall = 'subtitlemgmt.fetch_section_type_show';
	} else if (subtitlemgmt.selected_section.contentstype == 'seasons') {
		//functiontocall = 'fetch_show_seasons';
		functiontocall = 'subtitlemgmt.display_season';
		NumberOfPages = Math.ceil(subtitlemgmt.selected_section.contents.length / subtitlemgmt.options.items_per_page);
	} else if (subtitlemgmt.selected_section.contentstype == 'episodes') {
		functiontocall = 'subtitlemgmt.display_episodes';
		NumberOfPages = Math.ceil(subtitlemgmt.selected_section.contents.length / subtitlemgmt.options.items_per_page);
	}

	if (NumberOfPages > 10) {
		pages = pages + "\t<ul class='pagination pagination-sm'>";
		if ((subtitlemgmt.selected_section.currentpage - 1) >= 0) {
			pages = pages + '<li><span onclick="subtitlemgmt.set_pageToShow(' + (subtitlemgmt.selected_section.currentpage - 1) + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + (subtitlemgmt.selected_section.currentpage - 1) + ');">Previous</span></li>';
		}

		pages = pages + '<li><span><select id="pagenr" onChange="subtitlemgmt.set_pageToShow($(\'#pagenr\').val());' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',$(\'#pagenr\').val());">';
		for (var f = 0; f < NumberOfPages; f++) {
			if (f == subtitlemgmt.selected_section.currentpage) {
				pages = pages + '<option selected value="' + f + '">' + (f + 1);
			} else {
				pages = pages + '<option value="' + f + '">' + (f + 1);
			}

		}
		pages = pages + '</select></span></li>';

		if ((subtitlemgmt.selected_section.currentpage + 1) < NumberOfPages) {
			pages = pages + '<li><span onclick="subtitlemgmt.set_pageToShow(' + (subtitlemgmt.selected_section.currentpage + 1) + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + (subtitlemgmt.selected_section.currentpage + 1) + ');">Next</span></li>';
		}
		pages = pages + "</ul>";
	} else if (NumberOfPages > 1) {
		pages = pages + "\t<ul class='pagination pagination-sm'>";

		for (i = 0; i < NumberOfPages; i++) {
			if (i == subtitlemgmt.selected_section.currentpage) {
				pages = pages + '<li class="active"><span onclick="subtitlemgmt.set_pageToShow(' + i + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + i + ');">' + (i + 1) + '</span></li>';
			} else {
				pages = pages + '<li><span onclick="subtitlemgmt.set_pageToShow(' + i + ');' + functiontocall + '(' + subtitlemgmt.selected_section.key + ',' + i + ');">' + (i + 1) + '</span></li>';
			}

		}
		pages = pages + "</ul>";
	}
	$("#navfoot").html(pages);

}

subtitlemgmt.show_options = function() {

	// Define the default view of options for SubtitleMGMT.
	$('#myModalLabel').html('Preferences');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button> <button type="button" class="btn btn-default" onclick="webtools.save_options();">Save Options</button>');


	$('#OptionsModalAlert').hide();
	var options = ['<tr><td><input type="checkbox" name="options_hide_local"></td><td>Hide local subtitles</td></tr>',
		'<tr><td><input type="checkbox" name="options_hide_integrated"></td><td>Hide integrated subtitles</td></tr>',
		'<tr><td><input type="checkbox" name="options_only_multiple"></td><td>Show only multiple subtitles/language</td></tr>',
		'<tr><td><input type="checkbox" name="debug"></td><td>Show debug in logs</td></tr>',
		'<tr><td><input type="text" name="items_per_page" size="2"></td><td>Items per page <span id="items_per_page_max_min"></span></td></tr>'
	]

	$('#OptionsTable').html(options.join('<br>'));

	$("input[name=debug]").prop("checked", subtitlemgmt.options.debug);
	$("input[name=options_hide_integrated]").prop("checked", subtitlemgmt.options.options_hide_integrated);
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