function fetch_movies(section_key) {
    
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
                    for(var i = 0; i<Math.ceil(Number(data.replace(/"/g,''))/globalvariables.itemsperfetch); i++) {
                        get_section_video.functionsarray.push(function(callback,fetchinfo) {
                            var start = (fetchinfo.currentfetch * globalvariables.itemsperfetch);
                            $('#LoadingBody').html('Library Size: ' + data.replace(/"/g,'') + '<br>Currently fetched videos: ' + selected_section.contents.length);
                        
                            fetchinfo.currentfetch = fetchinfo.currentfetch + 1;
                            $.ajax({
                                url: '/webtools/section/' + fetchinfo.sectionkey + '/' + start + '/' + globalvariables.itemsperfetch + '/getsubs',
                                cache: false,
                                dataType: 'JSON',
                                headers: {'Mysecret':globalvariables.secret},
                                success: function(data) {
                                    //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
                                    data.forEach(function(video){
                                        selected_section.contents.push(video);                                    
                                    });
                                    callback('test function',fetchinfo);
                                },
                                error: function(data) {
                                    display_error('Failed fetching the section contents from the server. Please restart the server.');
                                    $('#LoadingModal').modal('hide');
                                    get_section_video.abort('Error: ' + data.statusText);
                                }
                            });

                        });
                    }

                    callback('Success',{sectionkey: selected_section.key, sectionsize: Number(JSON.stringify(data)),currentfetch: 0});
                },
                error: function(data) {
                    display_error('Failed fetching the size of the section from the server. Please restart the server.');
                    $('#LoadingModal').modal('hide');
                    get_section_video.abort('Error: ' + data.statusText);
                }            
            });
        }
    ],function() {
        console.log('Size of added videos:' + selected_section.contents.length);
        display(0);
    });
    get_section_video.start(section_key);
}