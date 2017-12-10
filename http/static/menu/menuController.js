angular.module('webtools').controller('menuController', ['$scope', 'menuModel', 'menuService', 'webtoolsModel', 'webtoolsService', '$location', function ($scope, menuModel, menuService, webtoolsModel, webtoolsService, $location) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.menuModel = menuModel;

    $scope.path = $location.path();

    $scope.init = function () {
        webtoolsModel.isNewVersionAvailable = localStorage.isNewVersionAvailable;
    }

    $scope.navigateTo = function (path) {
        menuService.navigateTo(path);
        $scope.path = $location.path();
    }
    $scope.redirectTo = function (url, isTargetBlank) {
        menuService.redirectTo(url, isTargetBlank);
    }
    $scope.upgradeWT = function() {
        webtoolsService.upgradeWT();
    }

    $scope.init();
}]);