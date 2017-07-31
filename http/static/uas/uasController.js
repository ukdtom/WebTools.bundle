angular.module('webtools').controller('uasController', ['$scope', 'uasModel', 'uasService', 'webtoolsModel', function ($scope, uasModel, uasService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.uasModel = uasModel;

    $scope.manualRepo = {};

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

    $scope.typeExist = function (selectedTypeName, itemTypes) {
        if (selectedTypeName === "All") return true;
        for (var i = 0; i < itemTypes.length; i++) {
            if (selectedTypeName === itemTypes[i]) return true;
        }
        return false;
    }

    $scope.installUpdate = function (repo, repoUrl, reinit) {
        repo.url = repoUrl;

        if (reinit) uasService.installUpdate(repo, $scope.init);
        else uasService.installUpdate(repo);
    }


    $scope.delete = function (repo, repoUrl) {
        repo.url = repoUrl;
        uasService.delete(repo);
    }

    $scope.migrate = function () {
        uasService.migrate($scope.init);
    }

    $scope.forceCache = function () {
        uasService.forceCache(true, $scope.init);
    }

    $scope.checkBundleUpdates = function () {
        uasService.getUpdateList();
    }

    $scope.updateAllBundles = function () {
        for (var i = 0; i < uasModel.updateList.length; i++) {
            var item = uasModel.list[uasModel.updateList[i].key];
            $scope.installUpdate(item, item.key);
        }
    }

    //Validation helper
    $scope.validUrl = function (url) {
        return url.indexOf("http") !== -1;
    }

    //Init
    if (localStorage.uasUpdated) {
        $scope.init();
    } else {
        uasService.forceCache(false, function () {
            localStorage.uasUpdated = true;
            $scope.init();
        });
    }
}]);