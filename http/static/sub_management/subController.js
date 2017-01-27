angular.module('webtools').controller('subController', ['$scope', 'subModel', 'subService', function ($scope, subModel, subService) {
    $scope.subModel = subModel;
}]);