/*
 Created by Mikael Aspehed (Dagalufh)
 Not yet migrated to APIv2
*/

// Stores values generic to Webtools. Function declerations are done further down in the script.
var webtools = {
	modules: [
		['subtitlemgmt', 'Subtitle Management'],
		['logviewer', 'LogViewer/Downloader Tool'],
		['install', 'Unsupported AppStore']
	],
	active_module: '',
	functions: {},
	version: 0,
	list_modules: new asynchelper(true, false),
	activate_module: function() {},
	display_error: function() {},
	defaultoptionsmenu: '',
	save_options: function() {},
	listlogfiles: function() {},
	log: function() {},
	show_log: function() {},
	changepassword_display: function() {},
	changepassword_work: function() {},
	updates_check: function() {},
	updates_check_display: function() {},
	longermodulestart: false,
	loading: function() {},
	changelog: '',
	credits: ''
};

// Webtools function

webtools.list_modules.inline([
		function(callback, activatemodulename) {
			//Name:VersionFetch
			webtools.loading();
			$('#OptionsMenu').html('');
			$.ajax({
				url: '/version',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					webtools.version = data.version;
					$('#MainLink').html('Webtools - v' + data.version);
					if (data.PlexTVOnline === false) {
						$('#OptionsMenu').append('<li><a class="customlink" onclick="webtools.changepassword_display();" >Change Password</a></li>');
					}
					$('#OptionsMenu').append('<li><a class="customlink" onclick="webtools.updates_check_display();" >Check for Webtools Updates</a></li>');
					webtools.defaultoptionsmenu = $('#OptionsMenu').html();
					callback('VersionFetch:Success', activatemodulename);
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the version from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
					webtools.list_modules.abort('Error: ' + data.statusText);
				}
			});
		},
		function(callback, activatemodulename) {
			webtools.listlogfiles(callback, activatemodulename);
		},
		function(callback, activatemodulename) {
			$.ajax({
				url: '/changelog.txt',
				cache: false,
				dataType: 'text',
				success: function(data) {
					var changelog = data.split('\n');

					for (var i = 0; i < changelog.length; i++) {
						if (changelog[i] == '####') {
							break;
						}
						changelog[i] = changelog[i].replace('\t', '<span style="padding-left:2em"></span>');
						if (changelog[i][changelog[i].length - 1] == ':') {
							changelog[i] = '<b>' + changelog[i] + '</b>';
						}

						webtools.changelog += changelog[i] + "<br>";
					}
					callback();
				},
				error: function(data) {
					callback();
				}
			});
		},
		function(callback, activatemodulename) {
			$.ajax({
				url: '/credits.txt',
				cache: false,
				dataType: 'text',
				success: function(data) {
					var credits = data.split('\n');
					for (var i = 0; i < credits.length; i++) {
						credits[i] = credits[i].replace('\t', '<span style="padding-left:2em"></span>');
						if (credits[i][credits[i].length - 1] == ':') {
							credits[i] = '<b>' + credits[i] + '</b>';
						}

						webtools.credits += credits[i] + "<br>";
					}
					callback();
				},
				error: function(data) {
					callback();
				}
			});
		}
	],
	function(result, activatemodulename) {
		//console.log(typeof(activatemodulename));
		if (typeof(activatemodulename) == 'undefined') {

			var contents = [
				'Webtools is a tool that enables the use of modules to help you with your Plex Server management.<br>',
				'<b>Available Modules</b>'
			];
			webtools.modules.forEach(function(modulename) {
				contents.push('<a class="customlink" onclick="webtools.activate_module(\'' + modulename[0] + '\')">' + modulename[1] + '</a>');
			});
			contents.push('<br><div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Latest changelog</h4></div><div class="panel-body">' + webtools.changelog + '</div></div>');
			contents.push('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Credits</h4></div><div class="panel-body">' + webtools.credits + '</div></div>');
			$('#ContentBody').html(contents.join('<br>'));
			$('.modal').modal('hide');
		} else {
			webtools.activate_module(activatemodulename);
		}
	});

