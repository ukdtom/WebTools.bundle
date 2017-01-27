angular.module('webtools').controller('logsController', ['$scope', 'logsModel', 'logsService', function ($scope, logsModel, logsService) {
    $scope.logsModel = logsModel;
}]);