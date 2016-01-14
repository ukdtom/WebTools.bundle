/*
 Created by Mikael Aspehed (Dagalufh)
 Modified to fit APIv2 of WebTools
*/
webtools.functions.logviewer = {
  start: function() {},
  hasoptions: false,
  fetchlogfiles: function() {},
  viewlogfile: function() {}
};

// Alias:
var logviewer = webtools.functions.logviewer;

logviewer.start = function() {
  webtools.loading();
  $('#ContentHeader').html('Viewing Logfile: <select id="LogfileList"></select> <a class="customlink" onClick="logviewer.download($(\'#LogfileList\').val());">Download selected logfile</a> / <a class="customlink" onClick="logviewer.download();">Download all as zip</a>');
  $('#ContentBody').html('');
  $('#ContentFoot').html('');
  logviewer.fetchlogfiles();

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
        $('#LogfileList').append('<option value="' + logname + '">' + logname);
      });
      $('#LogfileList').val("Plex Media Server.log");
      logviewer.viewlogfile("Plex Media Server.log");
    },
    error: function(data, statustext, errorthrown) {
      data.url = this.url;
      webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
    }
  });
};

logviewer.viewlogfile = function(filename) {
  $.ajax({
    url: '/webtools2',
    data: {
      'module': 'logs',
      'function': 'show',
      'fileName': filename
    },
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
          if (data[i].toLowerCase().indexOf('error') != -1) {
            tdnumber = 'bg-info';
            tdtext = 'bg-info';
          }
          
          subtitle += '<tr><td class="' + tdnumber + '">#' + (i + 1) + '</td><td class="' + tdtext + '">' + data[i] + '</td></tr>';
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
      webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.', data);
    }
  });
}

logviewer.download = function(filename) {
  if (typeof(filename) != 'undefined') {
    window.location.href = '/webtools2?module=logs&function=download&fileName=' + filename;
  } else {
    window.location.href = '/webtools2?module=logs&function=download';
  }
}