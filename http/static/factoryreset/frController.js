angular.module('webtools').controller('frController', ['$scope', 'frModel', 'frService', function ($scope, frModel, frService) {
    $scope.frModel = frModel;
    
    $scope.factoryReset = function () {
        frService.factoryReset();
    }
}]);