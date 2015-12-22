/*

  "title"           :     "AniDB.net Metadata Agent",
  "bundle"          :     "AniDB.bundle",
  "type"            :     ["Metadata Agent"],
  "description"     :     "Metadata agent for anime movies and tv-shows",
  "repo"            :     "https://github.com/bstard/AniDB.bundle",
  "branch"          :     "master",
  "identifier"      :     "com.plexapp.agents.anidb",
  "icon" 

*/
webtools.functions.install = {
    start: function () {},
    hasoptions: false,
    initiatedownload: function() {},
    loadChannels: function() {},
    channelarray: [],
    categories: [],
    showChannels: function() {},
    installedarray: [],
    showOnlyInstalled: false,
    switchShowInstalled: function () {},
    checkForUpdates: function() {},
    removebundleconfirm: function () {},
    removebundlework: function() {}
};

// Alias:
var install = webtools.functions.install;

install.start = function () {
    webtools.longermodulestart = true;
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $('#ContentHeader').html('UnsupportedAppStore');
    $('#ContentBody').html('To automatically download and install a channel for Plex, enter it\'s GitHub link below:<br><input type="text" id="gitlink"><button id="gitbutton" onClick="install.installfromgit(document.getElementById(\'gitlink\').value);">Install</button><br>Example: https://github.com/ukdtom/plex2csv.bundle <p class="text-danger">We do not offer any support for these channels. We only provide a installation method.</p><br><div id="install_availablechannels"></div>');
    $('#ContentFoot').html('');
    if ($('#LoadingModal').is(':visible') === false) {
      $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
    }
    install.loadChannels();
};

install.installfromgit = function (github) {
    
    //var gitlink = $('#gitlink').val().replace(/\//g,'--wt--');
    $('#myModalLabel').html('Install Plugin');
    $('#myModalBody').html('Sending link to Plex Server to download and install. Please wait while we download and install "' + github + '". We\'ll let you know when things are done.');
    $('#myModalFoot').html('');
    $('#myModal').modal('show');
    
    $.ajax({
        url: 'webtools2',
        data: {'module':'git','function':'getGit','url':github},
        type: 'GET',
        dataType: 'text',
        success: function(data) {
            $('#myModalBody').html('Done. Your channel has been successfully installed. Data will be refreshed from the server.');
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            
          
        },
        error: function(data) {
            $('#myModalBody').html('An error occured, please check the logs.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
        }
    });
    
    $('#myModal').on('hidden.bs.modal', function (e) {
        $('#gitlink').val('');
        if ($('#LoadingModal').is(':visible') === false) {
            $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
        }
        install.loadChannels();
    })
};

/*
  Fetch channels and get a list of types (categories)
*/
install.loadChannels = function() {
 
  
  if( typeof($('#channelmenu>button.btn-active').html()) != 'undefined' ) {
    var elementToHighlight = $('#channelmenu>button.btn-active');
  }
  
  
  var loader = new asynchelper(true,false);
  loader.inline([
    function(callback) {
      
      $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'updateUASCache'},
        cache: false,
        type: 'GET',
        success: function(data) {
          callback();
        },
        error: function(data) {
          callback();
        }
      })
      
    },
    function (callback) {
      $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'list'},
        cache: false,
        dataType: 'text',
        type: 'GET',
        success: function(data) {
          
          install.installedarray = JSON.parse(data);
          callback();
        },
        error: function(data) {
         
          webtools.display_error('Failed fetching the list of already installed channels from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
          loader.abort();
        }
      })
    },
    function(callback) {
      
      $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'getListofBundles'},
        cache: false,
        type: 'GET',
        success: function(data) {
          install.channelarray = data;
          callback();
        },
        error: function(data) {
          webtools.display_error('Failed fetching the list of available channels from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
          loader.abort();
        }
      })
      
    },
    function (callback) {
    
      for(var key in install.channelarray) {
        install.channelarray[key].type.forEach(function (type) {
          if (install.categories.indexOf(type) == -1) {
            install.categories.push(type);
          }
        })
        
      }
      
      install.categories.sort();
      callback();
    }
    
  ],function (){
    $('#install_availablechannels').html('<table class="table channeltable"><tr><td id="channelmenu" class="channelmenu"></td></tr><tr><td id="channellist"></td></tr>')
    var menu = '';
    menu += '<label><input type="checkbox" id="OnlyShowInstalledCheckbox" onclick="install.switchShowInstalled();"> Only Show Installed</label><br>'
    install.categories.forEach(function(type) {
      menu += '<button type="button" class="btn btn-default" id="' + type.trim().replace(' ','') + '" onclick="install.showChannels(this,\'' + type.trim() + '\')">' + type + '</button> '
    });
    
    $('#channelmenu').html(menu);
    
    if( typeof(elementToHighlight) != 'undefined' ) {
        install.showChannels(elementToHighlight,elementToHighlight.html());
    } else {
      $('#LoadingModal').modal('hide');
    }

  });
  loader.start();
};


