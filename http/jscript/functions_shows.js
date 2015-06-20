/* ##########################################
################## TV SHOWS #################
#############################################*/
function fetch_section_type_show(section_key, pageToShow) {
    selected_section.currentpage = pageToShow;
    var get_show = new asynchelper(false,false);
    get_show.inline([
        function(callback,section_key) {
            $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
            if (Number(section_key) == 'NaN') {
                get_section_video.abort('Incorrect section key provided. Needs to be number.');
            }

            globalvariables.sections.forEach(function(section) {
                if (section.key == section_key) {
                     selected_section.key = section_key;
                    selected_section.title = section.title;
                    selected_section.contents = [];
                    selected_section.parents_title = [];
                    selected_section.parents_key = [];
                }
            });
            webtools_log(1,'Success: Set a new Current Section. Current section is now: ' + selected_section.title)
            callback('SetCurrentSection:Success');
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
                    webtools_log(1,'Success: Fetched section size for section: ' + selected_section.title + '. It is: ' + selected_section.totalsize)
                    callback('FetchSectionSize:Success');
                },
                error: function(data) {
                    webtools_log(1,'Error: Failed fetching the size of the section. The section was: ' + selected_section.title)
                    display_error('Failed fetching the size of the section from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_show.abort('Error: ' + data.statusText);
                }            
            });
        },
        function(callback) {

            var start = (Number(selected_section.currentpage) * Number(globalvariables.options.items_per_page));
            $('#LoadingBody').html('Library Size: ' + selected_section.totalsize + '<br>Currently fetching: ' + start + '->' + (start+globalvariables.options.items_per_page));
            $.ajax({
                url: '/webtools/section/' + selected_section.key + '/' + start + '/' + globalvariables.options.items_per_page,
                cache: false,
                dataType: 'JSON',
                headers: {'Mysecret':globalvariables.secret},
                success: function(data) {
                    //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
                    data.forEach(function(video){
                        selected_section.contents.push(video);                                    
                        selected_section.contentstype = 'shows';
                    });
                    callback('FetchSectionContents:Success');
                },
                error: function(data) {
                    display_error('Failed fetching the section contents from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_show.abort('Error: ' + data.statusText);
                }
            });   
        }
    ],function(result) {
        webtools_log(0,result);
        //console.log('Size of added seasons:' + selected_section.contents.length);
        display_show(0);
    });
    get_show.start(section_key);
    
}

function fetch_show_seasons(show_key, pageToShow) {
    
    selected_section.currentpage = pageToShow;
    var get_season = new asynchelper(false,false);
    get_season.inline([
        function(callback,show_key) {
            $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
            if (Number(show_key) == 'NaN') {
                get_season.abort('Incorrect section key provided. Needs to be number.');
            }
            
            //console.log(selected_section);
            showfound = false;
            selected_section.contents.forEach(function(content) {
                if (content.key == show_key) {
                    console.log('Found it..');
                    showfound = true;
                    selected_section.parents_key.push(selected_section.key);
                    selected_section.parents_title.push(selected_section.title);


                    selected_section.key = show_key;
                    selected_section.title = content.title;
                    
                }
            });
            
            if (showfound == false) {
                console.log('Didn\'t find it..');
                for (var pk = 0; pk < selected_section.parents_key.length; pk++) {
                
                    if (selected_section.parents_key[pk] == show_key) {
                       
                        


                        selected_section.key = show_key;
                        selected_section.title = selected_section.parents_title[pk];
                        
                        selected_section.parents_key.pop();
                        selected_section.parents_title.pop();
                        break;
                    }    
                }
            }
            
            selected_section.contents = [];
            //console.log(selected_section);
            webtools_log(1,'Success: Set a new Current Section. Current section is now: ' + selected_section.title)
            callback('SetCurrentSection:Success');
        },
        function(callback) {


            $('#LoadingBody').html('Fetching seasons.');
            $.ajax({
                url: '/webtools/show/' + selected_section.key + '/seasons',
                cache: false,
                dataType: 'JSON',
                headers: {'Mysecret':globalvariables.secret},
                success: function(data) {
                    //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
                    data.forEach(function(video){
                        video.title = 'Season ' + video.season;
                        selected_section.contents.push(video); 
                        selected_section.contentstype = 'seasons';
                        
                    });
                    callback('Batchfetch complete.');
                },
                error: function(data) {
                    display_error('Failed fetching the seasons from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);;
                    $('#LoadingModal').modal('hide');
                    get_season.abort('Error: ' + data.statusText);
                }
            });   
        }
    ],function() {
        //console.log(selected_section.contents);
        //console.log('Size of added seasons:' + selected_section.contents.length);
        display_season();
    });
    get_season.start(show_key);
    
}

function fetch_season_episodes(season_key, pageToShow) {
    selected_section.currentpage = pageToShow;
    var get_episodes = new asynchelper(false,false);
    get_episodes.inline([
        function(callback,season_key) {
            $('#LoadingModal').modal({keyboard: false, backdrop:'static', show:true});  
            if (Number(season_key) == 'NaN') {
                get_show.abort('Incorrect section key provided. Needs to be number.');
            }
            
            console.log(selected_section);
            
            selected_section.contents.forEach(function(content) {
                if (content.key == season_key) {
                    
                    selected_section.parents_key.push(selected_section.key);
                    selected_section.parents_title.push(selected_section.title);

                    selected_section.key = season_key;
                    selected_section.title = content.title;
                    
                }
            });
            console.log(JSON.stringify(selected_section.parents_title));
            console.log(JSON.stringify(selected_section.parents_key));
            selected_section.contents = [];
            //console.log(selected_section);
            webtools_log(1,'Success: Set a new Current Section. Current section is now: ' + selected_section.title)
            callback('SetCurrentSection:Success');
        },
        function(callback) {


            $('#LoadingBody').html('Fetching episodes.');
            $.ajax({
                url: '/webtools/show/season/' + selected_section.key + '/getsubs',
                cache: false,
                dataType: 'JSON',
                headers: {'Mysecret':globalvariables.secret},
                success: function(data) {
                    //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
                    data.forEach(function(video){
                        //video.title = 'Season ' + video.season;
                        selected_section.contents.push(video); 
                        selected_section.contentstype = 'episodes';
                        
                    });
                    callback('FetchEpisodes:Success');
                },
                error: function(data) {
                    display_error('Failed fetching the episodes from the server. Please restart the server.<br>'
                                  +'<br>Errorinfo:'
                                  +'<br>Requested URL: ' + this.url
                                  +'<br>Error Code/Message: ' + data.status + '/'  + data.statusText);
                    $('#LoadingModal').modal('hide');
                    get_episodes.abort('Error: ' + data.statusText);
                }
            });   
        }
    ],function() {
        //console.log(selected_section.contents);
        //console.log('Size of added episodes:' + selected_section.contents.length);
        display_episodes();
    });
    get_episodes.start(season_key);    
}