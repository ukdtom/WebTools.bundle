angular.module('webtools').service('playlistService', ['$http', 'playlistModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', function ($http, playlistModel, webtoolsModel, webtoolsService, DialogFactory) {

    this.getPlaylist = function (userId, callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlists/List";
        if (userId) {
            url += "/user/" + userId;
        }
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            playlistModel.playlist = resp.data;
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.getPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }

    this.deletePlaylist = function (playlist, userId, callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlists/Delete/key/" + playlist.key;
        if (userId) {
            url += "/user/" + userId;
        }
        $http({
            method: "DELETE",
            url: url
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.deletePlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }

    this.downloadPlaylist = function (playlist, userId, callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlists/download/key/" + playlist.key;
        if (userId) {
            url += "/user/" + userId;
        }
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.downloadPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }

    this.copyPlaylist = function (playlist, toUserId, userId, callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlists/Copy/key/" + playlist.key + "/UserTo/" + toUserId;
        if (userId) {
            url += "/UserFrom/" + userId;
        }
        $http({
            method: "POST",
            url: url
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.copyPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }

    this.importPlaylist = function (file, callback) {
        webtoolsModel.playlistLoading = true;
        var url = webtoolsModel.apiV3Url + "/playlists/Import";
        $http({
            method: "POST",
            data: {
                localFile: file
            },
            url: url
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.playlistLoading = false;
        }, function (errorResp) {
            webtoolsService.log("playlistService.importPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistLoading = false;
        });
    }


}]);