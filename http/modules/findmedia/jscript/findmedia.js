webtools.functions.findmedia = {
	start: function() {},
  hasoptions: true,
	loading:  new asynchelper(true, false),
	options: {},
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
				webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
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
				webtools.display_error('Failed fetching the sections from the server. Please restart the server.', data);
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

findmedia.show_options = function() {

	// Define the default view of options for SubtitleMGMT.
	$('#myModalLabel').html('Preferences');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button> <button type="button" class="btn btn-default" onclick="webtools.save_options();">Save Options</button>');


	$('#OptionsModalAlert').hide();
	var options = [
		'<tr><td><input type="checkbox" name="options_ignore_hidden"></td><td>Ignore hidden</td></tr>',
		'<tr><td><input type="checkbox" name="options_ignored_dirs"></td><td>Ignored directories:</td></tr>',
		'<tr><td><input type="checkbox" name="options_valid_extensions"></td><td>Valid Extensions:</td></tr>',
		'<tr><td><input type="text" name="items_per_page" size="2"></td><td>Items per page <span id="items_per_page_max_min"></span></td></tr>'
	]

	$('#OptionsTable').html(options.join('<br>'));

	$('#myModal').modal('show');
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
				webtools.display_error('Failed starting the scanning. Please restart the server.', data);
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
				webtools.display_error('Failed fetching the status from the server. Please restart the server.', data);
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
				webtools.display_error('Failed fetching the results from the server. Please restart the server.', data);
				findmedia.loading.abort('Error: ' + data.statusText);
			}

		});
}