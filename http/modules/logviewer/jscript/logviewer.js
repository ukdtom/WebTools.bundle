/*
 Created by Mikael Aspehed (Dagalufh)
 Modified to fit APIv2 of WebTools
*/
webtools.functions.logviewer = {
  start: function() {},
  hasoptions: false,
  fetchlogfiles: function() {},
  viewlogfile: function() {}, 
};

// Alias:
var logviewer = webtools.functions.logviewer;

logviewer.start = function() {
  webtools.loading();
  $('#ContentHeader').html('Viewing Logfile: <select id="LogfileList"></select> <a class="customlink" onClick="logviewer.download($(\'#LogfileList\').val());">Download selected logfile</a> / <a class="customlink" onClick="logviewer.download();">Download all as zip</a><br>');
  $('#ContentBody').html('');
  $('#ContentFoot').html('');
  logviewer.fetchlogfiles();
	$('#navfoot').html('<input type="text" id="webtoolssearchKeyword" onkeydown="if (event.keyCode == 13) { webtools.searchkeyword(\'logtable\'); }"><button class="btn btn-default btn-xs" onclick="webtools.searchkeyword(\'logtable\')">Search keyword</button> <button class="btn btn-default btn-xs" onclick="webtools.previous()" id="webtoolssearchbuttonprevious">Previous</button><button class="btn btn-default btn-xs" onclick="webtools.next()" id="webtoolssearchbuttonnext">Next</button> <button class="btn btn-default btn-xs" onclick="webtools.jumptotop()">Jump to Top</button> <span id="webtoolssearchkeywordresult"></span>');
	webtools.clearresult();
  $('#LogfileList').change(function() {
    // Display loading screen when fetching.
    webtools.loading();
    logviewer.viewlogfile($(this).val());
  });
};

logviewer.fetchlogfiles = function() {
  $.ajax({
    url: '/webtools2',
    datatype: 'json',
    data: {
      "module": "logs",
      "function": "list"
    },
    type: 'GET',
    cache: false,
    success: function(data) {
      data.forEach(function(logname) {
				var downloadlogname = logname.replace(/ /g, "%20");
        $('#LogfileList').append('<option value="' + downloadlogname + '">' + logname);
      });
      $('#LogfileList').val("Plex%20Media%20Server.log");
      logviewer.viewlogfile("Plex%20Media%20Server.log");
    },
    error: function(data, statustext, errorthrown) {
      data.url = this.url;
      webtools.display_error('Failed fetching the settings from the server.', data);
    }
  });
};

logviewer.viewlogfile = function(filename) {
	webtools.clearresult();
  $.ajax({
    url: '/webtools2?module=logs&function=show&fileName=' + filename,
    cache: false,
    type: 'GET',
    dataType: 'JSON',
    success: function(data) {
      webtools.log('Fetched ' + filename);
      var subtitle = '<table class="table table-bordered smallfont" id="logtable">';
      subtitle += '<tr><th class="td-small">Row#</th><th>Logentry</th></tr>';
      if (data.length > 0) {
        for (var i = 0; i < data.length; i++) {
          var tdnumber = 'bg-warning';
          var tdtext = '';
          
          if (data[i].toLowerCase().indexOf('critical') != -1) {
            tdnumber = 'bg-danger';
            tdtext = 'bg-danger';
          }
          if (data[i].toLowerCase().indexOf('exception') != -1) {
            tdnumber = 'bg-danger';
            tdtext = 'bg-danger';
          }
          if (data[i].toLowerCase().indexOf('error') != -1) {
            tdnumber = 'bg-info';
            tdtext = 'bg-info';
          }
          
          subtitle += '<tr id="'+ (i + 1) +'"><td class="' + tdnumber + '">#' + (i + 1) + '</td><td class="' + tdtext + '">' + data[i] + '</td></tr>';
        }
      } else {
        subtitle += '<tr><td class="bg-warning">#-</td><td>Empty file</td></tr>';
      }
      subtitle += '</table>';

      $('#ContentBody').html(subtitle);
      $('#ContentFoot').html('<a href="/webtools2?module=logs&function=download&fileName=' + filename + '">Download Logfile</a>');

      $('.modal').modal('hide');
    },
    error: function(data) {
      data.url = this.url;
      webtools.log('Failed fetching ' + filename);
      webtools.display_error('Failed fetching the logfile from the server.', data);
    }
  });
}

logviewer.download = function(filename) {
  if (typeof(filename) != 'undefined') {
		webtools.log('Trying to download: ' + filename);
    window.location.href = '/webtools2?module=logs&function=download&fileName=' + filename;
  } else {
		webtools.log('Trying to download: ' + filename);
    window.location.href = '/webtools2?module=logs&function=download';
  }
}