/*
 Show channels that are of a specific type (category)
*/
install.showChannels = function(button, type) {
  $('#channelmenu>button').removeClass('btn-active');
  $('#'+type.replace(' ','')).addClass('btn-active');
  if ($('#LoadingModal').is(':visible') === false) {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true}); 
  }
  var channellist = [];
  $('#channellist').html('');
  
  for(var key in install.channelarray) {
    if(install.channelarray[key].type.indexOf(type) != -1) {
      var installlink = '<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\')">Install</button></div>';
      
      var isInstalled = false;
      var installDate = '';
      var rowspan = 2;
      for(var installed_key in install.installedarray) {
        if (installed_key == key) {
            isInstalled = true;
            installDate = install.installedarray[installed_key].date;
            rowspan = 3;
            installlink = '<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\')">Re-Install with latest available</button> <button class="btn btn-default btn-xs" onclick="install.checkForUpdates(\'' + install.channelarray[key].bundle + '\',\'' + key + '\')">Check for Updates</button> <button class="btn btn-default btn-xs" onclick="install.removebundleconfirm(\'' + key + '\')">Uninstall Bundle</button></div>';
          break;
        }
      }

        if( ( (install.showOnlyInstalled === true) && (isInstalled === true) ) || (install.showOnlyInstalled === false) ) {
          var newEntry = ['<div class="panel panel-default">'];
          newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + install.channelarray[key].title + '</h4></div>');
          newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');
          newEntry.push('<tr><td rowspan="' + rowspan + '" class="icontd"><img src="uas/Resources/' + install.channelarray[key].icon + '" class="icon"></td><td>'+install.channelarray[key].description+'</td></tr>')
          newEntry.push('<tr><td colspan="2"><div id="categoryDiv" class="changeDisplay marginRight"><span class="changeDisplay subheadline">Categories:&nbsp;</span> <span class="changeDisplay">' + install.channelarray[key].type + '</span></div><div class="changeDisplay"><span class="changeDisplay subheadline">Repo:&nbsp;</span> <span class="changeDisplay"><a href="' + key + '" target="_NEW">' + key + '</a></span></div></td></tr>')
          
          if (isInstalled === true) {
            newEntry.push('<tr><td colspan="2"><div id="categoryDiv" class="changeDisplay marginRight"><span class="changeDisplay subheadline">Installed:&nbsp;</span> <span class="changeDisplay"> ' + installDate + '</span></div><div class="changeDisplay"><span class="changeDisplay subheadline">Latest Update on Github:&nbsp;</span> <span class="changeDisplay"><span id="updateTime_' + install.channelarray[key].bundle.replace('.','') + '">-</span></span></div></td></tr>')
            //newEntry.push('<tr><td id="categoryDiv">Installed: ' + installDate + '</td><td>Latest Update on Github: <span id="updateTime">-</span></td></tr>')
          }
          newEntry.push('</table></div>');
          newEntry.push(installlink);
          newEntry.push('</div>');
          //channellist.push(newEntry);
          $('#channellist').append(newEntry.join('\n'));
        }
    }
  }
 
  $('#LoadingModal').modal('hide');
}

install.switchShowInstalled = function() {
  install.showOnlyInstalled = $('#OnlyShowInstalledCheckbox').prop('checked');
  if( typeof($('#channelmenu>button.btn-active').html()) != 'undefined' ) {
    install.showChannels($('#channelmenu>button.btn-active'),$('#channelmenu>button.btn-active').html());
  }
}

install.checkForUpdates = function(spanname, github) {

  $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'getLastUpdateTime','url':github},
        cache: false,
        dataType: 'text',
        type: 'GET',
        success: function(data) {
         
          $('#updateTime_'+spanname.replace('.','')).html(data);
        },
        error: function(data) {
          webtools.display_error('Failed checking for updates for the plugin. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
        }
      })
  
}
install.removebundleconfirm = function (key) {
        $('#myModalLabel').html('<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> Uninstall bundle from Plex');
        $('#myModalBody').html('Are you sure you want to uninstall "' + install.channelarray[key].title + '"?');
        $('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="install.removebundlework(\'' + key + '\');">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>');
        $('#myModal').modal('show');    
}

install.removebundlework = function (key) {
  
  ///webtools2?module=pms&function=delBundle&bundleName=plex2csv.bundle
   $.ajax({
        url: '/webtools2?module=pms&function=delBundle&bundleName=' + install.channelarray[key].bundle,
        cache: false,
        dataType: 'text',
        type: 'DELETE',
        success: function(data) {
         
          $('#myModalBody').html('Bundle ' + install.channelarray[key].title + ' has been successfully uninstalled.<br>Will now reload information.');
          $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
        },
        error: function(data) {
          if (data.statusCode().status == 404) {
              $('#myModalBody').html('Bundle ' + install.channelarray[key].title + ' was not found on the server.');
              $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
          } else if (data.statusCode().status == 500) {
              $('#myModalBody').html('Bundle ' + install.channelarray[key].title + ' could not be removed completly.');
              $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
          } else {
          webtools.display_error('Failed uninstalling the bundle. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          }
        }
      })
    $('#myModal').on('hidden.bs.modal', function (e) {
      if ($('#LoadingModal').is(':visible') === false) {
            $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
        }
        install.loadChannels();
    })
}