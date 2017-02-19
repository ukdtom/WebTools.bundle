/* ##########################################
################## TV SHOWS #################
############################################# */
subtitlemgmt.fetch_section_type_show = function(section_key, pageToShow) {
  subtitlemgmt.selected_section.currentpage = Number(pageToShow);
  var get_show = new asynchelper(false, false);
  get_show.inline([
    function(callback, section_key) {
      $('#navfoot').html('');
      $('#ContentFoot').html('');
      webtools.loading();
      if (Number(section_key) == 'NaN') {
        get_show.abort('Incorrect section key provided. Needs to be number.');
      }

      subtitlemgmt.sections.forEach(function(section) {
        if (section.key == section_key) {
          subtitlemgmt.selected_section.key = section_key;
          subtitlemgmt.selected_section.title = section.title;
          subtitlemgmt.selected_section.contents = [];
          subtitlemgmt.selected_section.parents_title = [];
          subtitlemgmt.selected_section.parents_key = [];
        }
      });
      webtools.log('Success: Set a new Current Section. Current section is now: ' + subtitlemgmt.selected_section.title)
      callback('SetCurrentSection:Success');
    },
    function(callback) {
      // First, lets check how big the section is that the user requested to see.
      $.ajax({
        url: 'webtools2?module=pms&function=getSectionSize&key=' + subtitlemgmt.selected_section.key,
        cache: false,
        dataType: 'text',
        success: function(data) {
          webtools.loading('Library Size: ' + data.replace(/"/g, ''));
          subtitlemgmt.selected_section.totalsize = data.replace(/"/g, '');
          webtools.log('Success: Fetched section size for section: ' + subtitlemgmt.selected_section.title + '. It is: ' + subtitlemgmt.selected_section.totalsize)
          callback('FetchSectionSize:Success');
        },
        error: function(data) {
          data.url = this.url;
          webtools.log('Error: Failed fetching the size of the section. The section was: ' + subtitlemgmt.selected_section.title)
          webtools.display_error('Failed fetching the size of the section from the server. ', data);
          get_show.abort('Error: ' + data.statusText);
        }
      });
    },
    function(callback) {
      var start = (Number(subtitlemgmt.selected_section.currentpage) * Number(subtitlemgmt.options.items_per_page));
      webtools.loading('Library Size: ' + subtitlemgmt.selected_section.totalsize + '<br>Currently fetching: ' + start + '->' + (start + subtitlemgmt.options.items_per_page));
      $.ajax({
        url: '/webtools2?module=pms&function=getSection&key=' + subtitlemgmt.selected_section.key + '&start=0&size=9999',
        cache: false,
        dataType: 'JSON',
        success: function(data) {
          data.forEach(function(video) {
            subtitlemgmt.selected_section.contents.push(video);
            subtitlemgmt.selected_section.contentstype = 'shows';
          });
          callback('FetchSectionContents:Success');
        },
        error: function(data) {
          data.url = this.url;
          webtools.display_error('Failed fetching the section contents from the server.', data);
          get_show.abort('Error: ' + data.statusText);
        }
      });
    }
  ], function(result) {
    webtools.log(result);
    subtitlemgmt.display_show();
  });
  get_show.start(section_key);

}

subtitlemgmt.fetch_show_seasons = function(show_key, pageToShow) {
  webtools.loading();
  $('#navfoot').html('');
  $('#ContentFoot').html('');
  subtitlemgmt.selected_section.currentpage = Number(pageToShow);
  var get_season = new asynchelper(false, false);
  get_season.inline([
    function(callback, show_key) {
      $('#ContentFoot').html('');
      if (Number(show_key) == 'NaN') {
        get_season.abort('Incorrect section key provided. Needs to be number.');
      }

      showfound = false;
      subtitlemgmt.selected_section.contents.forEach(function(content) {
        if (content.key == show_key) {
          showfound = true;
          subtitlemgmt.selected_section.parents_key.push(subtitlemgmt.selected_section.key);
          subtitlemgmt.selected_section.parents_title.push(subtitlemgmt.selected_section.title);

          subtitlemgmt.selected_section.key = show_key;
          subtitlemgmt.selected_section.title = content.title;
        }
      });

      if (showfound == false) {
        for (var pk = 0; pk < subtitlemgmt.selected_section.parents_key.length; pk++) {

          if (subtitlemgmt.selected_section.parents_key[pk] == show_key) {
            subtitlemgmt.selected_section.key = show_key;
            subtitlemgmt.selected_section.title = subtitlemgmt.selected_section.parents_title[pk];

            subtitlemgmt.selected_section.parents_key.pop();
            subtitlemgmt.selected_section.parents_title.pop();
            break;
          }
        }
      }

      subtitlemgmt.selected_section.contents = [];
      webtools.log('Success: Set a new Current Section. Current section is now: ' + subtitlemgmt.selected_section.title)
      callback('SetCurrentSection:Success');
    },
    function(callback) {
      webtools.loading('Fetching seasons.');
      $.ajax({
        url: '/webtools2?module=pms&function=tvShow&action=getSeasons&key=' + subtitlemgmt.selected_section.key,
        cache: false,
        dataType: 'JSON',
        success: function(data) {
          //console.log('Data:' + (fetchinfo.currentfetch-1) + ' :: ' + JSON.stringify(data));
          data.forEach(function(video) {
            video.title = 'Season ' + video.season;
            subtitlemgmt.selected_section.contents.push(video);
            subtitlemgmt.selected_section.contentstype = 'seasons';

          });
          callback('Batchfetch complete.');
        },
        error: function(data) {
          data.url = this.url;
          webtools.display_error('Failed fetching the seasons from the server.', data);
          get_season.abort('Error: ' + data.statusText);
        }
      });
    }
  ], function() {
    subtitlemgmt.display_season();
  });
  get_season.start(show_key);

}

subtitlemgmt.fetch_season_episodes = function(season_key, pageToShow) {
  webtools.loading();
  $('#navfoot').html('');
  $('#ContentFoot').html('');
  subtitlemgmt.selected_section.currentpage = Number(pageToShow);
  var get_episodes = new asynchelper(false, false);
  get_episodes.inline([
    function(callback, season_key) {
      webtools.loading();
      $('#ContentFoot').html('');
      if (Number(season_key) == 'NaN') {
        get_episodes.abort('Incorrect section key provided. Needs to be number.');
      }

      subtitlemgmt.selected_section.contents.forEach(function(content) {
        if (content.key == season_key) {

          subtitlemgmt.selected_section.parents_key.push(subtitlemgmt.selected_section.key);
          subtitlemgmt.selected_section.parents_title.push(subtitlemgmt.selected_section.title);

          subtitlemgmt.selected_section.key = season_key;
          subtitlemgmt.selected_section.title = content.title;

        }
      });
      subtitlemgmt.selected_section.contents = [];
      webtools.log('Success: Set a new Current Section. Current section is now: ' + subtitlemgmt.selected_section.title)
      callback('SetCurrentSection:Success');
    },
    function(callback) {
      webtools.loading('Fetching episodes.');
      $.ajax({
        url: '/webtools2?module=pms&function=tvShow&action=getSeason&key=' + subtitlemgmt.selected_section.key + '&getSubs=True',
        cache: false,
        dataType: 'JSON',
        success: function(data) {
          data.forEach(function(video) {
            //video.title = 'Season ' + video.season;
            subtitlemgmt.selected_section.contents.push(video);
            subtitlemgmt.selected_section.contentstype = 'episodes';

          });
          callback('FetchEpisodes:Success');
        },
        error: function(data) {
          data.url = this.url;
          webtools.display_error('Failed fetching the episodes from the server.', data);
          get_episodes.abort('Error: ' + data.statusText);
        }
      });
    }
  ], function() {
    subtitlemgmt.display_episodes(true);
  });
  get_episodes.start(season_key);
}

subtitlemgmt.display_show = function() {
  window.scrollTo(0, 0);

  webtools.loading('Applying filters and preparing output.');
  $('#ContentHeader').html(subtitlemgmt.selected_section.title);
  subtitlemgmt.calculate_pages();
  $('#ContentBody').html('');
  var newEntry = ['<table class="table table-bordered">']
  subtitlemgmt.selected_section.contents.forEach(function(content) {
    newEntry.push('<tr><td><a class="customlink" onclick="javascript:subtitlemgmt.fetch_show_seasons(' + content.key + ',0)">' + content.title + '</a></td></tr>');
  });
  newEntry.push('</table>');
  $("#ContentBody").append(newEntry.join('\n'));
  $('.modal').modal('hide');
}

subtitlemgmt.display_season = function() {
  window.scrollTo(0, 0);

  webtools.loading('Applying filters and preparing output.');

  $('#ContentHeader').html('<a class="customlink" onclick="javascript:subtitlemgmt.fetch_section_type_show(' + subtitlemgmt.selected_section.parents_key[0] + ',0)">' + subtitlemgmt.selected_section.parents_title[0] + '</a> /' + subtitlemgmt.selected_section.title);
  subtitlemgmt.calculate_pages();

  $('#ContentBody').html('');
  var newEntry = ['<table class="table table-bordered">']
  var end = ((subtitlemgmt.selected_section.currentpage * subtitlemgmt.options.items_per_page) + subtitlemgmt.options.items_per_page);
  if (end > subtitlemgmt.selected_section.contents.length) {
    end = subtitlemgmt.selected_section.contents.length
  }
  for (var i = 0; i < subtitlemgmt.selected_section.contents.length; i++) {
    newEntry.push('<tr><td><a class="customlink" onclick="javascript:subtitlemgmt.fetch_season_episodes(' + subtitlemgmt.selected_section.contents[i].key + ',0)">' + subtitlemgmt.selected_section.contents[i].title + '</a></td><td>Episodes in season: ' + subtitlemgmt.selected_section.contents[i].size + '</td></tr>');

  }
  newEntry.push('</table>');
  $("#ContentBody").append(newEntry.join('\n'));
  $('.modal').modal('hide');
}