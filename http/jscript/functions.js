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
		,['findmedia','FindMedia']
	],
	stylesheets: [],
	active_stylesheet: '',
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
	credits: '',
	install_WT: function() {},
	wait_update: function () {},
	languagecodes: {},
	// Search a table that has the tr with an id tag unique for each row
	keywordarray: [],
	currentkeyword: 0,
  searchkeyword: function () {},
	next: function () {},
	previous: function () {},
	clearresult: function () {},
	change_theme_display: function () {},
	change_theme_work: function() {},
	wait_restart: function () {},
	factory_reset_display: function() {},
	factory_reset_work: function() {}
};

// Webtools function

webtools.list_modules.inline([
		function(callback, activatemodulename) {
			//Name:VersionFetch
			webtools.loading();
			$('#OptionsMenu').html('');
			$('#ModuleMenu').html('');
			$.ajax({
				url: '/version',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					webtools.version = data.version;
					$('#MainLink').html('WebTools - v' + data.version);
					if (data.PlexTVOnline === false) {
						$('#OptionsMenu').append('<li><a class="customlink" onclick="webtools.changepassword_display();" >Change Password</a></li>');
					}
					$('#OptionsMenu').append('<li><a class="customlink" onclick="webtools.updates_check_display();" >Check for Webtools Updates</a></li>');
					$('#OptionsMenu').append('<li><a class="customlink" onclick="webtools.change_theme_display();" >Change Theme</a></li>');
					$('#OptionsMenu').append('<li><a class="customlink" onclick="javascript:webtools.show_log(\'changelog\')">View Changelog</a></li>');
					$('#OptionsMenu').append('<li><a class="customlink" onclick="javascript:webtools.factory_reset_display()">Factory Reset</a></li>');
					
					webtools.defaultoptionsmenu = $('#OptionsMenu').html();
					callback('VersionFetch:Success', activatemodulename);
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the version from the server.', data);
					webtools.list_modules.abort('Error: ' + data.statusText);
				}
			});
		},
		function (callback, activatemodulename) {
			
			$.ajax({
			///webtools2?module=settings&function=getSettings
			url: '/webtools2?module=wt&function=getCSS',
			cache: false,
			dataType: 'JSON',
			success: function (data, textStatus, xhr) {
				if (xhr.status == 200) {
					webtools.stylesheets = data;
				} else {
					webtools.stylesheets = [];
				}
				
				callback('SettingsFetch:Success');
			},
			error: function(data) {
				webtools.active_stylesheet = 'default.css';
				webtools.log('No custom CSSTheme setting found.','Core');
				callback('SettingsFetch:Success');
			}
		});
		
		//	callback('StylesheetSettings:Success', activatemodulename);
		},
		function (callback, activatemodulename) {
			
			$.ajax({
			///webtools2?module=settings&function=getSettings
			url: '/webtools2?module=settings&function=getSetting&name=wt_csstheme',
			cache: false,
			dataType: 'JSON',
			success: function(data) {
				webtools.active_stylesheet = data;
				if (data !== 'default.css') {
					webtools.log('Found custom CSSTheme file setting (custom_themes/' + data + '). Loading it.','Core');
					$('head').append('<link id="custom_theme_stylesheet" rel="stylesheet" href="custom_themes/' + data + '" type="text/css" />');
				}
				
				callback('SettingsFetch:Success');
			},
			error: function(data) {
				webtools.active_stylesheet = 'default.css';
				webtools.log('No custom CSSTheme setting found.','Core');
				callback('SettingsFetch:Success');
			}
		});
		
		//	callback('StylesheetSettings:Success', activatemodulename);
		},
		function(callback, activatemodulename) {
			//Name:VersionFetch
			webtools.loading();
			$.ajax({
				url: '/webtools2?module=language&function=get3CodeLangList',
				cache: false,
				dataType: 'JSON',
				success: function(data) {
					webtools.languagecodes = data;
					//console.log(webtools.languagecodes);
					callback('LanguageCodes:Success', activatemodulename);
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the languagecodes from the server.', data);
					webtools.list_modules.abort('Error: ' + data.statusText);
				}
			});
		},
		function(callback, activatemodulename) {
			callback('LogfileNamesFetch:Ignored', activatemodulename);
			//webtools.listlogfiles(callback, activatemodulename);
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
			$('#SublinkMainTitle').html('Choose Module');
			webtools.modules.forEach(function(modulename) {
				contents.push('<button class="btn btn-default btn-xs div-medium" class="customlink" onclick="webtools.activate_module(\'' + modulename[0] + '\')">' + modulename[1] + '</button>');
				$('#SublinkMenu').append('<li><a class="customlink" onclick="javascript:webtools.activate_module(\'' + modulename[0] + '\')">' + modulename[1] + '</a></li>');
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
	$('#ModuleMenu').html('');
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

			//$("#SubLink").attr('onclick', 'javascript:webtools.activate_module(\'' + modulename + '\')');
			//$("#SubLink").html('/' + moduledisplayname);
			
			$('#SublinkMainTitle').html(moduledisplayname);
			$('#SublinkMenu').html('<li><a class="customlink" onclick="javascript:webtools.activate_module(\'' + modulename + '\')" >Reload ' + moduledisplayname + '</a></li>');
			webtools.modules.forEach(function(modulename) {
				if (modulename[1] != moduledisplayname) {
					$('#SublinkMenu').append('<li><a class="customlink" onclick="javascript:webtools.activate_module(\'' + modulename[0] + '\')">' + modulename[1] + '</a></li>');
				}
			});

			$('#ModuleCSS').attr('href', 'modules/' + modulename + '/css/' + modulename + '.css');
			if (webtools.longermodulestart === false) {
				$('.modal').modal('hide');
			}
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed activating the module.', data);
		}
	});
};

