angular.module('webtools').controller('playlistController', ['$scope', 'playlistModel', 'playlistService', 'webtoolsService', 'webtoolsModel', function ($scope, playlistModel, playlistService, webtoolsService, webtoolsModel) {
    $scope.playlistModel = playlistModel;

    $scope.init = function () {
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
        playlistService.copyPlaylist(playlist, webtoolsModel.userToSelected, webtoolsModel.userSelected); //TODO
    }

    $scope.importPlaylist = function (file) {
        playlistService.importPlaylist(file); //TODO
    }

    $scope.init();
}]);