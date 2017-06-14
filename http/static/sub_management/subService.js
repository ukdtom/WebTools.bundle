angular.module('webtools').service('subService', ['$http', 'subModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', '$window', function ($http, subModel, webtoolsModel, webtoolsService, DialogFactory, $window) {
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
                    media.loading = false;
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

    this.getMovieDetails = function (show, callback) {
        var skip = (show.skip ? show.skip : 0);
        var take = 20;

        show.loading = true;
        var url = webtoolsModel.apiV3Url + "/pms/getSection/key/" + show.key + "/start/" + skip + "/size/" + take + "/getSubs/title/" + subModel.searchValue;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if (resp.data.length !== take) show.full = true;

            for (var i = 0; i < resp.data.length; i++) {
                show.details.push(resp.data[i]);
            }
            show.skip = show.details.length;

            if (callback) callback(resp.data);
            show.loading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.getMovieDetails - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            show.loading = false;
        });
    }

    this.getTvShowDetails = function (show, callback) {
        show.loading = true;
        var url = webtoolsModel.apiV3Url + "/pms/getSection/key/" + show.key + "/start/0/size/9999/title/" + subModel.searchValue;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            show.tvshows = resp.data;
            if (callback) callback(resp.data);
            show.loading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.getTvShowDetails - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            show.loading = false;
        });
    }

    this.getTvShowSeasons = function (tvshow, callback) {
        tvshow.loading = true;
        var url = webtoolsModel.apiV3Url + "/pms/getShowSeasons/" + tvshow.key;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            tvshow.seasons = resp.data;
            if (callback) callback(resp.data);
            tvshow.loading = false;
        }, function (errorResp) {
            webtoolsService.log("subService.getTvShowSeasons - " + webtoolsService.formatError(errorResp), "Sub", true, url);
            tvshow.loading = false;
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

    this.uploadFile = function (detail, file) {
        var url = webtoolsModel.apiV3Url + "/pms/uploadFile/key/" + detail.key;
        $http({
            method: "POST",
            data: {
                localFile: file
            },
            url: url,
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("subService.uploadFile - " + webtoolsService.formatError(errorResp), "Sub", true, url);
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
                    detail.subtitles.splice(detail.subtitles[i].indexOf, 1);
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
        $window.open(webtoolsModel.apiV3Url + "/pms/downloadSubtitle/" + subtitleKey, "_blank");
    }

    this.viewSubtitle = function (subtitleKey) {
        $window.open(webtoolsModel.apiV3Url + "/pms/showSubtitle/" + subtitleKey, "_blank");
    }


}]);