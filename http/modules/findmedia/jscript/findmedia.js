webtools.functions.findmedia = {
	start: function() {},
  hasoptions: true,
	loading:  new asynchelper(true, false),
	options: {},
	resetSettings: function() {},
	save_options: function() {},
	show_options: function() {},
	sections: [],
	scanning_start: function() {},
	scanning_wait: function() {},
	scanning_present_result: function() {}
}
var findmedia = webtools.functions.findmedia;

findmedia.start = function() {
	webtools.loading();
	webtools.longermodulestart = true;
	findmedia.loading.start();
}

findmedia.loading.inline([
		function(callback) { 
			$.ajax({
			///webtools2?module=settings&function=getSettings
			url: '/webtools2?module=findMedia&function=getSettings',
			cache: false,
			dataType: 'JSON',
			success: function(data) {
				console.log(data);
				findmedia.options = data;
				callback();
			},
			error: function(data) {
				console.log('error:' + data);
				data.url = this.url;
				findmedia.loading.abort();
				webtools.display_error('Failed fetching the settings from the server.', data);
			}
		});
	},
		function (callback) {
		$.ajax({
			url: '/webtools2',
			data: {
				'module': 'pms',
				'function': 'getSectionsList'
			},
			cache: false,
			dataType: 'JSON',
			success: function(data) {
				data.forEach(function(currentsection) {         
					findmedia.sections.push(currentsection);
				});
				callback('SectionFetch:Success');
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed fetching the sections from the server. ', data);
				findmedia.loading.abort('Error: ' + data.statusText);
			}

		});
	}
	], function () {
		$('#ContentHeader').html('Welcome to FindMedia');

		var body = ['This tool is a combination of FindUnmatched and FindMissing.','Select one of the libraries below to scan for videos/shows that are not in the Plex database or is not on your harddrive.'];

		findmedia.sections.forEach(function (section) {
			if( (section.type == "movie") || (section.type == "show") ){
				body.push('<button class="btn btn-default btn-xs div-medium" onclick="findmedia.scanning_start('+section.key+')"><img class="sectionicon" src="icons/plex_'+section.type+'.png">&nbsp;'+section.title+'</button>');
			}
		})
		body.push('');
		$('#ContentBody').html(body.join('<br>'));
		$('#ContentFoot').html('');
		$('#navfoot').html('');
		$('.modal').modal('hide');	
	});

findmedia.resetSettings = function() {
	$('#myModalLabel').html('Resetting settings');
	$('#myModalBody').html('Resetting settings...');
	$('#myModalFoot').html('');

	$.ajax({
						url: '/webtools2?module=findMedia&function=resetSettings',
						cache: false,
						type: 'POST',
						dataType: 'text',
						success: function(data) {
							$('#myModalBody').html('Settings has been reset.');
							webtools.log('Options reset successfully.');
							$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
						},
						error: function(data) {
							$('#myModalBody').html('Failed resetting settings.');
							webtools.log('Settings has not been reset due to an error.');
							$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
						}
					});	
}

findmedia.show_options = function() {
	// Define the default view of options for SubtitleMGMT.
	$('#myModalLabel').html('Preferences');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button> <button type="button" class="btn btn-default" onclick="webtools.save_options();">Save Options</button>');


	$('#OptionsModalAlert').hide();
	
	var ignored_dirs_string = '';
	findmedia.options.IGNORED_DIRS.forEach( function (ignored_dir) {
		if (ignored_dir.length > 0) {
			ignored_dirs_string += ignored_dir + ',';
		}
	});
	ignored_dirs_string = ignored_dirs_string.substring(0,ignored_dirs_string.length-1);
	
	var valid_extensions_string = '';
	findmedia.options.VALID_EXTENSIONS.forEach( function (extensions) {
		if (extensions.length > 0) {
			valid_extensions_string += extensions + ',';
		}
	});
	valid_extensions_string = valid_extensions_string.substring(0,valid_extensions_string.length-1);
	
	var ignore_hidden_checked = '';
	if (findmedia.options.IGNORE_HIDDEN === true) {
		ignore_hidden_checked = 'checked=' + findmedia.options.IGNORE_HIDDEN;
	}
	
	var options = [
		'<tr><td colspan="2">Seperate values with , (comma).</td></tr>',	
		'<tr><td>Ignore Hidden:</td><td><input type="checkbox" name="options_ignore_hidden" ' + ignore_hidden_checked + '></td></tr>',
		'<tr><td>Ignored Directories:</td><td><input type="text" name="options_ignored_dirs" value="' + ignored_dirs_string + '"></td></tr>',
		'<tr><td>Valid Extensions:</td><td><input type="text" name="options_valid_extensions" value="' + valid_extensions_string + '"></td></tr>',
		'<tr><td colspan="2"><button type="button" class="btn btn-default" onclick="findmedia.resetSettings();">Reset settings to default</button></td></tr>'
	]

	$('#OptionsTable').html(options.join('<br>'));

	$('#myModal').modal('show');
}

