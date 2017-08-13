angular.module('webtools').controller('frController', ['$scope', 'frModel', 'frService', '$interval', function ($scope, frModel, frService, $interval) {
    $scope.frModel = frModel;
    
    $scope.init = function () {        
    }

    $scope.factoryReset = function () {
        frService.factoryReset();
    }

    $scope.init();
}]);