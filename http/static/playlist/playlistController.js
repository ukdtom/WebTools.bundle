angular.module('webtools').controller('playlistController', ['$scope', 'playlistModel', 'playlistService', function ($scope, playlistModel, playlistService) {
    $scope.playlistModel = playlistModel;
}]);