findmedia.save_options = function() {
	console.log($("input[name=options_ignore_hidden]").prop('checked'));
	findmedia.options.IGNORE_HIDDEN = $("input[name=options_ignore_hidden]").prop('checked');
	//if ($("input[name=options_ignore_hidden]").val() == 'on') {
	//	findmedia.options.IGNORE_HIDDEN = true;
	//}
	
	
	
	
	var ignored_dirs = $("input[name=options_ignored_dirs]").val().split(',');
	findmedia.options.IGNORED_DIRS = [''];
	ignored_dirs.forEach(function (dir) {
		if(dir.length > 0) {
			findmedia.options.IGNORED_DIRS.push(dir);
		}
	}) 

	var valid_extensions = $("input[name=options_valid_extensions]").val().split(',');
	findmedia.options.VALID_EXTENSIONS = [''];
	valid_extensions.forEach(function (dir) {
		if(dir.length > 0) {
			findmedia.options.VALID_EXTENSIONS.push(dir);
		}
	})
	
	var save_options_to_server = new asynchelper(false, true);
	save_options_to_server.inline([
		function(callback) {
			var optionkeys = [];
			for (var key in findmedia.options) {
				optionkeys.push(key);
				save_options_to_server.functionsarray.push(function(callback, optionkeys) {
					var currentkey = optionkeys.shift();
					$.ajax({
						url: '/webtools2?module=findMedia&function=setSetting',
						cache: false,
						type: 'POST',
						data: {key: currentkey, value: findmedia.options[currentkey].toString()},
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

findmedia.scanning_start = function(sectionKey) {
	webtools.loading('Starting scan of section.');
	
	$.ajax({
			url: '/webtools2?module=findMedia&function=scanSection&section=' + sectionKey,
			cache: false,
			type: 'GET',
			success: function(data) {
				findmedia.scanning_wait()
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed starting the scanning. ', data);
				findmedia.loading.abort('Error: ' + data.statusText);
			}

		});

}

findmedia.scanning_wait = function() {
	$.ajax({
			url: '/webtools2?module=findMedia&function=getStatus',
			cache: false,
			type: 'GET',
			dataType: 'text',
			success: function(data) {
				console.log(data);
				if(data == 'Idle') {
					findmedia.scanning_present_result();
				} else {
					webtools.loading(data);
					setTimeout(findmedia.scanning_wait,2000);
				}
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed fetching the status from the server.', data);
				findmedia.loading.abort('Error: ' + data.statusText);
			}

		});
}

findmedia.scanning_present_result = function() {
		$.ajax({
			url: '/webtools2?module=findMedia&function=getResult',
			cache: false,
			type: 'GET',
			dataType: 'JSON',
			success: function(data) {
				console.log(data);
				
				var MissingFromDB = [];
				var MissingFromFS = [];
				
				var body = ['<table class="table table-condensed">',
										'<tr><th>Missing From Plex DB</th></tr>',
										'{MissingFromDB}',
									 '</table>',
										'<br>',
										'<table class="table table-condensed">',
										'<tr><th>Missing From Filesystem</th></tr>',
										'{MissingFromFS}',
									 '</table>'
									 ];
				
				body = body.join('\n');
				
				
				if(data.MissingFromDB.length > 0) {
					data.MissingFromDB.forEach(function(item) {
						MissingFromDB.push('<tr><td>' + item + '</td></tr>');
					})
				} else {
					MissingFromDB = ['<tr><td>','Nothing Missing','</td></tr>'];
				}
				
				if(data.MissingFromFS.length > 0) {
					data.MissingFromFS.forEach(function(item) {
						MissingFromFS.push('<tr><td>' + item + '</td></tr>');
					})
				} else {
					MissingFromFS = ['<tr><td>','Nothing Missing','</td></tr>'];
				}

				MissingFromDB = MissingFromDB.join('\n');
				MissingFromFS = MissingFromFS.join('\n');
				
				body = body.replace('{MissingFromDB}',MissingFromDB);
				body = body.replace('{MissingFromFS}',MissingFromFS);
				
				$('#ContentBody').html(body);
				
				$('.modal').modal('hide');
			},
			error: function(data) {
				data.url = this.url;
				webtools.display_error('Failed fetching the results from the server.', data);
				findmedia.loading.abort('Error: ' + data.statusText);
			}

		});
}