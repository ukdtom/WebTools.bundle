function fetch_section_type_movies(section_key, pageToShow) {
    selected_section.currentpage = pageToShow;
    var get_section_video = new asynchelper(false,false);
    get_section_video.inline([
        function(callback,section_key) {
            $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
            if (Number(section_key) == 'NaN') {
                get_section_video.abort('Incorrect section key provided. Needs to be number.');
            }

            globalvariables.sections.forEach(function(section) {
                if (section.key == section_key) {
                    selected_section.key = section.key;
                    selected_section.title = section.title;
                    selected_section.contents = [];
                    selected_section.parents_key = [];
                    selected_section.parents_title = [];
                }
            });

            callback('Success');
        },
        function(callback) {
            // First, lets check how big the section is that the user requested to see.
            $.ajax({
                url: '/webtools/section/'+selected_section.key+'/size',
                cache: false,
                dataType: 'text',
                headers: {'Mysecret':globalvariables.secret},
                success: function(data) {
                    $('#LoadingBody').html('Library Size: ' + data.replace(/"/g,''));
                    selected_section.totalsize = data.replace(/"/g,'');
                    callback('Success');
                },
                error: function(data) {
                    display_error('Failed fetching the size of the section from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_section_video.abort('Error: ' + data.statusText);
                }            
            });
        },
        function(callback) {
            
            var start = (Number(selected_section.currentpage) * Number(globalvariables.options.items_per_page));
            $('#LoadingBody').html('Library Size: ' + selected_section.totalsize + '<br>Currently fetching: ' + start + '->' + (start+globalvariables.options.items_per_page));
            console.log('Fetching..');
            $.ajax({
                url: '/webtools/section/' + selected_section.key + '/' + start + '/' + globalvariables.options.items_per_page + '/getsubs',
                cache: false,
                dataType: 'JSON',
                headers: {'Mysecret':globalvariables.secret},
                success: function(data) {
                    //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
                    data.forEach(function(video){
                        console.log('Video' + JSON.stringify(video));
                        video.subtitles.showsubs = true;
                        selected_section.contents.push(video);
                        selected_section.contentstype = 'video';
                    });
                    
                    callback('Batchfetch complete.');
                },
                error: function(data) {
                    display_error('Failed fetching the section contents from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_section_video.abort('Error: ' + data.statusText);
                }
            });   
        }
    ],function() {
        //console.log('Size of added videos:' + selected_section.contents.length);
        display_episodes();
    });
    get_section_video.start(section_key);
}