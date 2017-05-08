angular.module('webtools').controller('uasController', ['$scope', 'uasModel', 'uasService', 'webtoolsModel', function ($scope, uasModel, uasService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.uasModel = uasModel;

    $scope.init = function () {
        uasService.getTypes(function (data) {
            if (data["Metadata Agent"]) $scope.setType("Metadata Agent", data["Metadata Agent"]);

            uasService.getListBundle(function () {
                uasService.getInstalled();
            });
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

    $scope.installUpdate = function (repo, repoUrl) {
        repo.url = repoUrl;
        uasService.installUpdate(repo);
    }

    $scope.delete = function (repo, repoUrl) {
        repo.url = repoUrl;
        uasService.delete(repo);
    }

    $scope.migrate = function () {
        uasService.migrate($scope.init);
    }

    $scope.forceUAScache = function () {
        uasService.updateUASCache(true, $scope.init);
    }

    uasService.updateUASCache(false, function () {
        $scope.init();
    });
}]);