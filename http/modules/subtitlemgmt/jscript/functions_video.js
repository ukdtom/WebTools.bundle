
/*

PAGING:
LetterNumber

A - Size 4
B - Size 20 [SPLIT!]
B1 - Size 5, Start 0
B2 - Size 5, start B1.size + B1.Start
B3 - Size 5, start B2.size + B2.Start
B4 - Size 5. start B3.size + B3.Start
*/
subtitlemgmt.fetch_section_type_movies = function(section_key, pageToShow) {
	
	subtitlemgmt.subtitle_ajax_calls.forEach(function(ajaxcall) {
		//console.log(ajaxcall);
		if(ajaxcall && ajaxcall.readyState != 4){
					if (typeof ajaxcall.abort === "function") { 
            ajaxcall.abort();
					}
        }
	})
	
	
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
					subtitlemgmt.selected_section.contentstype = 'video';
				}
			});

			callback('Success');
		},
		function(callback) {
			$.ajax({
				url: '/webtools2?module=pms&function=getSectionLetterList&key=' + subtitlemgmt.selected_section.key,
				type: 'get',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					//console.log(data);
					subtitlemgmt.pagelist = [];
					for (var key in data) {
						var start = 0;
						//console.log(key);
						//console.log(data[key].size + ' > ' + subtitlemgmt.options.items_per_page)
						if (data[key].size > subtitlemgmt.options.items_per_page) {
							var pages = Math.round(data[key].size / subtitlemgmt.options.items_per_page);
							
							console.log('Key/Pages: ' + key + '/' + pages)
							
							for (var i =0 ; i <= pages; i++) {
								var size = data[key].size;
								start = (subtitlemgmt.options.items_per_page * i);
								
								console.log('Start: ' + start);
								console.log('i:' + i);
								if (data[key].size > subtitlemgmt.options.items_per_page) {
									size = subtitlemgmt.options.items_per_page
									data[key].size = data[key].size - subtitlemgmt.options.items_per_page;
								}
								
								subtitlemgmt.pagelist.push({'key':data[key].key,'size': size, 'displaykey':key + (i+1), 'start':start});	
							}
						} else {
							subtitlemgmt.pagelist.push({'key':data[key].key,'size':data[key].size, 'displaykey':key, 'start':start});
						}
					}
					console.log(subtitlemgmt.pagelist);
					subtitlemgmt.calculate_pages();
					//webtools.loading('Library Size: ' + data.replace(/"/g, ''));
					//subtitlemgmt.selected_section.totalsize = data.replace(/"/g, '');
					callback('Success');
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the size of the section from the server.', data);
					get_section_video.abort('Error: ' + data.statusText);
				}
			});
		},
		function(callback) {
			//console.log(subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].key);
			//var start = (Number(subtitlemgmt.selected_section.currentpage) * Number(subtitlemgmt.options.items_per_page));
			webtools.loading('Currently fetching information and subtitles for letter ' + subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].displaykey + " and items: " + subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].start + '->' + subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].size);

			$.ajax({
				// 
				url: '/webtools2?module=pms&function=getSectionByLetter&key=' + subtitlemgmt.selected_section.key + '&start=' + subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].start + '&size=' + subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].size + '&letterKey=' + encodeURI(subtitlemgmt.pagelist[subtitlemgmt.selected_section.currentpage].key) + '&getSubs=true',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					//console.log(data);
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
					webtools.display_error('Failed fetching the section contents from the server.', data);
					get_section_video.abort('Error: ' + data.statusText);
				}
			});
		}
	], function() {
		subtitlemgmt.display_episodes();	
	});
	
	get_section_video.start(section_key);
}

