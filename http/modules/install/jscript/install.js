webtools.functions.install = {
    start: function () {},
    hasoptions: false,
    initiatedownload: function() {}
};

// Alias:
var install = webtools.functions.install;

install.start = function () {
    $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
    $('#ContentHeader').html('Install/Update Plugins');
    $('#ContentBody').html('To automatically download and install a channel for Plex, enter it\'s GitHub link below:<br><input type="text" id="gitlink"><button id="gitbutton" onClick="install.initiatedownload();">Install</button><br>Example: https://github.com/ukdtom/plex2csv.bundle <p class="text-danger">We do not offer any support for these channels. We only provide a installation method.</p>');
    $('#ContentFoot').html('');
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