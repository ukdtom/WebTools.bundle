angular.module('webtools').controller('uasController', ['$scope', 'uasModel', 'uasService', 'webtoolsModel', function ($scope, uasModel, uasService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.uasModel = uasModel;

    $scope.init = function () {
        uasService.getTypes();
        uasService.getListBundle(function () {
            uasService.getInstalled();
        });
    }

    $scope.setType = function (typeName, type) {
        type.name = typeName;
        $scope.uasModel.selectedType = type;
    }

    $scope.typeExist = function (itemTypes) {
        for(var i = 0;i < itemTypes.length;i++){
            if (uasModel.selectedType.name === itemTypes[i]) return true;
        }
        return false;
    }

    $scope.installUpdate = function (repo) {

    }

    $scope.init();
}]);