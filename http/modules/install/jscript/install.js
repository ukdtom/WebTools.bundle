webtools.functions.install = {
	start: function() {},
	hasoptions: true,
	options: {
		'items_per_page': 15
	},
	items_per_page_max: 50,
	items_per_page_min: 5,
	search_apps: function () { },
	show_options: function () { },
	save_options: function() {},
	initiatedownload: function() {},
	loadChannels: function() {},
	categories: [],
	showChannels: function() {},
	showOnlyInstalled: false,
	switchShowInstalled: function() {},
	checkForUpdates: function() {},
	removebundleconfirm: function() {},
	removebundlework: function() {},
	allBundles: {},
	backupAllBundles: {},
	initiatemigrate: function() {},
	updatefrompreferences: function() {},
	massiveupdateongoinginstalls: 0,
	channelstoshow: [],
	show_quickjump: function() {},
	forceRepoUpdate: function() {}
};

// Alias:
var install = webtools.functions.install;

install.start = function() {
	webtools.longermodulestart = true;
	var launcher = new asynchelper(false, false);
	launcher.inline([

		function(callback) {
			// Initiate everything
			webtools.loading();
			//$('#ModuleMenu').html('<ul class="nav navbar-nav"><li><a class="customlink" onclick="javascript:install.show_quickjump();">Quick Jump To Bundle</a></li></ul>');
			$('#ContentHeader').html('UnsupportedAppStore');

			var body = ['Welcome to the UnsupportedAppStore. Here you can either install a channel by it\'s Github repository link or by selecting one of the categories below.',
				'If you have installed channels manually before installing WebTools, you can click on the "Migrate manually/previously installed channels" to make WebTools aware of them.',
				'You can also search for updates for all installed channels managed by WebTools via the "Check for updates for all installed channels" button.',
				'Category names contain installed/total available channels.',
				'',
				'',
				'To automatically download and install a channel for Plex, enter it\'s GitHub link below:',
				'<input type="text" id="gitlink" placeholder="https://github.com/ukdtom/ExportTools.bundle"><button id="gitbutton" class="btn btn-default" onClick="install.installfromgit(document.getElementById(\'gitlink\').value);">Install</button>',
				'Example: https://github.com/ukdtom/ExportTools.bundle <p class="text-danger">We do not offer any support for these channels. We only provide a installation method.</p>',
				'<div id="install_availablechannels"></div>'
			];

			var submenu = ['<table class="table channeltable">',
				'<tr>',
				'<td id="installmenu" class="channelmenu"><input type="text" class="form-control pull-left search" placeholder="Search..." id="search"><div class="input-group-btn pull-left"><button class="btn btn-default" type="button" onclick="javascript:install.search_apps();">Search</button></div><button class="btn btn-default" onclick="javascript:install.show_quickjump();">Quick Jump To Bundle</button> <button type="button" class="btn btn-default" onClick="install.initiatemigrate();">Migrate manually/previously installed channels</button> <button type="button" class="btn btn-default" onClick="install.massiveupdatechecker();">Check for updates for all installed channels</button> <button type="button" class="btn btn-default" onClick="install.forceRepoUpdate();">Force repo update</button></td>',
				'</tr>',
				'<tr>',
				'<td id="channelmenu" class="channelmenu"></td>',
				'</tr>',
				'<tr>',
				'<td id="channellist"></td>',
				'</tr>'
			]

			$('#ContentBody').html(body.join('<br>'));
			$('#ContentFoot').html('');
			$('#install_availablechannels').html(submenu.join('\n'));
			callback();
		},

		function(callback) {
			// Fetch the options
			$.ajax({
				url: '/webtools2?module=settings&function=getSetting&name=install.items_per_page',
				type: 'GET',
				success: function(data) {
					install.options.items_per_page = data;
					callback();
				},
				error: function(data) {
					callback();
				}
			});

		}

	], function() {
		// Finally, loadchannels
	    install.loadChannels(true);

	    //on ENTER pressed when focusing the search input -> Search
	    $("#search").on('keyup', function (e) {
	        if (e.keyCode == 13) {
	            install.search_apps();
	        }
	    });
	})

	launcher.start();
};