// The only purpose of this is to display a modal with an error message.
webtools.display_error = function(message, ajaxobject) {
    $('#myModalLabel').html('An error occured.');
    
    message += '<br /><br />Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex thread <a href="https://forums.plex.tv/discussion/126254" target="_blank" style="font-weight: bold;">here</a> if it occurs again. ';
    message += '<br /><br />You can download the log files <a onclick="window.open(\'webtools2?module=logs&function=download\',\'_blank\');" target="_blank" style="font-weight: bold;cursor:pointer;">here</a>';

	if (typeof (ajaxobject) != 'undefined') {
	    message += '<br /><br />';
	    message += '<hr>Technical details:<br /><br>Requested URL: ' + ajaxobject.url + '<br>Error Code/Message: ' + ajaxobject.status + '/' + ajaxobject.statusText;
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
 // Currently unused
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
			webtools.display_error('Failed fetching the logfilenames from the server.', data);

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
	if (Source.length === 0) {
		Source = 'Core';
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
	$('#ContentBody').html('Fetching Logfile..');
	$('#ContentFoot').html('');
	$('#navfoot').html('');
	if (filename == 'changelog') {
		$('#ContentHeader').html('Viewing Changelog');
		$.ajax({
			url: '/changelog.txt',
			cache: false,
			dataType: 'text',
			success: function(logs) {
				logs = logs.split('\n');
				//$('#ContentBody').html(logs.join('<br>'));  
				var logtable = '<table class="table table-bordered smallfont" id="logtable">';
				//logtable += '<tr><th>Changelog</th></tr>';
				if (logs.length > 0) {
					for (var i = 0; i < logs.length; i++) {
						if (logs[i].length === 0) {
							logs[i] = '&nbsp;';
						}

						if (logs[i] != '####') {
							logs[i] = logs[i].replace('\t', '<span style="padding-left:2em"></span>');
							if (logs[i].search(/\d\d\d\d[-]\d\d[-]\d\d/) !== -1) {
								//logs[i] = '<b>' + logs[i] + '</b>';
								logtable += '<tr><th>' + logs[i] + '</th></tr>';
							} else if (logs[i][logs[i].length - 1] == ':') {
								logtable += '<tr><td><b>' + logs[i] + '</b></td></tr>';
							} else {
								logtable += '<tr><td>' + logs[i] + '</td></tr>';
							}

						}
					}
				} else {
					logtable += '<tr><td class="bg-warning">#-</td><td>Empty file</td></tr>';
				}
				logtable += '</table>';

				$('#ContentBody').html(logtable);
				$('#ContentFoot').html('');
				$('.modal').modal('hide');
			},
			error: function(logs) {
				$('#ContentBody').html(logs);
				$('.modal').modal('hide');
			}
		});
	} else {
		$('#ContentHeader').html('Logfile: ' + filename);
		$('#navfoot').html('<input type="text" id="webtoolssearchKeyword" onkeydown="if (event.keyCode == 13) { webtools.searchkeyword(\'logtable\'); }"><button class="btn btn-default btn-xs" onclick="webtools.searchkeyword(\'logtable\')">Search keyword</button> <button class="btn btn-default btn-xs" onclick="webtools.previous()" id="webtoolssearchbuttonprevious">Previous</button><button class="btn btn-default btn-xs" onclick="webtools.next()" id="webtoolssearchbuttonnext">Next</button> <button class="btn btn-default btn-xs" onclick="webtools.jumptotop()">Jump to Top</button> <span id="webtoolssearchkeywordresult"></span>');
		webtools.clearresult();
		$.ajax({
			url: '/webtools2&module=logs&function=show&fileName' + filename.replace(/ /g, "%20"),
			type: 'GET',
			cache: false,
			dataType: 'JSON',
			success: function(logs) {
				//$('#ContentBody').html(logs.join('<br>'));  
				var logtable = '<table class="table table-bordered smallfont" id="logtable">';
				logtable += '<tr><th class="td-small">Row#</th><th>Logentry</th></tr>';
				if (logs.length > 0) {
					for (var i = 0; i < logs.length; i++) {

						var tdnumber = 'bg-warning';
						var tdtext = '';

						if (logs[i].toLowerCase().indexOf('critical') != -1) {
							tdnumber = 'bg-danger';
							tdtext = 'bg-danger';
						}
						if (logs[i].toLowerCase().indexOf('exception') != -1) {
							tdnumber = 'bg-danger';
							tdtext = 'bg-danger';
						}
						if (logs[i].toLowerCase().indexOf('error') != -1) {
							tdnumber = 'bg-info';
							tdtext = 'bg-info';
						}

						logtable += '<tr id="'+ (i + 1) +'"><td class="' + tdnumber + '">#' + (i + 1) + '</td><td class="' + tdtext + '">' + logs[i] + '</td></tr>';
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
	}


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

webtools.updates_check = function () {
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
						$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.install_WT();">Re-Install WebTools</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
						break;
					case -1:
						infoarray.push('You\'ve fallen behind. Time to update to the greatest!');
						$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.install_WT();">Update WebTools</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
						break;
					case 1:
						infoarray.push('You are ahead of time. Your version is newer than the one on Github.');
						$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.install_WT();">Re-Install WebTools</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
						break;
				}
			}
			$('#updateinfo').html(infoarray.join('<br>'));
		},
		error: function() {
			$('#updateinfo').html('An error occured while trying to fetch information from Github. Try again in a little while.');
		}
	});
}

webtools.install_WT = function () {
	
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Installing WebTools');
	$('#myModalBody').html('<p id="updateinfo">Installation in progress.</p>');
	$('#myModalFoot').html('');
	$.ajax({
		url: '/webtools2?module=git&function=upgradeWT',
		type:'PUT',
		dataType:'text',
		success: function (data) {
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Waiting for WebTools');
			$('#myModalBody').html('<p id="updateinfo">Waiting for WebTools to come online. Will automatically return you to start when ready.</p>');
			$('#myModalFoot').html('');
			
			console.log('success');
			console.log(data);
			setTimeout(webtools.wait_restart,5000);
			// Call webtools_wait_for_reload();
			// That function is an ajax call for /, if 404, wait for a few seconds, then try again. Otherwise, notify user of updated completed.
		},
		error: function (data) {
			console.log('error');
			console.log(data);
			//webtools.wait_update();
			// Notify user
		}
	})
}

webtools.wait_restart = function () {
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Waiting for WebTools');
	$('#myModalBody').html('<p id="updateinfo">Waiting for WebTools to come online. Will automatically return you to start when ready.</p>');
	$('#myModalFoot').html('');
	$('#myModal').modal('show');
	$.ajax({
		url:'/',
		type: 'GET',
		success: function () {
			window.location.href='/';
		},
		error: function () {
			setTimeout(webtools.wait_restart,1000);
		}
	})
}

$(function(ready) {
	$('#myModal').on('hidden.bs.modal', function(e) {
		//console.log('myModal Hidden');
	})
	
	$(document).on('change','#custom_theme_selectbox',function() {
		

	$('#custom_theme_stylesheet').remove();
		if ( $('#custom_theme_selectbox').val() !== 'default.css') {
			$('head').append('<link id="custom_theme_stylesheet" rel="stylesheet" href="custom_themes/' + $('#custom_theme_selectbox').val() + '" type="text/css" />');
		}
	});
})

webtools.loading = function(CustomMessage) {
	//console.log('myModal Requested');
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
		//console.log('myModal, to be shown NOW');
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
		var result = (a[property].toLowerCase() < b[property].toLowerCase()) ? -1 : (a[property].toLowerCase() > b[property].toLowerCase()) ? 1 : 0;
		return result * sortOrder;
	}
}

//Find in string - Wildcard and insentetive search
function _searchInString(str, value) {
    return new RegExp(value.toLowerCase().trim()).test(str.toLowerCase().trim());
}
webtools.searchBundle = function (bundle, value) {
    value.replace("*", "");
    return $.grep(bundle, function (obj) {
        return _searchInString(obj.title, value) || _searchInString(obj.description, value);
    });
}

webtools.searchkeyword = function(tablename) {
	webtools.keywordarray = [];
	webtools.currentkeyword = 0;
	$('#webtoolssearchkeywordresult').html('');
	
	if ($('#webtoolssearchKeyword').val().length > 0) {
		$('#'+tablename + ' tr').each(function (index,value) {
			var children = $(this).children()
			$(children[1]).removeClass('bg-info');
			$(children[1]).removeClass('keyword');
			if (typeof($(this).context) != 'undefined') {
				if ($(':nth-child(2)', this).html().toLowerCase().indexOf($('#webtoolssearchKeyword').val().toLowerCase()) != -1) {
					$(children[1]).addClass('bg-info');
					$(children[1]).addClass('keyword');
					webtools.keywordarray.push($(this).attr('id'));
				}
			}
		})
		if (webtools.keywordarray.length > 0) {
			$('.bg-primary').addClass('bg-info');
			$('.bg-primary').removeClass('bg-primary');
			var targetrow = $('#' + webtools.keywordarray[webtools.currentkeyword]).children();
			$(targetrow[1]).addClass('bg-primary');
			$(targetrow[1]).removeClass('bg-info');
			
			$('html, body').animate({
				scrollTop: ($('#' + webtools.keywordarray[webtools.currentkeyword]).offset().top - 60)
			});
			
			$('#webtoolssearchbuttonnext').prop('disabled',false);
			$('#webtoolssearchbuttonprevious').prop('disabled',false);
			// Enable Next / Previous buttons
		} else {
			$('#webtoolssearchbuttonnext').prop('disabled',true);
			$('#webtoolssearchbuttonprevious').prop('disabled',true);
		}
		$('#webtoolssearchkeywordresult').html('Found ' + webtools.keywordarray.length + ' Rows');
	}
}

webtools.next = function () {
	if (webtools.keywordarray.length > 0) {
		webtools.currentkeyword++;
		if (webtools.currentkeyword >= webtools.keywordarray.length) {
			webtools.currentkeyword = 0;
		}
		//console.log('Jumping to: ' + logviewer.currentkeyword );
		$('.bg-primary').addClass('bg-info');
		$('.bg-primary').removeClass('bg-primary');
		var targetrow = $('#' + webtools.keywordarray[webtools.currentkeyword]).children();
		$(targetrow[1]).addClass('bg-primary');
		$(targetrow[1]).removeClass('bg-info');
		
		$('html, body').animate({
				scrollTop: ($('#' + webtools.keywordarray[webtools.currentkeyword]).offset().top - 60)
			});
	}
}

webtools.previous = function () {
	if (webtools.keywordarray.length > 0) {
		webtools.currentkeyword--;
		if (webtools.currentkeyword < 0) {
			webtools.currentkeyword = webtools.keywordarray.length-1;
		}

		//console.log('Jumping to: ' + logviewer.currentkeyword );
		$('.bg-primary').addClass('bg-info');
		$('.bg-primary').removeClass('bg-primary');
		var targetrow = $('#' + webtools.keywordarray[webtools.currentkeyword]).children();
		$(targetrow[1]).addClass('bg-primary');
		$(targetrow[1]).removeClass('bg-info');
		
		$('html, body').animate({
				scrollTop: ($('#' + webtools.keywordarray[webtools.currentkeyword]).offset().top - 60)
			});
	}
}

webtools.jumptotop = function () {
	$('html, body').animate({
				scrollTop: (0)
			});
}

webtools.clearresult = function () {
	webtools.keywordarray = [];
	webtools.currentkeyword = 0;
	$('#webtoolssearchkeywordresult').html('');
	$('#webtoolssearchKeyword').val('');
	$('#webtoolssearchbuttonnext').prop('disabled',true);
	$('#webtoolssearchbuttonprevious').prop('disabled',true);
}

webtools.change_theme_display = function () {
	
	var theme_dropdown = ['<select id="custom_theme_selectbox">'];
	theme_dropdown.push('<option value="default.css">default.css');
	webtools.stylesheets.forEach(function(theme) {
		theme_dropdown.push('<option value="' + theme + '">' + theme);
	})
	theme_dropdown.push('</select>');
	$('#myModalLabel').html('<button onclick="webtools.change_theme_reset();" type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Change Theme');
	$('#myModalBody').html('Select one of the available themes to use it:<br>' + theme_dropdown.join('\n') + '<br>Note: Changing theme in the selectbox will automatically enable it as a preview. Upon closing this modal, it will revert back to your settings.');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="webtools.change_theme_work();">Set Theme</button> <button onclick="webtools.change_theme_reset();" type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	$('#custom_theme_selectbox').val(webtools.active_stylesheet);
	$('#myModal').modal('show');
}

webtools.change_theme_work = function() {
	$.ajax({
		url: '/webtools2?module=settings&function=putSetting&name=wt_csstheme&value=' + $('#custom_theme_selectbox').val(),
		type:'PUT',
		dataType:'text',
		success: function (data) {
			webtools.active_stylesheet = $('#custom_theme_selectbox').val();
			$('#custom_theme_stylesheet').remove();
			if (webtools.active_stylesheet !== 'default.css') {
				$('head').append('<link id="custom_theme_stylesheet" rel="stylesheet" href="custom_themes/' + $('#custom_theme_selectbox').val() + '" type="text/css" />');
			}
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Change Theme');
			$('#myModalBody').html('Active theme has been changed.');
			$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
			// Call webtools_wait_for_reload();
			// That function is an ajax call for /, if 404, wait for a few seconds, then try again. Otherwise, notify user of updated completed.
		},
		error: function (data) {
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Change Theme');
			$('#myModalBody').html('An error occured, check the logs for more information.');
			$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
		}
	})
}

webtools.change_theme_reset = function() {
	$('#custom_theme_stylesheet').remove();	
	if (webtools.active_stylesheet !== 'default.css') {
		$('head').append('<link id="custom_theme_stylesheet" rel="stylesheet" href="custom_themes/' + webtools.active_stylesheet + '" type="text/css" />');
	}
	//$('#custom_theme_stylesheet').prop('href',webtools.active_stylesheet);
}


webtools.factory_reset_display = function() {
	// /webtools2?module=wt&function=reset
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Factory Reset');
	$('#myModalBody').html('Are you sure you want to do a factory reset of WebTools?<br><br>Note that this will clear any settings and data related to WebTools and that any channels previously managed by UAS needs to be migrated after reset.');
	$('#myModalFoot').html('<button type="button" onclick="webtools.factory_reset_work()" class="btn btn-default">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>');
	$('#myModal').modal('show');
}

webtools.factory_reset_work = function () {
	
	$.ajax({
		url: '/webtools2?module=wt&function=reset',
		type: 'POST',
		success: function() {
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Waiting for WebTools');
			$('#myModalBody').html('<p id="updateinfo">Waiting for WebTools to come online. Will automatically return you to start when ready.</p>');
			$('#myModalFoot').html('');
			
			console.log('success');
			console.log(data);
			setTimeout(webtools.wait_restart,2000);
		},
		error: function (data) {
			$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Waiting for WebTools');
			$('#myModalBody').html('<p id="updateinfo">Waiting for WebTools to come online. Will automatically return you to start when ready.</p>');
			$('#myModalFoot').html('');
			
			console.log('success');
			console.log(data);
			setTimeout(webtools.wait_restart,2000);
		}
		
	})
}