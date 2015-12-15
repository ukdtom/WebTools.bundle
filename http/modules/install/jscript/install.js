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
    showChannels: function() {}
};

// Alias:
var install = webtools.functions.install;

install.start = function () {
    webtools.longermodulestart = true;
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $('#ContentHeader').html('Install/Update Plugins');
    $('#ContentBody').html('To automatically download and install a channel for Plex, enter it\'s GitHub link below:<br><input type="text" id="gitlink"><button id="gitbutton" onClick="install.initiatedownload();">Install</button><br>Example: https://github.com/ukdtom/plex2csv.bundle <p class="text-danger">We do not offer any support for these channels. We only provide a installation method.</p><br><div id="install_availablechannels"></div>');
    $('#ContentFoot').html('');
    if ($('#LoadingModal').is(':visible') === false) {
      $('#LoadingModal').modal({keyboard: true, backdrop:'static', show:true});    
    }
    install.loadChannels();
};

install.initiatedownload = function () {
    var gitlink = $('#gitlink').val().replace(/\//g,'--wt--');
    $('#myModalLabel').html('Install Plugin');
    $('#myModalBody').html('Sending link to Plex Server to download and install. Please wait while we download and install "' + $('#gitlink').val() + '". We\'ll let you know when things are done.');
    $('#myModalFoot').html('');
    $('#myModal').modal('show');
    
    $.ajax({
        url: '/webtools/install/'+gitlink,
        type: 'GET',
        success: function(data) {
            $('#myModalBody').html('Done. Your channel has been successfully installed.');
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
        },
        error: function(data) {
            $('#myModalBody').html('An error occured, please check the logs.');
            $('#myModalFoot').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
        }
    });
    
    $('#myModal').on('hidden.bs.modal', function (e) {
        $('#gitlink').val('');
    })
};

/*
  Fetch channels and get a list of types (categories)
*/
install.loadChannels = function() {
  
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
      install.channelarray.forEach(function (channel) {
        channel.type.forEach(function (type) {
          if (install.categories.indexOf(type) == -1) {
            install.categories.push(type);     
          }
        })
        install.categories.sort();
      })
      callback();
    }
  ],function (){
    $('#install_availablechannels').html('<table class="table channeltable"><tr><td id="channelmenu" class="channelmenu"></td></tr><tr><td id="channellist"></td></tr>')
    var menu = '';
    install.categories.forEach(function(type) {
      menu += '<button type="button" class="btn btn-default" onclick="install.showChannels(this,\'' + type.trim() + '\')">' + type + '</button> '
    });
    
    $('#channelmenu').html(menu);
    $('#LoadingModal').modal('hide');
  });
  loader.start();
};


/*
 Show channels that are of a specific type (category)
*/
install.showChannels = function(button, type) {
  $('#channelmenu>button').removeClass('btn-active');
  $(button).addClass('btn-active');
  
  $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true}); 
  var channellist = [];
  $('#channellist').html('');
  install.channelarray.forEach(function(channel) {
    if(channel.type.indexOf(type) != -1) {
        var newEntry = ['<div class="panel panel-default">'];
        newEntry.push('<div class="panel-heading"><h4 class="panel-title">' + channel.title + '</h4></div>');
        newEntry.push('<div class="panel-body subtitle"><table class="table table-condensed">');
        newEntry.push('<tr><td rowspan="2" class="icontd"><img src="uas/Resources/' + channel.icon + '" class="icon"></td><td colspan="2">'+channel.description+'</td></tr>')
        newEntry.push('<tr><td id="categoryDiv">Categories: ' + channel.type + '</td><td id="repoDiv">Repo: ' + channel.repo + '</td></tr>')
        newEntry.push('</table></div>');
        newEntry.push('<div class="panel-footer"><button class="btn btn-default btn-xs" onclick="">Install</button></div>');
        newEntry.push('</div>');
        //channellist.push(newEntry);
        $('#channellist').append(newEntry.join('\n'));
    }
  });
 
  $('#LoadingModal').modal('hide');
}