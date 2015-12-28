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
    hasoptions: true,
    options: {},
    show_options: function () {$('#OptionsModal').modal('show'); },
    initiatedownload: function() {},
    loadChannels: function() {},
    categories: [],
    showChannels: function() {},
    showOnlyInstalled: false,
    switchShowInstalled: function () {},
    checkForUpdates: function() {},
    removebundleconfirm: function () {},
    removebundlework: function() {},
    allBundles: {},
    initiatemigrate: function() {},
    updatefrompreferences: function() {},
    massiveupdateongoinginstalls: 0
};

// Alias:
var install = webtools.functions.install;

install.start = function () {
    webtools.longermodulestart = true;
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $('#ContentHeader').html('UnsupportedAppStore');
    
    var body = ['Welcome to the UnsupportedAppStore. Here you can either install a channel by it\'s Github repository link or by selecting one of the categories below.',
                'If you have installed channels manually before installing WebTools, you can go into Options-><a class="customlink" onclick="javascript:webtools.functions[\'install\'].show_options();" >Preferences</a> and migrate them to WebTools.',
                'In Options-><a class="customlink" onclick="javascript:webtools.functions[\'install\'].show_options();">Preferences</a> you can also search for updates for all installed channels managed by WebTools.',
                '',
                'To automatically download and install a channel for Plex, enter it\'s GitHub link below:',
                '<input type="text" id="gitlink"><button id="gitbutton" onClick="install.installfromgit(document.getElementById(\'gitlink\').value);">Install</button>',
                'Example: https://github.com/ukdtom/plex2csv.bundle <p class="text-danger">We do not offer any support for these channels. We only provide a installation method.</p>',
                '<div id="install_availablechannels"></div>'];
  
  
    $('#ContentBody').html(body.join('<br>'));
    $('#ContentFoot').html('');
    if ($('#LoadingModal').is(':visible') === false) {
      $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
    }
    $('#OptionsModal').on('show.bs.modal', function (e) {
      var options = ['<tr><td class="aligncenter"><button type="button" class="btn btn-default" onClick="install.initiatemigrate();">Migrate manually/previously installed channels</button></td></tr>',
                      '<tr><td class="aligncenter"><button type="button" class="btn btn-default" onClick="install.massiveupdatechecker();">Check for updates for all installed channels</button></tr>',
                      '<tr><td class="installhidden"></td></tr>']
      $('#OptionsTable').html(options.join('<br>'));
      $('#OptionsFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
    });
    install.loadChannels(true);
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
install.loadChannels = function(InitalRun) {
  if( typeof($('#channelmenu>button.btn-active').html()) != 'undefined' ) {
      var elementToHighlight = $('#channelmenu>button.btn-active');
  }
    
  var loader = new asynchelper(true,false);
  loader.inline([
    function(callback) {
      if (typeof(InitalRun) != 'undefined') {
        $.ajax({
          url: '/webtools2',
          data: {'module':'git','function':'updateUASCache'},
          cache: false,
          type: 'GET',
          dataType: 'text',
          success: function(data) {
            webtools.log('Successfully called UpdateUASCache. Received: ' + data);
            callback();
          },
          error: function(data) {
            webtools.log('Failed calling UpdateUASCache. Received: ' + data);
            webtools.display_error('Failed updating UAS Cache. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
                +'<br>Errorinfo:'
                +'<br>Requested URL: ' + this.url
                +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
            $('#LoadingModal').modal('hide');
            loader.abort();
          }
        })
      } else {
        callback();
      }
    },
    function (callback) {
      $.ajax({
        url: '/webtools2',
        data: {'module':'pms','function':'getAllBundleInfo'},
        cache: false,
        dataType: 'JSON',
        type: 'GET',
        success: function(data) {
          install.allBundles = data;
          callback();
        },
        error: function(data) {
         
          webtools.display_error('Failed fetching the list of channels from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
          loader.abort();
        }
      })
    },
    function (callback) {
      $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'uasTypes'},
        cache: false,
        dataType: 'JSON',
        type: 'GET',
        success: function(data) {
          
          install.categories = data;
          install.categories.sort();
          callback();
        },
        error: function(data) {
         
          webtools.display_error('Failed fetching the list of categories from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
          loader.abort();
        }
      })
    }
  ],function (){
    $('#install_availablechannels').html('<table class="table channeltable"><tr><td id="channelmenu" class="channelmenu"></td></tr><tr><td id="channellist"></td></tr>')
    var menu = '';
    var checked = '';
    if (install.showOnlyInstalled === true) {
      checked = 'checked';
    }
    
    menu += '<label><input ' + checked + ' type="checkbox" id="OnlyShowInstalledCheckbox" onclick="install.switchShowInstalled();"> Only Show Installed</label><br>'
    install.categories.forEach(function(type) {
      
      if ( (typeof(elementToHighlight) == 'undefined') && (type == 'Application') ){
        
        menu += '<button type="button" class="btn btn-default btn-active" id="' + type.trim().replace(' ','') + '" onclick="install.showChannels(this,\'' + type.trim() + '\')">' + type + '</button> '
      } else {
        menu += '<button type="button" class="btn btn-default" id="' + type.trim().replace(' ','') + '" onclick="install.showChannels(this,\'' + type.trim() + '\')">' + type + '</button> '
      }
    });
    
    $('#channelmenu').html(menu);
    
    if( typeof($('#channelmenu>button.btn-active').html()) != 'undefined' ) {
      elementToHighlight = $('#channelmenu>button.btn-active');
    }
    
    if( typeof(elementToHighlight) != 'undefined' ) {
        $('#LoadingModal').modal('hide');
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
  $('#gitlink').focus();
  $('#'+type.replace(' ','')).addClass('btn-active');
  if ($('#LoadingModal').is(':visible') === false) {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true}); 
  }
  var channellist = [];
  $('#channellist').html('');
  
  for(var key in install.allBundles) {
    if(install.allBundles[key].type.indexOf(type) != -1) {
      var installlink = '<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\')">Install</button></div>';
      
      var isInstalled = false;
      var installDate = '';
      var rowspan = 2;
      
      if ( (typeof(install.allBundles[key].date) != 'undefined') && (install.allBundles[key].date.length > 0) ){
        isInstalled = true;
        rowspan = 3;
        installlink = '<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="install.installfromgit(\'' + key + '\')">Re-Install with latest available</button> <button class="btn btn-default btn-xs" onclick="install.checkForUpdates(\'' + install.allBundles[key].bundle + '\',\'' + key + '\')">Check for Updates</button> <button class="btn btn-default btn-xs" onclick="install.removebundleconfirm(\'' + key + '\')">Uninstall Bundle</button></div>';
      }
        if( ( (install.showOnlyInstalled === true) && (isInstalled === true) ) || (install.showOnlyInstalled === false) ) {
          var iconurl = 'icons/NoIcon.png';
          var supporturl = '-';
          var updateTime = '-';
          if (install.allBundles[key].icon.length > 0) {
            iconurl = 'uas/Resources/' + install.allBundles[key].icon;
          }
          if (typeof(install.allBundles[key].supporturl) != 'undefined') {
            supporturl = '<a href="' + install.allBundles[key].supporturl + '" target="_NEW">' + install.allBundles[key].supporturl + '</a>';
          }
          
          if (typeof(install.allBundles[key].latestupdateongit) != 'undefined') {
            updateTime = install.allBundles[key].latestupdateongit;
          }
          var newEntry = ['<div class="panel panel-default">'];
          newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + install.allBundles[key].title + '</h4></div>');
          newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');
          newEntry.push('<tr><td rowspan="' + rowspan + '" class="icontd"><img src="' + iconurl + '" class="icon"></td><td>'+install.allBundles[key].description+'</td></tr>')
          newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Categories:&nbsp;</span> <span class="changeDisplay">' + install.allBundles[key].type + '</span></div>&nbsp;<div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Repo:&nbsp;</span> <span class="changeDisplay"><a href="' + key + '" target="_NEW">' + key + '</a></span></div>&nbsp;<div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Support:&nbsp;</span> <span class="changeDisplay">'+supporturl+'</span></div></td></tr>')
          
          if (isInstalled === true) {
            newEntry.push('<tr><td colspan="2"><div class="categoryDiv changeDisplay marginRight"><span class="changeDisplay subheadline">Installed:&nbsp;</span> <span class="changeDisplay"> ' + install.allBundles[key].date + '</span></div>&nbsp;<div class="categoryDiv changeDisplay"><span class="changeDisplay subheadline">Latest Update on Github:&nbsp;</span> <span class="changeDisplay"><span id="updateTime_' + install.allBundles[key].bundle.replace('.','') + '">' + updateTime + '</span></span></div></td></tr>')
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
  if ($('#LoadingModal').is(':visible') === false) {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true}); 
  }
  $.ajax({
        url: '/webtools2',
        data: {'module':'git','function':'getLastUpdateTime','url':github},
        cache: false,
        dataType: 'text',
        type: 'GET',
        success: function(data) {
          install.allBundles[github].latestupdateongit = data;
          $('#updateTime_'+spanname.replace('.','')).html(data);
          $('#LoadingModal').modal('hide');
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
        $('#myModalBody').html('Are you sure you want to uninstall "' + install.allBundles[key].title + '"?');
        $('#myModalFoot').html('<button type="button" class="btn btn-default" onclick="install.removebundlework(\'' + key + '\');">Yes</button> <button type="button" class="btn btn-default" data-dismiss="modal">No</button>');
        $('#myModal').modal('show');    
}

install.removebundlework = function (key) {
  
   $.ajax({
        url: '/webtools2?module=pms&function=delBundle&bundleName=' + install.allBundles[key].bundle,
        cache: false,
        dataType: 'text',
        type: 'DELETE',
        success: function(data) {
         
          $('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' has been successfully uninstalled.<br>Will now reload information.');
          $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
        },
        error: function(data) {
          if (data.statusCode().status == 404) {
              $('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' was not found on the server.');
              $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
          } else if (data.statusCode().status == 500) {
              $('#myModalBody').html('Bundle ' + install.allBundles[key].title + ' could not be removed completly.');
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

install.initiatemigrate = function () {
  $('#OptionsModal').modal('hide');
  if ($('#LoadingModal').is(':visible') === false) {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true}); 
  }
  $.ajax({
        url: '/webtools2?module=git&function=migrate',
        cache: false,
        dataType: 'text',
        type: 'PUT',
        success: function(data) {
         install.loadChannels();
        },
        error: function(data) {
          webtools.display_error('Failed migrating previously installed channels.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
          $('#LoadingModal').modal('hide');
        }
      })  
}

install.massiveupdatechecker = function () {
  $('#OptionsTable').html('<tr><td>Searching for updates</td></tr>');
  $.ajax({
        url: '/webtools2?module=git&function=getUpdateList',
        cache: false,
        dataType: 'JSON',
        type: 'GET',
        success: function(data, textStatus, jqXHR) {
         if( (jqXHR.status == 204) || (jQuery.isEmptyObject(data))) {
           $('#OptionsTable').html('<tr><td>No updates are available for any of your installed channels.</td></tr>');
         } else {
           
           var updates = ['<tr><td>Bundle Title</td><td>Github Time</td><td><button type="button" class="btn btn-default" id="InstallUpdateAll" onclick="install.updateallfrompreferences();">Update All</button></td></tr>'];
           for(var key in data) {
             updates.push('<tr id="updateTR' + install.allBundles[key].bundle.replace('.','') + '"><td>'+data[key].title+'</td><td>'+data[key].gitHubTime+'</td><td><button id="updateButton_' + install.allBundles[key].bundle.replace('.','') + '" type="button" class="btn btn-default" onClick="install.updatefrompreferences(\''+key+'\');">Update</button></td></tr>');
             install.allBundles[key].latestupdateongit = data[key].gitHubTime;
             $('#updateTime_'+install.allBundles[key].bundle.replace('.','')).html(data[key].gitHubTime);
           }
          $('#OptionsTable').html(updates.join('\n'));
         }
        },
        error: function(data) {
          webtools.display_error('Failed migrating previously installed channels.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
              +'<br>Errorinfo:'
              +'<br>Requested URL: ' + this.url
              +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
        }
      })  
}

install.updatefrompreferences = function(key) {
  
  $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).prop('disabled',true);
  $('#InstallUpdateAll').prop('disabled',true);
  $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Updating...');
  $('#OptionsFoot').html('<button type="button" class="btn btn-default" id="UpdateClose" data-dismiss="modal">Close</button>');
  $('#UpdateClose').prop('disabled',true);
  install.massiveupdateongoinginstalls++;
  $.ajax({
        url: 'webtools2',
        data: {'module':'git','function':'getGit','url':key},
        type: 'GET',
        dataType: 'text',
        success: function(data) {
            $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Updated');
            $('#updateTR' + install.allBundles[key].bundle.replace('.','')).addClass('bg-success');
            install.massiveupdateongoinginstalls--;
          
            if (install.massiveupdateongoinginstalls === 0) {
              $('#UpdateClose').prop('disabled',false);
              $('#InstallUpdateAll').prop('disabled',false);
            }
        },
        error: function(data) {
            $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Error');
            $('#updateTR' + install.allBundles[key].bundle.replace('.','')).addClass('bg-danger');
            install.massiveupdateongoinginstalls--;
          
            if (install.massiveupdateongoinginstalls === 0) {
              $('#UpdateClose').prop('disabled',false);
              $('#InstallUpdateAll').prop('disabled',false);
            }
        }
    });
}

install.updateallfrompreferences = function() {
  $( "button[id^='updateButton_']").prop('disabled',true);
  $( "button[id^='updateButton_']").html('Waiting..');
  $('#OptionsFoot').html('<button type="button" class="btn btn-default" id="UpdateClose" data-dismiss="modal">Close</button>');
  $('#UpdateClose').prop('disabled',true);
  $('#InstallUpdateAll').prop('disabled',true);
  
  var serieupdater = new asynchelper(false,false);
  serieupdater.inline([],function(result) {
       $('#UpdateClose').prop('disabled',false);
  });
  var keystoupdate = [];
  for(var key in install.allBundles) {
     if (typeof(install.allBundles[key].latestupdateongit) != 'undefined') {
       keystoupdate.push(key);
       serieupdater.functionsarray.push(function(callback,keystoupdate) {
         key = keystoupdate.shift();
         $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Updating...');
         $.ajax({
          url: 'webtools2',
          data: {'module':'git','function':'getGit','url':key},
          type: 'GET',
          dataType: 'text',
          success: function(data) {
              $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Updated');
              $('#updateTR' + install.allBundles[key].bundle.replace('.','')).addClass('bg-success');
              callback('success',keystoupdate);
          },
          error: function(data) {
              $('#updateButton_' + install.allBundles[key].bundle.replace('.','')).html('Error');
              $('#updateTR' + install.allBundles[key].bundle.replace('.','')).addClass('bg-danger');
              install.massiveupdateongoinginstalls--;

              if (install.massiveupdateongoinginstalls === 0) {
                $('#UpdateClose').prop('disabled',false);
              }
              callback('error',keystoupdate);
          }
        });
       });
     }
  }  
  serieupdater.start(keystoupdate);
}

install.initiateloading = function() {
 $('#OptionsModal').modal('hide');
}
$('#OptionsModal').on('hidden.bs.modal', function (e) {
      if (typeof($('#UpdateClose').html()) != 'undefined') {
        if ($('#LoadingModal').is(':visible') === false) {
            $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
        }
        install.loadChannels();
      }
    }) 