//Hackz: Size of weird object received from backend. TODO: Get list from backend not object.
Object.size = function (obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

//Searching in allBundles for keyword.
//Will look in description and title
install.search_apps = function () {
    var searchValue = $("#search").val();

    if (Object.size(install.backupAllBundles) > Object.size(install.allBundles)) install.allBundles = install.backupAllBundles;
    var allBundles = install.allBundles;
    install.backupAllBundles = install.allBundles;

    //Temp array.. TODO: Get list from backend instead - WILL IN V3
    var tempArray = [];
    for (var key in allBundles) {
        allBundles[key].key = key;
        tempArray.push(allBundles[key]);
    }

    tempArray = webtools.searchBundle(tempArray, searchValue);

    //Resseting total amount and installed amount
    for (var categorykey in install.categories) {
        install.categories[categorykey].total = 0;
        install.categories[categorykey].installed = 0;
    }

    install.allBundles = {};
    tempArray.forEach(function (object) {
        var tempkey = object.key;
        delete object.key;
        install.allBundles[tempkey] = object;

        object.type.forEach(function (categorykey) {
            if (object.date !== "") install.categories[categorykey].installed++; //Puhaa.. It's getting better with 3.0...
            install.categories[categorykey].total++
        });
    });

    //Again. This can be done way easier with ang.
    //Getting each category and finding the installed and total span.
    for (var categorykey in install.categories) {
        $("#" + categorykey.trim().replace(' ', '')).find("#categoriesInstalled").text(install.categories[categorykey].installed);
        $("#" + categorykey.trim().replace(' ', '')).find("#categoriesTotal").text(install.categories[categorykey].total);
    }

    install.showChannels($('#channelmenu>button.btn-active'), $('#channelmenu>button.btn-active').attr('id'));
}

install.show_options = function() {
	webtools.loading();
	$('#myModalLabel').html('Preferences');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button> <button type="button" class="btn btn-default" onclick="webtools.save_options();">Save Options</button>');

	var options = ['<tr><td><input type="text" name="items_per_page" size="2"></td><td>Items per page <span id="items_per_page_max_min"></span></td></tr>'];

	$('#OptionsTable').html(options.join('<br>'));
	// Populate the dialogbox with correct values.
	$("input[name=items_per_page]").val(install.options.items_per_page);
	$("#items_per_page_max_min").html('(Max: ' + install.items_per_page_max + '. Min: ' + install.items_per_page_min + ')');
	$('#OptionsModalAlert').hide();
}

install.installfromgit = function (github, popupmsg) {
    github = github.trim();
    //If the user insert this manually we need to find the popupmsg
    //We only do this for the ExportTools bundle because the ExportTool is displayed as an example
    if (github === "https://github.com/ukdtom/ExportTools.bundle" && !popupmsg) {
        //Temp array.. TODO: Get list from backend instead
        for (var key in install.allBundles) {
            var currentBundle = install.allBundles[key];

            //TODO: Get ID's on bundles (That will never ever change)
            if (currentBundle.bundle === "ExportTools.bundle") {
                popupmsg = currentBundle.popupmsg;
                break;
            }
        }
    }
    var branch = null;
    popupmsg = (popupmsg ? "<br /><br />" + popupmsg : "");
	
	// Retrieve channel element
	var $channel = $('#channellist .panel[data-url="' + github + '"]');
	if($channel.length !== 0) {
			// Try retrieve selected branch
			var $branchDropdown = $('.branch-dropdown', $channel);

			if($branchDropdown.length !== 0) {
				branch = $branchDropdown.val();
			}
		}

	
	if ((typeof(github) != 'undefined') && (github.length > 0)) {
		//var gitlink = $('#gitlink').val().replace(/\//g,'--wt--');
		$('#myModalLabel').html('Install Plugin');
		$('#myModalBody').html('Sending link to Plex Server to download and install. Please wait while we download and install "' + github + '". We\'ll let you know when things are done.');
		$('#myModalFoot').html('');
		$('#myModal').modal('show');

		$.ajax({
			url: 'webtools2',
			data: {
				'module': 'git',
				'function': 'getGit',
				'url': github,
				'branch': branch
			},
			type: 'GET',
			dataType: 'text',
			success: function (data) {
			    $('#myModalBody').html('Done. Your channel has been successfully installed. Data will be refreshed from the server.' + (popupmsg ? "<br /><br />" : ""));
			    //Popupmsg displaying html tags as text. 
			    //Security reasons because we are getting this from the semi-public json in UAS repo
			    var popupmsgEle = document.createElement("DIV");
			    popupmsgEle.innerHTML = popupmsg;
			    $('#myModalBody').append(popupmsgEle.textContent || popupmsgEle.innerText || "");
				$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="$(\'#gitlink\').val(\'\');install.loadChannels();" data-dismiss="modal">Close</button>');
			},
			error: function(data) {
				console.log(data);
				$('#myModalBody').html('An error occured, please check the logs.<br>' + '<br>Errorinfo:' + '<br>Requested URL: ' + this.url + '<br>Error Code/Message: ' + data.status + '/' + data.statusText);
				$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="$(\'#gitlink\').val(\'\');install.loadChannels();" data-dismiss="modal">Close</button>');
			}
		});
	}
};

/*
  Fetch channels and get a list of types (categories)
*/
install.loadChannels = function (InitalRun) {
	webtools.loading();
	$('#navfoot').html('');
	if (typeof($('#channelmenu>button.btn-active').html()) != 'undefined') {
		var elementToHighlight = $('#channelmenu>button.btn-active');
	}

	var loader = new asynchelper(true, false);
	loader.inline([
		function(callback) {
			if (typeof(InitalRun) != 'undefined') {
				$.ajax({
					url: '/webtools2',
					data: {
						'module': 'git',
						'function': 'updateUASCache'
					},
					cache: false,
					type: 'GET',
					dataType: 'text',
					success: function(data) {
						webtools.log('Successfully called UpdateUASCache. Received: ' + data);
						callback();
					},
					error: function(data) {
						data.url = this.url;
						
						webtools.log('Failed calling UpdateUASCache. Received: ' + data);
						if (data.responseText.indexOf('Errno 13') != -1) {
							webtools.display_error('Failed updating UAS Cache. Looks like permissions are not correct, because we where denied access to create a needed directory.<br>If running on Linux, you might have to issue: <b>sudo chown plex:plex ./WebTools.bundle -R</b>' , data);
						} else {
							webtools.display_error('Failed updating UAS Cache.' , data);
						}
						loader.abort();
					}
				})
			} else {
				callback();
			}
		},
		function(callback) {
			$.ajax({
				url: '/webtools2',
				data: {
					'module': 'pms',
					'function': 'getAllBundleInfo'
				},
				cache: false,
				dataType: 'JSON',
				type: 'GET',
				success: function(data) {
					console.log(data);
					//install.allBundles = data;
					var tempArray = [];
					for (var key in data) {
						data[key].key = key;
						tempArray.push(data[key]);
					}

					tempArray.sort(webtools.dynamicSort('title'));

					install.allBundles = {};
					tempArray.forEach(function(object) {
						var tempkey = object.key;
						delete object.key;
						install.allBundles[tempkey] = object;
						console.log(object);
					})
					callback();
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the list of channels from the server. ', data);
					loader.abort();
				}
			})
		},
		function(callback) {
			$.ajax({
				url: '/webtools2',
				data: {
					'module': 'git',
					'function': 'uasTypes'
				},
				cache: false,
				dataType: 'JSON',
				type: 'GET',
				success: function(data) {

				    install.categories = data;
					//install.categories.sort();
					callback();
				},
				error: function(data) {
					data.url = this.url;
					webtools.display_error('Failed fetching the list of categories from the server. ', data);
					loader.abort();
				}
			})
		}
	], function() {

		var menu = '';
		var checked = '';
		install.showOnlyInstalled = false;
		if (install.showOnlyInstalled === true) {
			checked = 'checked';
		}

		menu += '<label><input ' + checked + ' type="checkbox" id="OnlyShowInstalledCheckbox" onclick="install.switchShowInstalled();"> Only Show Installed</label><br>'
		menu += '<button type="button" class="btn btn-default" id="All" onclick="install.showChannels(this,\'All\')">All</button> '

		for (var categorykey in install.categories) {
			if ((install.categories[categorykey].installed > 0) || (install.showOnlyInstalled === false)) {
				if ((typeof(elementToHighlight) == 'undefined') && (categorykey.trim() == 'Application')) {
				    menu += '<button type="button" class="btn btn-default btn-active" id="' + categorykey.trim().replace(' ', '') + '" onclick="install.showChannels(this,\'' + categorykey.trim() + '\')">' + categorykey + ' (<span id="categoriesInstalled">' + install.categories[categorykey].installed + '</span>/<span id="categoriesTotal">' + install.categories[categorykey].total + '</span>)</button> '
				} else {
				    menu += '<button type="button" class="btn btn-default" id="' + categorykey.trim().replace(' ', '') + '" onclick="install.showChannels(this,\'' + categorykey.trim() + '\')">' + categorykey + ' (<span id="categoriesInstalled">' + install.categories[categorykey].installed + '</span>/<span id="categoriesTotal">' + install.categories[categorykey].total + '</span>)</button> '
				}
			}
		}

		$('#channelmenu').html(menu);

		if (typeof($('#channelmenu>button.btn-active').html()) != 'undefined') {
			elementToHighlight = $('#channelmenu>button.btn-active');
		}

		if (typeof(elementToHighlight) != 'undefined') {
			$('.modal').modal('hide');
			install.showChannels(elementToHighlight, elementToHighlight.attr('id'));
		} else {
			$('.modal').modal('hide');
		}

	});
	loader.start();
};

/*
 Show channels that are of a specific type (category)
*/
install.showChannels = function (button, type, page, highlight) {
	webtools.loading();

	if (typeof(highlight) != 'undefined') {
		$('#OnlyShowInstalledCheckbox').prop('checked', false);
		install.showOnlyInstalled = $('#OnlyShowInstalledCheckbox').prop('checked');
	}

	if (typeof(page) == 'undefined') {
		page = 0;
	}

	// Reset install.channelstoshow
	install.channelstoshow = [];
	$('#channelmenu>button').removeClass('btn-active');
	//$('#All').focus();
	$('#' + type.replace(' ', '')).addClass('btn-active');

	var channellist = [];
	$('#channellist').html('');
	// Preparing for paging
	for (var channelkey in install.allBundles) {
		var isInstalled = false;
		if ((install.allBundles[channelkey].type.indexOf(type) != -1) || (type == 'All')) {

			if ((typeof(install.allBundles[channelkey].date) != 'undefined') && (install.allBundles[channelkey].date.length > 0)) {
				isInstalled = true;
			}
			if (((install.showOnlyInstalled === true) && (isInstalled === true)) || (install.showOnlyInstalled === false)) {
				install.channelstoshow.push(channelkey);
			}
		}
	}

	var start = page * install.options.items_per_page;
	var end = start + install.options.items_per_page;

	if (end >= install.channelstoshow.length) {
		end = install.channelstoshow.length;
	}

	var NumberOfPages = Math.ceil(install.channelstoshow.length / install.options.items_per_page);
	var pages = '';
	if (NumberOfPages > 10) {
		pages = pages + "\t<ul class='pagination pagination-sm'>";
		if ((page - 1) >= 0) {
			pages = pages + '<li><span onclick="install.showChannels(\'Null\',\'' + type + '\',' + (page - 1) + ')">Previous</span></li>';
		}
		pages = pages + '<li><span><select id="pagenr" onChange="install.showChannels(\'Null\',\'' + type + '\',$(\'#pagenr\').val());">';
		for (var f = 0; f < NumberOfPages; f++) {
			if (f == page) {
				pages = pages + '<option selected value="' + f + '">' + (f + 1);
			} else {
				pages = pages + '<option value="' + f + '">' + (f + 1);
			}

		}
		pages = pages + '</select></span></li>';
		if ((page + 1) < NumberOfPages) {
			pages = pages + '<li><span onclick="install.showChannels(\'Null\',\'' + type + '\',' + (page + 1) + ')">Next</span></li>';
		}
		pages = pages + "</ul>";
	} else if (NumberOfPages > 1) {
		pages = pages + "\t<ul class='pagination pagination-sm'>";

		for (var j = 0; j < NumberOfPages; j++) {
			if (j == page) {
				pages = pages + '<li class="active"><span onclick="install.showChannels(\'Null\',\'' + type + '\',' + j + ')">' + (j + 1) + '</span></li>';
			} else {
				pages = pages + '<li><span onclick="install.showChannels(\'Null\',\'' + type + '\',' + j + ')">' + (j + 1) + '</span></li>';
			}

		}
		pages = pages + "</ul>";
	}
	$("#navfoot").html(pages);

	for (var i = start; i < end; i++) {
		var key = install.channelstoshow[i];
		var bundleInfo = install.allBundles[key];
		console.log(bundleInfo);
		var popupmsg = (bundleInfo.popupmsg ? bundleInfo.popupmsg : "");

		var dropdown_branch = '';
		
		var link_install = '';
		var link_update = '';
		var link_uninstall = '';

		var isInstalled = false;
		var installDate = '';
		var rowspan = 3;
		var repolink = '';
		if((typeof(bundleInfo.branches) != 'undefined') && Array.isArray(bundleInfo.branches)) {
			// Retrieve selected branch
			var selectedBranch = null;

			if(typeof(bundleInfo.branch) != 'undefined') {
				selectedBranch = bundleInfo.branch;
			}

			// Build list of dropdown choices
			var choices = '';

			for(var bi = 0; bi < bundleInfo.branches.length; bi++) {
				var branch = bundleInfo.branches[bi];

				choices += (
					'<option value="' + branch.name + '"' + (branch.name == selectedBranch ? 'selected' : '') + '>' +
						branch.label +
					'</option>'
				);
			}

			// Build dropdown element
			dropdown_branch = '<select class="branch-dropdown">' + choices + '</select>';
		}

	if ((typeof(bundleInfo.date) != 'undefined') && (bundleInfo.date.length > 0)) {
			isInstalled = true;
			rowspan = 3;
			if ((key.indexOf('http') != -1) && (key.indexOf('https') != -1)) {
			    link_install = '<button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\', \'' + popupmsg + '\')">Re-Install with latest available</button>';
			}
		}

		
		if ((key.indexOf('http') != -1) && (key.indexOf('https') != -1)) {
			if (isInstalled === false) {
				//link_install = '<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\')">Install</button>';
			    link_install = '<button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\', \'' + popupmsg + '\')">Install</button>';
			}
			repolink = '<a href="' + key + '" target="_NEW">' + key + '</a>';
			//link_update += ' <button class="btn btn-default btn-xs" onclick="install.checkForUpdates(\'' + install.allBundles[key].bundle + '\',\'' + key + '\')">Check for Updates</button>';
			link_update += ' <button class="btn btn-default btn-xs" onclick="install.checkForUpdates(\'' + bundleInfo.bundle + '\',\'' + key + '\')">Check for Updates</button>';
		}
		
		
		//if ((type == 'Unknown') && ((typeof(install.allBundles[key].date) != 'undefined') && (install.allBundles[key].date.length > 0))) {
		//if ((type == 'Unknown') && ((typeof(bundleInfo.date) != 'undefined') && (bundleInfo.date.length > 0))) {
		if (isInstalled === true) {
			//link_uninstall = ' <button class="btn btn-default btn-xs" onclick="install.removebundleconfirm(\'' + key + '\')">Uninstall Bundle</button></div>';
			link_uninstall = ' <button class="btn btn-default btn-xs" onclick="install.removebundleconfirm(\'' + key + '\')">Uninstall Bundle</button>';
		}
		//}
		
		if (((install.showOnlyInstalled === true) && (isInstalled === true)) || (install.showOnlyInstalled === false)) {
			var iconurl = 'icons/NoIcon.png';
			var supporturl = '-';
			var updateTime = '-';
			//if (install.allBundles[key].icon.length > 0) {
			//	iconurl = 'uas/Resources/' + install.allBundles[key].icon;
			if (bundleInfo.icon.length > 0) {
				iconurl = 'uas/Resources/' + bundleInfo.icon;
			}
			
			//if (typeof(install.allBundles[key].supporturl) != 'undefined') {
			//	supporturl = '<a href="' + install.allBundles[key].supporturl + '" target="_NEW">' + install.allBundles[key].supporturl + '</a>';
			//}
			
			if (typeof(bundleInfo.supporturl) != 'undefined') {
				supporturl = '<a href="' + bundleInfo.supporturl + '" target="_NEW">' + bundleInfo.supporturl + '</a>';
 			}
			
			if (typeof(bundleInfo.latestupdateongit) != 'undefined') {
				updateTime = bundleInfo.latestupdateongit;
 			}

			//if (typeof(install.allBundles[key].latestupdateongit) != 'undefined') {
			//	updateTime = install.allBundles[key].latestupdateongit;
			//}

			//var newEntry = ['<div class="panel panel-default" id="' + install.allBundles[key].bundle.replace('.', '').replace(' ', '') + '">'];
			//newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + install.allBundles[key].title + '</h4></div>');
			var newEntry = ['<div class="panel panel-default" id="' + bundleInfo.bundle.replace('.', '').replace(' ', '') + '" data-url="' + key + '">'];
			newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + bundleInfo.title + '</h4></div>');
			newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');
			//newEntry.push('<tr><td rowspan="' + rowspan + '" class="icontd"><img src="' + iconurl + '" class="icon"></td><td>' + install.allBundles[key].description + '</td></tr>')
			//newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Categories:&nbsp;</span> <span class="changeDisplay">' + install.allBundles[key].type + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Repo:&nbsp;</span> <span class="changeDisplay">' + repolink + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Support:&nbsp;</span> <span class="changeDisplay">' + supporturl + '&nbsp;</span></div></td></tr>')
			newEntry.push('<tr><td rowspan="' + rowspan + '" class="icontd"><img src="' + iconurl + '" class="icon"></td><td>' + bundleInfo.description + '</td></tr>')
			newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Categories:&nbsp;</span> <span class="changeDisplay">' + bundleInfo.type + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Repo:&nbsp;</span> <span class="changeDisplay">' + repolink + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Support:&nbsp;</span> <span class="changeDisplay">' + supporturl + '&nbsp;</span></div></td></tr>')
 
			//if (isInstalled === true) {
				//newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Installed:&nbsp;</span> <span class="changeDisplay"> ' + install.allBundles[key].date + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Latest Update on Github:&nbsp;</span> <span class="changeDisplay"><span id="updateTime_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '') + '">' + updateTime + '&nbsp;</span></span></div></td></tr>')
			newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Installed:&nbsp;</span> <span class="changeDisplay"> ' + bundleInfo.date + '&nbsp;</span></div><div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Latest Update on Github:&nbsp;</span> <span class="changeDisplay"><span id="updateTime_' + bundleInfo.bundle.replace('.', '').replace(' ', '') + '">' + updateTime + '&nbsp;</span></span></div></td></tr>')
			//}
			newEntry.push('</table></div>');
			//newEntry.push('<div class="panel-footer">' + link_install + link_update + link_uninstall + '</div>');
			newEntry.push('<div class="panel-footer">' + dropdown_branch + link_install + link_update + link_uninstall + '</div>');
 			
			newEntry.push('</div>');

			$('#channellist').append(newEntry.join('\n'));
		}
	}

	if (typeof(highlight) != 'undefined') {
		window.scrollTo(0, 0);
		$('html, body').animate({
			scrollTop: ($('#' + install.allBundles[highlight].bundle.replace('.', '').replace(' ', '')).offset().top - 60)
		});
		$('#' + install.allBundles[highlight].bundle.replace('.', '').replace(' ', '')).addClass('highlight');
	}
	$('.modal').modal('hide');
}

