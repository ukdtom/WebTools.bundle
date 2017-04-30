angular.module('webtools').controller('uasController', ['$scope', 'uasModel', 'uasService', 'webtoolsModel', function ($scope, uasModel, uasService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.uasModel = uasModel;

    uasService.getTypes();
}]);