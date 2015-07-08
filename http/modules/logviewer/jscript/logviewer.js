webtools.functions.logviewer = {
    start: function () {},
    hasoptions: false,
    fetchlogfiles: function () {},
    viewlogfile: function () {}
};

// Alias:
var logviewer = webtools.functions.logviewer;

logviewer.start = function () {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $('#ContentHeader').html('Viewing Logfile: <select id="LogfileList"></select>');
    $('#ContentBody').html('');
    $('#ContentFoot').html('');
    logviewer.fetchlogfiles();
    
    $('#LogfileList').change(function() {        
        console.log('change');
        logviewer.viewlogfile($(this).val());
    });
};

logviewer.fetchlogfiles = function () {
    $.ajax({
        url: '/webtools/logs',
        datatype: 'JSON',
        type: 'GET',
        cache: false,
        success: function (data) {
            data.forEach(function (logname) {
                $('#LogfileList').append('<option value="' + logname + '">' + logname);
            });
            
            logviewer.viewlogfile($('#LogfileList').val());
            
        },
        error: function(data) {
            webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
                          +'<br>Errorinfo:'
                          +'<br>Requested URL: ' + this.url
                          +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
            $('#LoadingModal').modal('hide');
        }
    });
};

logviewer.viewlogfile = function (filename) {
    //$('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $.ajax({
        url: '/webtools/logs/show/'+filename,
        cache: false,
        type: 'GET',
        dataType: 'JSON',
        success: function(data) {
            var subtitle = '<table class="table table-bordered">';
            subtitle += '<tr><th class="td-small">Row#</th><th>Logentry</th></tr>';
            if (data.length > 0) {
                for (i=0;i<data.length;i++) {
                    subtitle += '<tr><td class="bg-warning">#'+(i+1) + '</td><td>' + data[i] + '</td></tr>';
                }
            } else {
                subtitle += '<tr><td class="bg-warning">#-</td><td>Empty file</td></tr>';
            }
            subtitle += '</table>';
            
            $('#ContentBody').html(subtitle);
            $('#ContentFoot').html('<a href="/webtools/logs/download/'+filename+'">Download Logfile</a>');
            
            $('#LoadingModal').modal('hide');
            
        },
        error: function(data) {
            webtools.display_error('Failed fetching the settings from the server. Reload the page and try again.<br>If the error persists please restart the server.<br>Contact devs on the Plex forums if it occurs again.<br>'
                          +'<br>Errorinfo:'
                          +'<br>Requested URL: ' + this.url
                          +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
            $('#LoadingModal').modal('hide');
        }
    }); 
}