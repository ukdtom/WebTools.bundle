angular.module('webtools').service('subService', ['$http', 'subModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', '$window', 'gettext', function ($http, subModel, webtoolsModel, webtoolsService, DialogFactory, $window, gettext) {
    var _this = this;

    this.lang = {
        noFilter: gettext("No filter")
    }


    this.setSettings = function (callback) {
        if (!subModel.settings) {
            console.log("No settings!?");
            return;
        }

        var url = webtoolsModel.apiV3Url + "/settings/setSetting";
        $http({
            method: "PUT",
            url: url,
            data: {
                HideWithoutSubs: subModel.settings.hideWithoutSub
            }
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("subService.setSettings - " + webtoolsService.formatError(errorResp), "Sub", true, url);
        });
    }

    this.getSettings = function (callback) {
        var url = webtoolsModel.apiV3Url + "/settings/getSettings/HideWithoutSubs";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if (!subModel.settings) {
                subModel.settings = {}
            }
            subModel.settings.hideWithoutSub = resp.data;

            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("subService.getSettings - " + webtoolsService.formatError(errorResp), "Sub", true, url);
        });
    }


    this.getShows = function (callback) {
        webtoolsModel.subLoading = true;
        var url = webtoolsModel.apiV3Url + "/pms/getSectionsList";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            subModel.shows = [];
            angular.forEach(resp.data, function (media) {
                if (media.type === "movie" || media.type === "show") {
                    media.expanded = false;
                    media.loading = 0;
                    subModel.shows.push(media);
                }
            });
            if (callback) callback(resp.data);
            webtoolsModel.subLoading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.getShows - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            webtoolsModel.subLoading = false;
        });
    }

    this.getSectionLetterList = function (show, callback) {
        show.loading++;
        var url = webtoolsModel.apiV3Url + "/pms/getSectionLetterList/" + show.key;

        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            show.letterOptions = [{
                name: _this.lang.noFilter,
                key: null,
                size: ""
            }];
            show.letter = show.letterOptions[0].key;
            for (var key in resp.data) {
                if (resp.data.hasOwnProperty(key)) {
                    var item = resp.data[key];
                    item.name = key;
                    show.letterOptions.push(item);
                }
            }
            if (callback) callback(resp.data);
            show.loading--;
        }, function (errorResp) {
            webtoolsService.log("subService.getSectionLetterList - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            show.loading--;
        });
    }

    this.getMovieDetails = function (show, callback) {
        var skip = (show.skip ? show.skip : 0);
        var take = 20;

        show.loading++;
        var url = webtoolsModel.apiV3Url + "/pms/getSection/key/" + show.key + "/start/" + skip + "/size/" + take + "/getSubs/title/" + subModel.searchValue;
        if (show.letter) url += "/letterKey/" + show.letter;

        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            show.full = resp.data.count !== take;

            for (var i = 0; i < resp.data.Section.length; i++) {
                show.details.push(resp.data.Section[i]);
            }

            show.skip = skip + resp.data.count;

            if (callback) callback(resp.data);
            show.loading--;
        }, function (errorResp) {
            webtoolsService.log("subService.getMovieDetails - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            show.loading--;
        });
    }

    this.getTvShowDetails = function (show, callback) {
        var skip = (show.skip ? show.skip : 0);
        var take = 30;

        show.loading++;
        var url = webtoolsModel.apiV3Url + "/pms/getSection/key/" + show.key + "/start/" + skip + "/size/" + take + "/title/" + subModel.searchValue;
        if (show.letter) url += "/letterKey/" + show.letter;

        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            show.full = resp.data.count !== take;

            if (!show.tvshows) show.tvshows = [];
            for (var i = 0; i < resp.data.Section.length; i++) {
                show.tvshows.push(resp.data.Section[i]);
            }

            show.skip = skip + resp.data.count;

            if (callback) callback(resp.data);
            show.loading--;
        }, function (errorResp) {
            webtoolsService.log("subService.getTvShowDetails - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            show.loading--;
        });
    }

    this.getTvShowSeasons = function (tvshow, callback) {
        tvshow.loading++;
        var url = webtoolsModel.apiV3Url + "/pms/getShowSeasons/" + tvshow.key;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            tvshow.seasons = resp.data;
            if (callback) callback(resp.data);
            tvshow.loading--;
        }, function (errorResp) {
            webtoolsService.log("subService.getTvShowSeasons - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            tvshow.loading--;
        });
    }

    this.getTvShowSeasonDetails = function (season, callback) {
        season.loading = true;
        var url = webtoolsModel.apiV3Url + "/pms/getShowSeason/" + season.key + "/getSub";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            season.details = resp.data;
            if (callback) callback(resp.data);
            season.loading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.getTvShowSeasonDetails - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            season.loading = false;
        });
    }

    this.getParts = function (detail, callback) {
        var url = webtoolsModel.apiV3Url + "/pms/getParts/" + detail.key;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            var list = [];
            for (var key in resp.data) {
                if (resp.data.hasOwnProperty(key)) {
                    var value = resp.data[key];
                    list.push({
                        id: key,
                        value: value
                    });
                }
            }
            if (callback) callback(list, resp.data);
        }, function (errorResp) {
            webtoolsService.log("subService.getParts - " + webtoolsService.formatError(errorResp), "Sub", true, url);
        });
    }

    this.uploadSub = function (detail, part, file, lang, callback) {
        var data = new FormData();
        data.append("language", lang);
        data.append("localFile", file);

        var url = webtoolsModel.apiV3Url + "/pms/uploadSub/key/" + detail.key + "/part/" + part;
        $http({
            method: "POST",
            data: data,
            headers: { 'Content-Type': undefined },
            transformRequest: angular.identity,
            url: url
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("subService.uploadSub - " + webtoolsService.formatError(errorResp), "Sub", true, url);
        });
        
    }

    this.deleteSubtitle = function (detail, subtitle, callback) {
        detail.loading = true;
        subModel.deleteCountAsyncRunning++;
        var url = webtoolsModel.apiV3Url + "/pms/delSub/key/" + detail.key + "/sub/" + subtitle.key;
        $http({
            method: "DELETE",
            url: url,
        }).then(function (resp) {
            for (var i = 0; i < detail.subtitles.length; i++) {
                if (detail.subtitles[i].key === subtitle.key)
                    detail.subtitles.splice(i, 1);
            }
            if (detail.subtitles.length === 0) detail.subAllChecked = false;

            if (callback) callback(resp.data);
            subModel.deleteCountAsyncRunning--;
            if (subModel.deleteCountAsyncRunning === 0) detail.loading = false;
        }, function (errorResp) {
            if (errorResp.status === 403) {
                if (!subModel.deleteErrorDialogActive){
                    subModel.deleteErrorDialogActive = true;
                    var dialog = new DialogFactory();
                    dialog.create("<p class='textSize3'>WebTools do not have permission to delete these files.</p>"); //TODO: Move to template. Maybe a better description too
                    dialog.setPlain();
                    dialog.closeEvent(function () {
                        subModel.deleteErrorDialogActive = false;
                    });
                    dialog.showError();
                }
            } else {
                webtoolsService.log("subService.deleteSubtitle - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            }
            subModel.deleteCountAsyncRunning--;
            if (subModel.deleteCountAsyncRunning === 0) detail.loading = false;
        });
    }

    this.downloadSubtitle = function (subtitleKey) {
      // $window.location(webtoolsModel.apiV3Url + "/pms/downloadSubtitle/" + subtitleKey);       
        $window.location.href = webtoolsModel.apiV3Url + "/pms/downloadSubtitle/" + subtitleKey;
    }

    this.viewSubtitle = function (subtitleKey, callback) {
        //$window.location.href = webtoolsModel.apiV3Url + "/pms/showSubtitle/" + subtitleKey;
        var url = webtoolsModel.apiV3Url + "/pms/showSubtitle/" + subtitleKey;

        webtoolsModel.subLoading = true;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            subModel.selectedSub = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.subLoading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.viewSubtitle - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            webtoolsModel.subLoading = false;
        });
    }


}]);