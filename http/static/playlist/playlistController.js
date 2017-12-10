angular.module('webtools').controller('playlistController', ['$scope', 'playlistModel', 'playlistService', 'webtoolsService', 'webtoolsModel', 'gettext', function ($scope, playlistModel, playlistService, webtoolsService, webtoolsModel, gettext) {
    $scope.playlistModel = playlistModel;

    $scope.translate = function () {
        var lang = {
            confirmDeleteQuestion: gettext("Are you sure you want to delete the playlist?"),
            confirmDelete: gettext("Delete")
        };
        $scope.lang = lang;
    }

    $scope.init = function () {
        $scope.translate();
        webtoolsService.loadUsers();
        playlistService.getPlaylist();
    }

    $scope.changeUserSelected = function () {
        playlistService.getPlaylist(webtoolsModel.userSelected);
    }

    $scope.deletePlaylist = function(playlist) {
        playlistService.deletePlaylist(playlist, webtoolsModel.userSelected);
    }
    
    $scope.downloadPlaylist = function (playlist) {
        playlistService.downloadPlaylist(playlist, webtoolsModel.userSelected);
    }

    $scope.copyPlaylist = function (playlist) {
        playlistService.copyPlaylist(playlist, webtoolsModel.userToSelected, webtoolsModel.userSelected);
    }

    $scope.importPlaylist = function (file) {
        playlistService.importPlaylist(file, function () {
            $scope.init();
        });
    }

    $scope.init();
}]);