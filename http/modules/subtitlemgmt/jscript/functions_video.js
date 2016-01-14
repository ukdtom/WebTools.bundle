subtitlemgmt.fetch_section_type_movies = function(section_key, pageToShow) {
	$('#navfoot').html('');
	$('#ContentFoot').html('');
	subtitlemgmt.selected_section.currentpage = Number(pageToShow);
	var get_section_video = new asynchelper(false, false);
	get_section_video.inline([
		function(callback, section_key) {
			webtools.loading();
			$('#ContentFoot').html('');
			if (Number(section_key) == 'NaN') {
				get_section_video.abort('Incorrect section key provided. Needs to be number.');
			}

			subtitlemgmt.sections.forEach(function(section) {
				if (section.key == section_key) {
					subtitlemgmt.selected_section.key = section.key;
					subtitlemgmt.selected_section.title = section.title;
					subtitlemgmt.selected_section.contents = [];
					subtitlemgmt.selected_section.parents_key = [];
					subtitlemgmt.selected_section.parents_title = [];
				}
			});

			callback('Success');
		},
		function(callback) {
			// First, lets check how big the section is that the user requested to see.
			$.ajax({
				url: '/webtools2?module=pms&function=getSectionSize&key=' + subtitlemgmt.selected_section.key,
				cache: false,
				dataType: 'text',
				success: function(data) {
					webtools.loading('Library Size: ' + data.replace(/"/g, ''));
					subtitlemgmt.selected_section.totalsize = data.replace(/"/g, '');
					callback('Success');
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the size of the section from the server. Please restart the server.', data);
					get_section_video.abort('Error: ' + data.statusText);
				}
			});
		},
		function(callback) {

			var start = (Number(subtitlemgmt.selected_section.currentpage) * Number(subtitlemgmt.options.items_per_page));
			webtools.loading('Library Size: ' + subtitlemgmt.selected_section.totalsize + '<br>Currently fetching: ' + start + '->' + (start + subtitlemgmt.options.items_per_page));

			$.ajax({
				url: '/webtools2?module=pms&function=getSection&key=' + subtitlemgmt.selected_section.key + '&start=' + start + '&size=' + subtitlemgmt.options.items_per_page + '&getSubs=true',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					//console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
					data.forEach(function(video) {
						video.subtitles.showsubs = true;
						subtitlemgmt.selected_section.contents.push(video);
						subtitlemgmt.selected_section.contentstype = 'video';
					});

					callback('Batchfetch complete.');
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the section contents from the server. Please restart the server.', data);
					get_section_video.abort('Error: ' + data.statusText);
				}
			});
		}
	], function() {
		subtitlemgmt.display_episodes();
	});
	get_section_video.start(section_key);
}

subtitlemgmt.display_episodes = function() {
	window.scrollTo(0, 0);
	/*
	    Go through all the options and modify the output accordingly.
	*/

	var end = ((subtitlemgmt.selected_section.currentpage * subtitlemgmt.options.items_per_page) + subtitlemgmt.options.items_per_page);
	if (end > subtitlemgmt.selected_section.contents.length) {
		end = subtitlemgmt.selected_section.contents.length;
	}

	var start = (subtitlemgmt.selected_section.currentpage * subtitlemgmt.options.items_per_page);
	if (start >= subtitlemgmt.selected_section.contents.length) {
		start = 0;
	}

	//selected_section.prepared_content


	webtools.loading('Applying filters and preparing output.');
	if (subtitlemgmt.selected_section.parents_key.length > 0) {
		$('#ContentHeader').html('<a class="customlink" onclick="javascript:subtitlemgmt.fetch_section_type_show(' + subtitlemgmt.selected_section.parents_key[0] + ',0)">' + subtitlemgmt.selected_section.parents_title[0] + '</a> /' +
			'<a class="customlink" onclick="javascript:subtitlemgmt.fetch_show_seasons(' + subtitlemgmt.selected_section.parents_key[1] + ',0)">' + subtitlemgmt.selected_section.parents_title[1] + '</a> /' +
			subtitlemgmt.selected_section.title);
	} else {
		$('#ContentHeader').html(subtitlemgmt.selected_section.title);
	}

	subtitlemgmt.calculate_pages();

	$('#ContentBody').html('');

	for (var i = start; i < end; i++) {
		var discoveredlanguages = [];
		subtitlemgmt.selected_section.contents[i].subtitles.forEach(function(subtitle) {
			if (discoveredlanguages.length == 0) {
				discoveredlanguages.push([subtitle.languageCode, 1]);
			} else {
				added = false;
				for (l = 0; l < discoveredlanguages.length; l++) {
					if (discoveredlanguages[l][0] == subtitle.languageCode) {
						discoveredlanguages[l][1] += 1;
						added = true;
					}
				}
				if (added === false) {
					//log_to_console("We didn't find a match afterall, we have to add to position: " + discovered_languages.length);
					discoveredlanguages.push([subtitle.languageCode, 1]);
				}
			}
		});
		// End of Options Time!
		var AppendToTitle = '';
		if (subtitlemgmt.selected_section.contentstype == 'episodes') {
			AppendToTitle = '#' + subtitlemgmt.selected_section.contents[i].episode + ". ";
		}
		var newEntry = ['<div class="panel panel-default">'];
		newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + AppendToTitle + subtitlemgmt.selected_section.contents[i].title + '</h4></div>');
		newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');
		newEntry.push('<tr><th></th><th class="td-small">Lang.</th><th>Location</th><th>Codec</th><th></th></tr>');

		var anysubtitleadded = false;
		subtitlemgmt.selected_section.contents[i].subtitles.forEach(function(subtitle) {
			var display_subtitle = true;
			var language = 'None';
			var selectedsubtitle = '';

			if (subtitle.languageCode != null) {
				if (typeof(languagecodes[subtitle.languageCode.toLowerCase()]) != 'undefined') {
					//language = '<img src="flags/blank.png" class="flag flag-'+languagecodes[subtitle.languageCode.toUpperCase()].toLowerCase()+'" alt="'+subtitle.languageCode.toUpperCase()+'"/>';
					var languagetext = languagecodes[subtitle.languageCode.toLowerCase()];
					if (languagecodes[subtitle.languageCode.toLowerCase()].length > 8) {
						languagetext = languagecodes[subtitle.languageCode.toLowerCase()].substr(0, 6) + '...';
					}
					language = '<span data-toggle="tooltip" title="' + languagecodes[subtitle.languageCode.toLowerCase()] + '">' + languagetext + '</span>';
				} else {
					language = subtitle.languageCode.toLowerCase();
				}
			}

			if (subtitle.selected != null) {
				selectedsubtitle = ' class="bg-success"';
			}

			// Options filtering
			if (subtitlemgmt.options.options_only_multiple) {
				display_subtitle = false;
				discoveredlanguages.forEach(function(language) {
					if ((language[0] == subtitle.languageCode) && (language[1] > 1)) {
						display_subtitle = true;
					}
				});
			}

			if ((subtitlemgmt.options.options_hide_integrated) && (subtitle.location == 'Embedded')) {
				display_subtitle = false;
			}

			if ((subtitlemgmt.options.options_hide_local) && (subtitle.location == 'Sidecar')) {
				display_subtitle = false;
			}
			// End of options filtering
			if (display_subtitle) {
				anysubtitleadded = true;
				var view = '';
				var checkbox = '';
				if (subtitle.location == 'Sidecar') {
					checkbox = '<input type="checkbox" name="subtitle-' + subtitlemgmt.selected_section.contents[i].key + '" value="' + subtitlemgmt.selected_section.contents[i].key + ',' + subtitle.key + '">';
					view = '<button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.view_subtitle(' + subtitlemgmt.selected_section.contents[i].key + ',' + subtitle.key + ')\'>View</button>';
				}
				newEntry.push('<tr' + selectedsubtitle + '><td class="td-small">' + checkbox + '</td><td class="td-small">' + language + '</td><td>' + subtitle.location + '</td><td>' + subtitle.codec + '</td><td>' + view + '</td></tr>');
			}
		});

		if (anysubtitleadded == false) {
			newEntry.pop();
			newEntry.push('<tr><td>No subtitles that matched your filter. Video has a total of ' + subtitlemgmt.selected_section.contents[i].subtitles.length + ' subtitles.</td></tr>');
		}
		newEntry.push('</table></div>');
		newEntry.push('<div class="panel-footer"><button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_select_all("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '", true)\'>Select All</button> <button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_select_all("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '", false)\'>Clear Selection</button> <button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_delete_confirm("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '");\'>Delete Selected</button></div>');
		newEntry.push('</div>');
		$("#ContentBody").append(newEntry.join('\n'));
	}

	$('.modal').modal('hide');
}

subtitlemgmt.view_subtitle = function(mediaKey, subtitleKey) {
	webtools.loading();
	$.ajax({
		url: '/webtools2?module=pms&function=showSubtitle&key=' + subtitleKey,
		cache: false,
		type: 'GET',
		dataType: 'JSON',
		success: function(data) {
			var subtitle = '<table class="table table-bordered">';
			subtitle += '<tr><th>Row#</th><th>Line</th></tr>';
			for (i = 0; i < data.length; i++) {
				subtitle += '<tr><td class="bg-warning">#' + (i + 1) + '</td><td>' + data[i] + '</td></tr>';
			}
			subtitle += '</table>';

			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Viewing Subtitle');
			$('#myModalBody').html(subtitle);
			$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed fetching the section contents from the server. Please restart the server.', data);
		}
	});
}

subtitlemgmt.subtitle_select_all = function(videoKey, boolean) {
	if (boolean == true) {
		$('input[name=' + videoKey + ']').prop('checked', true);
	} else {
		$('input[name=' + videoKey + ']').prop('checked', false);
	}
}

subtitlemgmt.subtitle_delete_confirm = function(videoKey) {
	if ($('input[name=' + videoKey + ']:checked').length > 0) {
		$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Delete subtitle?');
		$('#myModalBody').html('Are you sure you want to remove the selected subtitles?');
		$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="subtitlemgmt.subtitle_delete(\'' + videoKey + '\');">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>');
		if ($('#myModal').is(':visible') === false) {
			$('#myModal').modal({
				keyboard: false,
				backdrop: 'static'
			});
			$('#myModal').modal('show');
		}
	}
}

subtitlemgmt.subtitle_delete = function(videoKey) {
	$('#myModalBody').html('Working...');
	$('#myModalFoot').html('<button type="button" disabled class="btn btn-default" data-dismiss="modal">Close</button>');
	var delete_query = new asynchelper(false, false);
	var subtitlearray = [];
	delete_query.inline([], function(result) {
		result.shift();

		$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Deleted Subtitles');
		$('#myModalBody').html(result.join('<br>'));
		$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
		if ($('#myModal').is(':visible') === false) {
			$('#myModal').modal({
				keyboard: false,
				backdrop: 'static'
			});
			$('#myModal').modal('show');
		}
	});

	$('input[name=' + videoKey + ']:checked').each(function() {
		subtitlearray.push($(this).val());
		delete_query.functionsarray.push(function(callback, subtitlearray) {
			var splitstring = subtitlearray.shift();
			splitstring = splitstring.split(',');
			$.ajax({
				url: '/webtools2?module=pms&function=delSub&key=' + splitstring[0] + '&subKey=' + splitstring[1],
				type: 'DELETE',
				cache: false,
				success: function(response, status, xhr) {
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').prop('disabled', true);
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').prop('checked', false);
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').parent().parent().addClass('bg-danger');
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').parent().parent().fadeOut(2000);
					webtools.log("Deleted File: " + response['Deleted file']);
					callback("Deleted File: " + response['Deleted file'], subtitlearray);
				},
				error: function(response) {
					webtools.log(JSON.stringify(response));
					callback(JSON.stringify(response), subtitlearray);
				}
			});

		});

	});
	delete_query.start(subtitlearray);

};