angular.module('webtools').service('subService', ['$http', 'subModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', function ($http, subModel, webtoolsModel, webtoolsService, DialogFactory) {
    this.getShows = function (callback) {
        webtoolsModel.subLoading = true;
        $http({
            method: "GET",
            url: webtoolsModel.apiUrl + "?module=pms&function=getSectionsList",
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
            webtoolsService.log("subService.getShows - Sections could not be loaded!", "Sub", true);
            webtoolsModel.subLoading = false;
        });
    }

    this.getShowDetails = function (show, callback) {
        show.loading = true;
        $http({
            method: "GET",
            url: webtoolsModel.apiUrl + "?module=pms&function=getSection&key=" + show.key + "&start=0&size=20&getSubs=true",
        }).then(function (resp) {
            show.details = resp.data;
            if (callback) callback(resp.data);
            show.loading = false;
        }, function (errorResp) {
            debugger;
            webtoolsService.log("subService.getShowDetails - Show details could not be loaded!", "Sub", true);
            show.loading = false;
        });
    }

    this.deleteSubtitle = function (detail, subtitle, callback) {
        detail.loading = true;
        subModel.deleteCountAsyncRunning++;
        $http({
            method: "DELETE",
            url: webtoolsModel.apiUrl + "?module=pms&function=delSub&key=" + detail.key + "&subKey=" + subtitle.key,
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
                webtoolsService.log("subService.deleteSubtitle", "Sub", true);
            }
            subModel.deleteCountAsyncRunning--;
            if (subModel.deleteCountAsyncRunning === 0) detail.loading = false;
        });
    }
}]);