install.switchShowInstalled = function() {
	install.showOnlyInstalled = $('#OnlyShowInstalledCheckbox').prop('checked');
	if (typeof($('#channelmenu>button.btn-active').html()) != 'undefined') {
		install.showChannels($('#channelmenu>button.btn-active'), $('#channelmenu>button.btn-active').attr('id'));
		//install.loadChannels();
	}
}

install.checkForUpdates = function(spanname, github) {
	webtools.loading();

	$.ajax({
		url: '/webtools2',
		data: {
			'module': 'git',
			'function': 'getLastUpdateTime',
			'url': github
		},
		cache: false,
		dataType: 'text',
		type: 'GET',
		success: function(data) {
			install.allBundles[github].latestupdateongit = data;
			$('#updateTime_' + spanname.replace('.', '').replace(' ', '')).html(data);
			$('.modal').modal('hide');
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed checking for updates for the plugin. ', data);
		}
	})

}
install.removebundleconfirm = function(key) {
	$('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Uninstall bundle from Plex');
	$('#myModalBody').html('Are you sure you want to uninstall "' + install.allBundles[key].title + '"?');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="install.removebundlework(\'' + key + '\');">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>');
	$('#myModal').modal('show');
}

install.removebundlework = function(key) {

	$.ajax({
		url: '/webtools2?module=pms&function=delBundle&bundleName=' + install.allBundles[key].bundle,
		cache: false,
		dataType: 'text',
		type: 'DELETE',
		success: function(data) {

			$('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' has been successfully uninstalled.<br>Will now reload information.');
			$('#myModalFoot').html('<button type="button" class="btn btn-default" onClick="install.loadChannels();" data-dismiss="modal">Close</button>');
		},
		error: function(data) {
			if (data.statusCode().status == 404) {
				$('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' was not found on the server.');
				$('#myModalFoot').html('<button type="button" class="btn btn-default" onClick="install.loadChannels();" data-dismiss="modal">Close</button>');
			} else if (data.statusCode().status == 500) {
				$('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' could not be removed completly.');
				$('#myModalFoot').html('<button type="button" class="btn btn-default" onClick="install.loadChannels();" data-dismiss="modal">Close</button>');
			} else {
				data.url = this.url;
				webtools.display_error('Failed uninstalling the bundle. ', data);
			}
		}
	})
}

install.initiatemigrate = function() {
	webtools.loading();
	$('#myModalLabel').html('Migration');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal" disabled>Close</button>');
	$('#OptionsModalAlert').hide();
	$('#OptionsTable').html('<tr><td>Migration in progress.</td></tr>');
	$.ajax({
		url: '/webtools2?module=git&function=migrate',
		cache: false,
		dataType: 'JSON',
		type: 'PUT',
		success: function(data) {

			$('#myModalLabel').html('Migration');
			var migrated = [];
			migrated.push('<tr><td colspan="2">Below is the list of migrated bundles. These should be managed via Webtools from now on.<td></tr>');
			for (var key in data) {
				var iconurl = 'icons/NoIcon.png';
				if (data[key].icon.length > 0) {
					iconurl = 'uas/Resources/' + data[key].icon;
				}
				migrated.push('<tr><td class="icontd"><img src="' + iconurl + '" class="icon"></td><td>' + data[key].title + '</td></tr>');

			}
			$('#OptionsTable').html(migrated.join('\n'));
			$('#myModalFoot').html('<button type="button" class="btn btn-default" onClick="install.loadChannels();" data-dismiss="modal">Close</button>');
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed migrating previously installed channels.', data);
		}
	})
}

install.massiveupdatechecker = function() {
	webtools.loading();
	$('#myModalLabel').html('Massive Updater');
	$('#myModalBody').html('<div class="alert alert-danger" role="alert" id="OptionsModalAlert"></div><table class="table table-bordered" id="OptionsTable"></table>');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" id="UpdateClose" data-dismiss="modal">Close</button>');

	$('#OptionsTable').html('<tr><td>Searching for updates</td></tr>');
	$('#OptionsModalAlert').hide();
	$('#UpdateClose').prop('disabled', true);
	$.ajax({
		url: '/webtools2?module=git&function=getUpdateList',
		cache: false,
		dataType: 'JSON',
		type: 'GET',
		success: function(data, textStatus, jqXHR) {
			if ((jqXHR.status == 204) || (jQuery.isEmptyObject(data))) {
				$('#OptionsTable').html('<tr><td>No updates are available for any of your installed channels.</td></tr>');
			} else {

				var updates = ['<tr><td>Bundle Title</td><td>Github Time</td><td><button type="button" class="btn btn-default" id="InstallUpdateAll" onclick="install.updateallfrompreferences();">Update All</button></td></tr>'];
				for (var key in data) {
					updates.push('<tr id="updateTR' + install.allBundles[key].bundle.replace('.', '').replace(' ', '') + '"><td>' + data[key].title + '</td><td>' + data[key].gitHubTime + '</td><td><button id="updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '') + '" type="button" class="btn btn-default" onClick="install.updatefrompreferences(\'' + key + '\');">Update</button></td></tr>');
					install.allBundles[key].latestupdateongit = data[key].gitHubTime;
					$('#updateTime_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html(data[key].gitHubTime);
				}
				$('#OptionsTable').html(updates.join('\n'));
			}
			$('#UpdateClose').prop('disabled', false);
		},
		error: function(data) {
			data.url = this.url;
			webtools.display_error('Failed migrating previously installed channels.', data);
		}
	})
}

install.updatefrompreferences = function(key) {

	$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).prop('disabled', true);
	$('#InstallUpdateAll').prop('disabled', true);
	$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Updating...');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" id="UpdateClose" data-dismiss="modal">Close</button>');
	$('#UpdateClose').prop('disabled', true);
	install.massiveupdateongoinginstalls++;
	$.ajax({
		url: 'webtools2',
		data: {
			'module': 'git',
			'function': 'getGit',
			'url': key
		},
		type: 'GET',
		dataType: 'text',
		success: function(data) {
			$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Updated');
			$('#updateTR' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).addClass('bg-success');
			install.massiveupdateongoinginstalls--;

			if (install.massiveupdateongoinginstalls === 0) {
				$('#UpdateClose').prop('disabled', false);
				$('#InstallUpdateAll').prop('disabled', false);
			}
		},
		error: function(data) {
			$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Error');
			$('#updateTR' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).addClass('bg-danger');
			install.massiveupdateongoinginstalls--;

			if (install.massiveupdateongoinginstalls === 0) {
				$('#UpdateClose').prop('disabled', false);
				$('#InstallUpdateAll').prop('disabled', false);
			}
		}
	});
}

install.updateallfrompreferences = function() {
	$("button[id^='updateButton_']").prop('disabled', true);
	$("button[id^='updateButton_']").html('Waiting..');
	$('#myModalFoot').html('<button type="button" class="btn btn-default" id="UpdateClose" data-dismiss="modal">Close</button>');
	$('#UpdateClose').prop('disabled', true);
	$('#InstallUpdateAll').prop('disabled', true);

	var serieupdater = new asynchelper(false, false);
	serieupdater.inline([], function(result) {
		$('#UpdateClose').prop('disabled', false);
	});
	var keystoupdate = [];
	for (var key in install.allBundles) {
		if (typeof(install.allBundles[key].latestupdateongit) != 'undefined') {
			keystoupdate.push(key);
			serieupdater.functionsarray.push(function(callback, keystoupdate) {
				key = keystoupdate.shift();
				$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Updating...');
				$.ajax({
					url: 'webtools2',
					data: {
						'module': 'git',
						'function': 'getGit',
						'url': key
					},
					type: 'GET',
					dataType: 'text',
					success: function(data) {
						$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Updated');
						$('#updateTR' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).addClass('bg-success');
						callback('success', keystoupdate);
					},
					error: function(data) {
						$('#updateButton_' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).html('Error');
						$('#updateTR' + install.allBundles[key].bundle.replace('.', '').replace(' ', '')).addClass('bg-danger');
						install.massiveupdateongoinginstalls--;

						if (install.massiveupdateongoinginstalls === 0) {
							$('#UpdateClose').prop('disabled', false);
						}
						callback('error', keystoupdate);
					}
				});
			});
		}
	}
	serieupdater.start(keystoupdate);
}

install.save_options = function() {
	if (!$.isNumeric($("input[name=items_per_page]").val())) {
		$("input[name=items_per_page]").addClass('bg-danger');
		$('#OptionsModalAlert').html('The items per page can only be numeric');
		$('#OptionsModalAlert').show();
		return false;
	}
	// Make sure that the value is an integer.
	$("input[name=items_per_page]").val(Math.round($("input[name=items_per_page]").val()));


	if (($("input[name=items_per_page]").val() < install.items_per_page_min) || ($("input[name=items_per_page]").val() > install.items_per_page_max)) {
		$("input[name=items_per_page]").addClass('bg-danger');
		$('#OptionsModalAlert').html('The items per page can only be between: ' + install.items_per_page_min + ' and ' + install.items_per_page_max);
		$('#OptionsModalAlert').show();
		return false;
	} else {
		$('#OptionsModalAlert').hide();
		$("input[name=items_per_page]").removeClass('bg-danger');
	}

	install.options.items_per_page = $("input[name=items_per_page]").val();

	var save_options_to_server = new asynchelper(false, true);
	save_options_to_server.inline([
		function(callback) {
			var optionkeys = [];
			for (var key in install.options) {
				optionkeys.push(key);
				save_options_to_server.functionsarray.push(function(callback, optionkeys) {
					var currentkey = optionkeys.shift();
					$.ajax({
						url: '/webtools2?module=settings&function=putSetting&name=install.' + currentkey + '&value=' + install.options[currentkey],
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

		if (typeof($('#channelmenu>button.btn-active').html()) != 'undefined') {
			var elementToHighlight = $('#channelmenu>button.btn-active');
		}

		if (typeof(elementToHighlight) != 'undefined') {
			$('.modal').modal('hide');
			install.showChannels(elementToHighlight, elementToHighlight.attr('id'));
		} else {
			$('.modal').modal('hide');
		}
	});
}

install.show_quickjump = function() {
	webtools.loading();
	var optionlist = []
	optionlist.push('<select id="quickjump">');
	var keys = Object.keys(install.allBundles);
	keys.forEach(function(key, index) {
		optionlist.push('<option value="' + key + '">' + install.allBundles[key].title);
	})
	optionlist.push('</select>');

	$('#myModalLabel').html('Quick Jump To Bundle');
	$('#myModalBody').html(optionlist.join('\n'));
	$('#myModalFoot').html('<button type="button" class="btn btn-default" onClick="install.quickjump($(\'#quickjump\').val())" data-dismiss="modal">Jump To</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
}

install.quickjump = function(key) {
	webtools.loading();
	var bundleindex = Object.keys(install.allBundles).indexOf(key);

	var targetPage = 0;
	var NumberOfPages = Math.ceil(Object.keys(install.allBundles).length / install.options.items_per_page);
	NumberOfPages++;
	for (var i = NumberOfPages; i > 0; i--) {
		if (bundleindex < (install.options.items_per_page * i)) {
			targetPage = i;
		} else {
			break;
		}
	}

	targetPage--;
	var elementToHighlight = $('#All');
	install.showChannels(elementToHighlight, elementToHighlight.attr('id'), targetPage, key);

}

install.forceRepoUpdate = function() {
	webtools.loading();
	$('#myModalLabel').html('Force repo update');
	$.ajax({
		url: '/webtools2?module=git&function=updateUASCache&Force=true',
		cache: false,
		type: 'GET',
		dataType: 'text',
		success: function(data) {
				webtools.log('Successfully called UpdateUASCache. Received: ' + data);
				$('#myModalBody').html("UAS repo cache has been successfully updated.");
				$('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');

		},
		error: function(data) {
			data.url = this.url;

			webtools.log('Failed calling UpdateUASCache. Received: ' + data);
			if (data.responseText.indexOf('Errno 13') != -1) {
				webtools.display_error('Failed updating UAS Cache. Looks like permissions are not correct, because we where denied access to create a needed directory.<br>If running on Linux, you might have to issue: <b>sudo chown plex:plex ./WebTools.bundle -R</b>' , data);
			} else {
				webtools.display_error('Failed updating UAS Cache.' , data);
			}
		}
	})
}