// This module sets the active module and launches it's start function.
webtools.activate_module = function(modulename) {
	webtools.loading();
	webtools.longermodulestart = false;
	$('#navfoot').html('');
	$('#ContentFoot').html('');
	$('#OptionsMenu').html(webtools.defaultoptionsmenu);

	$.ajax({
		url: 'modules/' + modulename + '/jscript/' + modulename + '.js',
		cache: false,
		dataType: 'script',
		global: false,
		success: function() {
			webtools.active_module = modulename;
			webtools.functions[modulename].start();
			if (webtools.functions[modulename].hasoptions === true) {
				$("#OptionsMenu").append('<li><a class="customlink" onclick="javascript:webtools.functions[\'' + modulename + '\'].show_options();" >Preferences</a></li>');
			}

			if ($('#OptionsMenu li').length === 0) {
				$('#OptionsMainLi').html('');
			}

			var moduledisplayname = '';
			webtools.modules.forEach(function(modulename_find) {
				if (modulename_find[0] == modulename) {
					moduledisplayname = modulename_find[1];
				}
			});

			$("#SubLink").attr('onclick', 'javascript:webtools.activate_module(\'' + modulename + '\')');
			$("#SubLink").html('/' + moduledisplayname);

			$('#ModuleCSS').attr('href', 'modules/' + modulename + '/css/' + modulename + '.css');
			if (webtools.longermodulestart === false) {
				$('.modal').modal('hide');
			}
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed activating the module. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
		}
	});
};

// The only purpose of this is to display a modal with an error message.
webtools.display_error = function(message, ajaxobject) {
	$('#myModalLabel').html('An error occured.');

	if (typeof(ajaxobject) != 'undefined') {
		message += '<hr>Errorinfo:' + '<br>Requested URL: ' + ajaxobject.url + '<br>Error Code/Message: ' + ajaxobject.status + '/' + ajaxobject.statusText;
	}

	$('#myModalBody').html(message);
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');

	if ($('#myModal').is(':visible') === false) {
		$('#myModal').modal({
			keyboard: false,
			backdrop: 'static'
		});
		$('#myModal').modal('show');
	}
};

webtools.save_options = function() {
	webtools.functions[webtools.active_module].save_options();
};

webtools.listlogfiles = function(callback, activatemodulename) {

	webtools.loading();
	//Name:LogfileNamesFetch
	$("#LogfilesMenu").html('');
	$.ajax({
		url: '/webtools2',
		data: {
			'module': 'logs',
			'function': 'list',
			'filter': 'WebTools'
		},
		cache: false,
		dataType: 'JSON',
		success: function(data) {
			data.forEach(function(logfilename) {
				$('#LogfilesMenu').append('<li><a class="customlink" onclick="javascript:webtools.show_log(\'' + logfilename + '\')">' + logfilename + '</a></li>');
			});

			$('#LogfilesMenu').append('<li><a class="customlink" href="/webtools2?module=logs&function=download">Download all logfiles as Zip</a></li>');
			$('#LogfilesMenu').append('<li><a class="customlink" onclick="javascript:webtools.listlogfiles();">Refresh Logfilelist</a></li>');
			if (typeof(callback) != 'undefined') {
				callback('LogfileNamesFetch:Success', activatemodulename);
			} else {
				$('.modal').modal('hide');
			}

		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed fetching the logfilenames from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);

			if (typeof(callback) != 'undefined') {
				webtools.list_modules.abort('Error: ' + data.statusText);
			}
		},

	});
};

webtools.log = function(LogEntry, Source) {
	if (typeof(Source) == 'undefined') {
		Source = webtools.active_module;
	}

	$.ajax({
		url: '/webtools2?module=logs&function=entry&text=[' + Source + '] ' + encodeURIComponent(LogEntry),
		type: 'POST',
		global: false,
		cache: false,
		dataType: 'text',
		success: function(data) {},
		error: function(data) {}
	});
};