subtitlemgmt.display_episodes = function (forceAll) {
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
			subtitlemgmt.selected_section.title + (subtitlemgmt.selected_section.type === 'movie' ? '<div class="input-group-btn"><input type="search" class="form-control search" placeholder="search.." style="width:200px;margin-top:5px;float:left;" id="searchvalue"></input><button class="btn btn-default" type="button" onclick="javascript:subtitlemgmt.search_shows();" style="margin-top:5px">Search</button></div>' : ''))
        
	} else {
	    /* QUICK FIXED.. MOVING TO V3 SOON ...*/
	    /* QUICK FIXED.. MOVING TO V3 SOON ...*/
	    $('#ContentHeader').html(subtitlemgmt.selected_section.title + '<div class="input-group-btn"><input type="search" class="form-control search" placeholder="search.." style="width:200px;margin-top:5px;float:left;" id="searchvalue"></input><button class="btn btn-default" type="button" onclick="javascript:subtitlemgmt.search_shows();" style="margin-top:5px">Search</button></div>');
	}

	//subtitlemgmt.calculate_pages();

	$('#ContentBody').html('');


	if (forceAll) {
	    start = 0
	    end = subtitlemgmt.selected_section.contents.length;
	}
	for (var i = start; i < end; i++) {
	    if (subtitlemgmt.options.options_hide_withoutsubs && subtitlemgmt.selected_section.contents[i].subtitles.length === 0) {
	        continue;
	    }

		var discoveredlanguages = [];
		
	    // DISABLE HERE IF NOT TO USE FETCH ALL AT ONCE
		subtitlemgmt.selected_section.contents[i].subtitles.forEach(function (subtitle) {

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
		// DISABLE HERE IF NOT TO USE FETCH ALL AT ONCE
		// End of Options Time!
		var AppendToTitle = '';
		if (subtitlemgmt.selected_section.contentstype == 'episodes') {
			AppendToTitle = '#' + subtitlemgmt.selected_section.contents[i].episode + ". ";
		}
		var newEntry = ['<div class="panel panel-default fetchsubtitles">'];
		newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + AppendToTitle + subtitlemgmt.selected_section.contents[i].title + '</h4></div>');
		//Add this to below if needed <span id="showsubtitle_' + subtitlemgmt.selected_section.contents[i].key + '" onClick="subtitlemgmt.showsubtitletable(this);">Show Fetched Subtitles</span>
		newEntry.push('<div class="panel-body subtitle"><input type="hidden" class="mediakey" value="' + subtitlemgmt.selected_section.contents[i].key + '"><table class="table table-condensed subtitletable">');
		newEntry.push('<tr><th></th><th class="td-small">Lang.</th><th>Location</th><th>Codec</th><th></th></tr>');

		var anysubtitleadded = false;
	    // DISABLE HERE IF NOT TO USE FETCH ALL AT ONCE

		subtitlemgmt.selected_section.contents[i].subtitles.forEach(function(subtitle) {
			var display_subtitle = true;
			var language = 'None';
			var selectedsubtitle = '';

			if (subtitle.languageCode != null) {
				if (typeof(webtools.languagecodes[subtitle.languageCode.toLowerCase()]) != 'undefined') {
					//language = '<img src="flags/blank.png" class="flag flag-'+webtools.languagecodes[subtitle.languageCode.toUpperCase()].toLowerCase()+'" alt="'+subtitle.languageCode.toUpperCase()+'"/>';
					var languagetext = webtools.languagecodes[subtitle.languageCode.toLowerCase()];
					if (webtools.languagecodes[subtitle.languageCode.toLowerCase()].length > 8) {
						languagetext = webtools.languagecodes[subtitle.languageCode.toLowerCase()].substr(0, 6) + '...';
					}
					language = '<span data-toggle="tooltip" title="' + webtools.languagecodes[subtitle.languageCode.toLowerCase()] + '">' + languagetext + '</span>';
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

			if (subtitlemgmt.options.options_hide_integrated && subtitle.location == 'Embedded') {
				display_subtitle = false;
			}

			if (subtitlemgmt.options.options_hide_local && subtitle.location == 'Sidecar') {
				display_subtitle = false;
			}
			// End of options filtering
			if (display_subtitle) {
			    anysubtitleadded = true;
			    var download = '';
				var view = '';
				var checkbox = '';
				if (subtitle.location == 'Sidecar' || subtitle.location == 'Agent') {
					checkbox = '<input type="checkbox" name="subtitle-' + subtitlemgmt.selected_section.contents[i].key + '" value="' + subtitlemgmt.selected_section.contents[i].key + ',' + subtitle.key + '">';
					view = '<button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.view_subtitle(' + subtitlemgmt.selected_section.contents[i].key + ',' + subtitle.key + ')\'>View</button>';
				    download = '<button class="btn btn-default btn-xs" onclick="window.open(\'webtools2?module=pms&function=downloadSubtitle&key=' + subtitle.key + '\');">Download</button>';
				}
				newEntry.push('<tr' + selectedsubtitle + '><td class="td-small">' + checkbox + '</td><td class="td-small">' + language + '</td><td>' + subtitle.location + '</td><td>' + subtitle.codec + '</td><td>' + view + ' ' + download + '</td></tr>');
			}
		});
		
		// DISABLE HERE IF NOT TO USE FETCH ALL AT ONCE

		if (anysubtitleadded === false) {
		    if (subtitlemgmt.options.options_hide_withoutsubs) {
		        continue;
		    }

			newEntry.pop();
			// DISABLE HERE IF NOT TO USE FETCH ALL AT ONCE
			newEntry.push('<tr><td>No subtitles that matched your filter. Video has a total of ' + subtitlemgmt.selected_section.contents[i].subtitles.length + ' subtitles.</td></tr>');
		}
		newEntry.push('</table></div>');
		newEntry.push('<div class="panel-footer"><button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_select_all("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '", true)\'>Select All</button> <button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_select_all("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '", false)\'>Clear Selection</button> <button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.subtitle_delete_confirm("subtitle-' + subtitlemgmt.selected_section.contents[i].key + '");\'>Delete Selected</button> <button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.upload_dialog("' + subtitlemgmt.selected_section.contents[i].key + '")\'>Upload Subtitle</button></div>');
		newEntry.push('</div>');
		$("#ContentBody").append(newEntry.join('\n'));
	}

	$('.modal').modal('hide');
    //subtitlemgmt.check_visibility();

	$("input").on('keyup', function (e) {
	    if (e.keyCode == 13) {
	        subtitlemgmt.search_shows();
	    }
	});
}

$(window).scroll(function() {
	
		//subtitlemgmt.check_visibility();
		
});

subtitlemgmt.check_visibility = function () {
	// Currently unused
	$('.fetchsubtitles').each(function () {
			
		
    var top_of_element = $(this).offset().top;
    var bottom_of_element = $(this).offset().top + $(this).outerHeight();
    var bottom_of_screen = screen.availHeight + $(window).scrollTop();
		//console.log('top_of_element: ' + top_of_element);
		//console.log('bottom_of_element: ' + bottom_of_element);
		//console.log('bottom_of_screen: ' + bottom_of_screen);
    if((bottom_of_screen > top_of_element) && (bottom_of_screen > bottom_of_element)){
        // The element is visible, do something
			//console.log($('.subtitletable',this).html());
			$('#showsubtitle_' + $('.mediakey',this).val() ).html('Fetching Subtitledata');
			$('.subtitletable',this).html('<tr><td>Fetching Subtitledata....</td></tr>');
			// 
			//$(this).html($(this).html() + "VISIBLE");
			$(this).removeClass('fetchsubtitles');
			
			// Call this here and update accordingly: /webtools2?module=pms&function=getSubtitles&key=<Media Rating Key>
			// Store active Ajax calls in an array, abort them when reloading page or changing page.
			subtitlemgmt.subtitle_ajax_calls.push(subtitlemgmt.fetchSubtitle($('.mediakey',this).val()), this);
			//subtitlemgmt.subtitle_ajax_calls[index];
    }
    else {
			console.log('NotVisble');
			//$(this).html($(this).html() + "NOTVISIBLE");
        // The element is not visible, do something else
    }

			
			})
}


subtitlemgmt.fetchSubtitle = function (mediakey, context) {
	// Currently unused
	return $.ajax({
				url: '/webtools2?module=pms&function=getSubtitles&key=' + mediakey,
				type: 'GET',
				dataType: 'JSON',
				success: function(data) {
					var counter = 0;
					var subtitlecontent = ['<tr><th></th><th class="td-small">Lang.</th><th>Location</th><th>Codec</th><th></th></tr>'];
					data.forEach(function(subtitle) {
						
						var display_subtitle = true;
						var language = 'None';
						var selectedsubtitle = '';

						if (subtitle.languageCode != null) {
							if (typeof(webtools.languagecodes[subtitle.languageCode.toLowerCase()]) != 'undefined') {
								//language = '<img src="flags/blank.png" class="flag flag-'+webtools.languagecodes[subtitle.languageCode.toUpperCase()].toLowerCase()+'" alt="'+subtitle.languageCode.toUpperCase()+'"/>';
								var languagetext = webtools.languagecodes[subtitle.languageCode.toLowerCase()];
								if (webtools.languagecodes[subtitle.languageCode.toLowerCase()].length > 8) {
									languagetext = webtools.languagecodes[subtitle.languageCode.toLowerCase()].substr(0, 6) + '...';
								}
								language = '<span data-toggle="tooltip" title="' + webtools.languagecodes[subtitle.languageCode.toLowerCase()] + '">' + languagetext + '</span>';
							} else {
								language = subtitle.languageCode.toLowerCase();
							}
						}

						if (subtitle.selected != null) {
							selectedsubtitle = ' class="bg-success"';
						}

						// Options filtering
						//if (subtitlemgmt.options.options_only_multiple) {
						//	display_subtitle = false;
						//	discoveredlanguages.forEach(function(language) {
						//		if ((language[0] == subtitle.languageCode) && (language[1] > 1)) {
						//			display_subtitle = true;
						//		}
						//	});
						//}

						if ((subtitlemgmt.options.options_hide_integrated) && (subtitle.location == 'Embedded')) {
							display_subtitle = false;
						}

						if ((subtitlemgmt.options.options_hide_local) && (subtitle.location == 'Sidecar')) {
							display_subtitle = false;
						}
						// End of options filtering
						if (display_subtitle) {
							//anysubtitleadded = true;
							var view = '';
							var checkbox = '';
							if ( (subtitle.location == 'Sidecar') || (subtitle.location == 'Agent') ) {
								checkbox = '<input type="checkbox" name="subtitle-' + mediakey + '" value="' + mediakey + ',' + subtitle.key + '">';
								view = '<button class="btn btn-default btn-xs" onclick=\'subtitlemgmt.view_subtitle(' + mediakey + ',' + subtitle.key + ')\'>View</button>';
							}
							counter++;
							subtitlecontent.push('<tr' + selectedsubtitle + '><td class="td-small">' + checkbox + '</td><td class="td-small">' + language + '</td><td>' + subtitle.location + '</td><td>' + subtitle.codec + '</td><td>' + view + '</td></tr>');
						}
		
					});
					
					$('.subtitletable',context).html(subtitlecontent.join('\n'));
					$('#showsubtitle_' + mediakey ).html('Found ' + counter + ' subtitles, click here to view the list.');
				},
				error: function(data) {
					$('.subtitletable',context).html('<tr><td>Unable to fetch subtitledata</td></tr>');
				}
			})
}

subtitlemgmt.showsubtitletable = function (context) {
	// Currently unused
	//console.log($(context).parent().html());
	//console.log($(context).parent().html());
	if ( $('.subtitletable',$(context).parent()).is( ":hidden" ) ) {
    $('.subtitletable',$(context).parent()).slideDown(1000);
  } else {
    $('.subtitletable',$(context).parent()).hide();
  }
}

subtitlemgmt.view_subtitle = function(mediaKey, subtitleKey) {
	webtools.loading();
	$.ajax({
		url: '/webtools2?module=pms&function=showSubtitle&key=' + subtitleKey,
		cache: false,
		type: 'GET',
		dataType: 'JSON',
		success: function(data) {
			var subtitle = '<table class="table table-bordered table-condensed">';
			subtitle += '<tr><th>Row#</th><th>Line</th></tr>';
			for (i = 0; i < data.length; i++) {
				subtitle += '<tr><td class="bg-warning smallfont">#' + (i + 1) + '</td><td class="smallfont">' + data[i] + '</td></tr>';
			}
			subtitle += '</table>';

			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Viewing Subtitle');
			$('#myModalBody').html(subtitle);
			$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed fetching the section contents from the server.', data);
		}
	});
}

var getSubs = function (key, callback) {
    $.ajax({
        url: '/webtools2?module=pms&function=getSubtitles&key=' + key + '&getFile=false',
        cache: false,
        dataType: 'JSON',
        success: function (data) {
            callback({ subs: data, key: key });
        },
        error: function(data) {
            data.url = this.url;
            webtools.display_error('Failed getting subs.', data);
        }
    });
    
}

subtitlemgmt.search_shows = function () {
    $.ajax({
        url: '/webtools2?module=pms&function=search&title=' + $("#searchvalue").val(),
        cache: false,
        dataType: 'JSON',
        success: function (data) {
            subtitlemgmt.selected_section.contents = [];
            subtitlemgmt.selected_section.contentstype = 'video';

            //Quick solution before release of v3 - Will become much much better with v3
            var counter = 0;
            var asyncCounter = 0;
            for (var key in data) {
                var obj = data[key];
                if (obj.type !== "movie") {
                    asyncCounter++;
                    continue;
                }

                counter++;
                getSubs(key, function (data2) {
                    asyncCounter++;

                    data[data2.key].subtitles = data2.subs;
                    data[data2.key].subtitles.showsubs = true;
                    subtitlemgmt.selected_section.contents.push(data[data2.key]);

                    var size = Object.keys(data).length;
                    if (asyncCounter === size) {
                        subtitlemgmt.display_episodes();
                    }
                });

                if (counter === 15) break;
            }

        },
        error: function(data) {
            data.url = this.url;
            webtools.display_error('Failed searching.', data);
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
					//console.log(response);
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').prop('disabled', true);
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').prop('checked', false);
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').parent().parent().addClass('bg-danger');
					$('input[value="' + splitstring[0] + ',' + splitstring[1] + '"]').parent().parent().fadeOut(2000);
					if(typeof(response.FilePath) == 'undefined') {
						webtools.log("Deleted File: " + response['Deleted file']);
						callback("Deleted File: " + response['Deleted file'], subtitlearray);
					} else {
						webtools.log("Deleted File: " + response.FilePath);
						callback("Deleted File: " + response.FilePath, subtitlearray);
					}
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