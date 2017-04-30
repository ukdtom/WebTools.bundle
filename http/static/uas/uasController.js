angular.module('webtools').controller('uasController', ['$scope', 'uasModel', 'uasService', function ($scope, uasModel, uasService) {
    $scope.uasModel = uasModel;

    uasService.getListBundle();
}]);