webtools.show_log = function(filename) {
	webtools.loading();
	$('#ContentHeader').html('Logfile: ' + filename);
	$('#ContentBody').html('Fetching Logfile..');
	$('#ContentFoot').html('');
	$('#navfoot').html('');

	$.ajax({
		url: '/webtools2',
		data: {
			'module': 'logs',
			'function': 'show',
			'fileName': filename
		},
		type: 'GET',
		cache: false,
		dataType: 'JSON',
		success: function(logs) {
			//$('#ContentBody').html(logs.join('<br>'));  
			var logtable = '<table class="table table-bordered smallfont">';
			logtable += '<tr><th class="td-small">Row#</th><th>Logentry</th></tr>';
			if (logs.length > 0) {
				for (var i = 0; i < logs.length; i++) {

					var tdnumber = 'bg-warning';
					var tdtext = '';

					if (logs[i].toLowerCase().indexOf('critical') != -1) {
						tdnumber = 'bg-danger';
						tdtext = 'bg-danger';
					}
					if (logs[i].toLowerCase().indexOf('error') != -1) {
						tdnumber = 'bg-info';
						tdtext = 'bg-info';
					}

					logtable += '<tr><td class="' + tdnumber + '">#' + (i + 1) + '</td><td class="' + tdtext + '">' + logs[i] + '</td></tr>';
				}
			} else {
				logtable += '<tr><td class="bg-warning">#-</td><td>Empty file</td></tr>';
			}
			logtable += '</table>';

			$('#ContentBody').html(logtable);
			$('#ContentFoot').html('<a href="/webtools2?module=logs&function=download&fileName=' + filename + '">Download Logfile</a>');
			$('.modal').modal('hide');
		},
		error: function(logs) {
			$('#ContentBody').html(logs);
			$('.modal').modal('hide');
		}
	});



};

// Debug every AJAX calls hit.
$(document).ajaxComplete(function(event, request, settings) {
	webtools.log("Completed AJAX Call for URL: " + settings.url, 'Core');
});

