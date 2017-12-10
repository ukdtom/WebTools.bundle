angular.module('webtools').service('playlistService', ['$http', 'playlistModel', 'webtoolsModel', 'webtoolsService', 'DialogFactory', '$window', function ($http, playlistModel, webtoolsModel, webtoolsService, DialogFactory, $window) {

    this.getPlaylist = function (userId, callback) {
        webtoolsModel.playlistsLoading++;
        var url = webtoolsModel.apiV3Url + "/playlists/List";
        if (userId) {
            url += "/user/" + userId;
        }
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            playlistModel.playlists = [];
            for (var key in resp.data) {
                if (resp.data.hasOwnProperty(key)) {
                    var item = resp.data[key];
                    item.key = key;
                    playlistModel.playlists.push(item);
                }
            }
            if (callback) callback(resp.data);
            webtoolsModel.playlistsLoading--;
        }, function (errorResp) {
            webtoolsService.log("playlistService.getPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistsLoading--;
        });
    }

    this.deletePlaylist = function (playlist, userId, callback) {
        webtoolsModel.playlistsLoading++;
        var url = webtoolsModel.apiV3Url + "/playlists/Delete/key/" + playlist.key;
        if (userId) {
            url += "/user/" + userId;
        }
        $http({
            method: "DELETE",
            url: url
        }).then(function (resp) {
            for (var i = 0; i < playlistModel.playlists.length; i++) {
                if (playlistModel.playlists[i].key === playlist.key) {
                    playlistModel.playlists.splice(i, 1);
                }
            }
            if (callback) callback(resp.data);
            webtoolsModel.playlistsLoading--;
        }, function (errorResp) {
            webtoolsService.log("playlistService.deletePlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistsLoading--;
        });
    }

    this.downloadPlaylist = function (playlist, userId, callback) {
        var url = webtoolsModel.apiV3Url + "/playlists/download/key/" + playlist.key;
        if (userId) {
            url += "/user/" + userId;
        }
        $window.location = url;
        //$http({
        //    method: "GET",
        //    url: url
        //}).then(function (resp) {
        //    debugger;
        //    if (callback) callback(resp.data);
        //    webtoolsModel.playlistsLoading--;
        //}, function (errorResp) {
        //    webtoolsService.log("playlistService.downloadPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
        //    webtoolsModel.playlistsLoading--;
        //});
    }

    this.copyPlaylist = function (playlist, toUserId, userId, callback) {
        webtoolsModel.playlistsLoading++;
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
            webtoolsModel.playlistsLoading--;
        }, function (errorResp) {
            webtoolsService.log("playlistService.copyPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistsLoading--;
        });
    }

    this.importPlaylist = function (file, callback) {
        var data = new FormData();
        data.append("localFile", file);

        webtoolsModel.playlistsLoading++;
        var url = webtoolsModel.apiV3Url + "/playlists/Import";
        $http({
            method: "POST",
            data: data,
            headers: { 'Content-Type': undefined },
            transformRequest: angular.identity,
            url: url
        }).then(function (resp) {
            if (callback) callback(resp.data);
            webtoolsModel.playlistsLoading--;
        }, function (errorResp) {
            webtoolsService.log("playlistService.importPlaylist - " + webtoolsService.formatError(errorResp), "Playlist", true, url);
            webtoolsModel.playlistsLoading--;
        });
    }


}]);