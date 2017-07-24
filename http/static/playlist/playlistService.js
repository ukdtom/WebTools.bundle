angular.module('webtools').service('playlistService', ['$http', 'playlistModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', function ($http, playlistModel, webtoolsModel, webtoolsService, DialogFactory) {

    this.getSOMETHING = function (callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlist/SOMETHING";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {

            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.getSOMETHING - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }


}]);