webtools.changepassword_display = function() {
	$("input[name=newpassword]").val('');
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Change Password');
	$('#myModalBody').html('<table class="table table-condensed">' +
		'<tr><td>Old Password:</td><td><input type="password" name="oldpassword"></td></tr>' +
		'<tr><td>New Password:</td><td><input type="password" name="newpassword"></td></tr>' +
		'<tr><td>Repeat Password:</td><td><input type="password" name="repeatpassword"></td></tr>' +
		'</table>' +
		'<p id="newpassword_error"></p>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.changepassword_work();">Save</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	$('#myModal').modal('show');
};

webtools.changepassword_work = function() {
	if ($("input[name=newpassword]").val().length === 0) {
		$('#newpassword_error').html('Password can\'t be empty.');
		$("input[name=newpassword]").addClass('bg-danger');
	} else if ($("input[name=newpassword]").val() != $("input[name=repeatpassword]").val()) {
		$('#newpassword_error').html('The new passwords didn\'t match.');
		$("input[name=newpassword]").addClass('bg-danger');
		$("input[name=repeatpassword]").addClass('bg-danger');
	} else {
		$("input[name=newpassword]").removeClass('bg-danger');
		$("input[name=oldpassword]").removeClass('bg-danger');
		$("input[name=repeatpassword]").removeClass('bg-danger');
		$('#newpassword_error').html('');
		$.ajax({
			url: '/webtools2',
			data: {
				'module': 'settings',
				'function': 'setPwd',
				'oldPwd': $("input[name=oldpassword]").val(),
				'newPwd': $("input[name=newpassword]").val()
			},
			type: 'POST',
			dataType: 'text',
			cache: false,
			success: function(data) {
				$('#myModalBody').html('Password has been changed.');
				$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
			},
			error: function(data) {
				if (data.statusCode().status == 401) {
					$('#newpassword_error').html('Old password incorrect.');
					$("input[name=oldpassword]").addClass('bg-danger');
				} else {
					$('#myModalBody').html('An error occured and the password has not been changed.');
					$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
				}
			}
		});
	}
};

webtools.updates_check_display = function() {
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Check For Updates');
	$('#myModalBody').html('<p id="updateinfo">No update information fetched yet.</p>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.updates_check();">Check</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	$('#myModal').modal('show');
};

webtools.updates_check = function() {
	$('#updateinfo').html('Please wait while fetching information from Github.');
	$.ajax({
		url: '/webtools2',
		data: {
			'module': 'git',
			'function': 'getReleaseInfo',
			'url': 'https://github.com/dagalufh/WebTools.bundle',
			'version': 'latest'
		},
		type: 'GET',
		datatype: 'JSON',
		cache: false,
		success: function(data) {
			data = JSON.parse(data);
			infoarray = [];

			if (typeof(data.published_at) == 'undefined') {
				infoarray.push('No releases available.');
			} else {
				infoarray.push('Currently Installed Version: ' + webtools.version);
				infoarray.push('Latest Update: ' + data.published_at);
				infoarray.push('Version Name: ' + data.name);
				infoarray.push('Author: <a target="_NEW" href="' + data.author.html_url + '">' + data.author.login + '</a>');
				infoarray.push('Release Notes: ' + data.body);
				infoarray.push('Download url: <a target="_NEW" href="' + data.zipball_url + '">' + data.zipball_url + '</a>');
				//console.log('version compare: ' + compare(webtools.version, data.name.substring(1)) + ' A: ' + webtools.version + '> B: ' + data.tag_name);

				switch (compare(webtools.version, data.tag_name)) {
					case 0:
						infoarray.push('You are on the latest and greatest!');
						break;
					case -1:
						infoarray.push('You\'ve fallen behind. Time to update to the greatest!');
						break;
					case 1:
						infoarray.push('You are ahead of time. Your version is newer than the one on Github.');
						break;
				}
			}
			$('#updateinfo').html(infoarray.join('<br>'));
		},
		error: function() {
			$('#updateinfo').html('An error occured while trying to fetch information from Github. Try again in a little while.');
		}
	});
};

$(function(ready) {
	$('#myModal').on('hidden.bs.modal', function(e) {
		console.log('myModal Hidden');
	})
})

webtools.loading = function(CustomMessage) {
	console.log('myModal Requested');
	$('#myModalLabel').html('Loading');
	if (typeof(CustomMessage) == 'undefined') {
		$('#myModalBody').html('Loading, please wait.');
	} else {
		$('#myModalBody').html(CustomMessage);
	}
	$('#myModalFoot').html('');

	if ($('#myModal').is(':visible') === false) {
		$('#myModal').modal({
			keyboard: false,
			backdrop: 'static'
		});
		console.log('myModal, to be shown NOW');
		$('#myModal').modal('show');
	}
}

// This function is created by http://stackoverflow.com/users/148423/joe
function compare(a, b) {
	if (a === b) {
		return 0;
	}

	var a_components = a.split(".");
	var b_components = b.split(".");

	var len = Math.min(a_components.length, b_components.length);

	// loop while the components are equal
	for (var i = 0; i < len; i++) {
		// A bigger than B
		if (parseInt(a_components[i]) > parseInt(b_components[i])) {
			return 1;
		}

		// B bigger than A
		if (parseInt(a_components[i]) < parseInt(b_components[i])) {
			return -1;
		}
	}

	// If one's a prefix of the other, the longer one is greater.
	if (a_components.length > b_components.length) {
		return 1;
	}

	if (a_components.length < b_components.length) {
		return -1;
	}

	// Otherwise they are the same.
	return 0;
}

webtools.dynamicSort = function(property) {
	var sortOrder = 1;
	if (property[0] === "-") {
		sortOrder = -1;
		property = property.substr(1);
	}
	return function(a, b) {
		var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
		return result * sortOrder;
	}
}