angular.module('webtools').controller('menuController', ['$scope', 'menuModel', 'menuService', 'webtoolsModel', function ($scope, menuModel, menuService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.menuModel = menuModel;

    $scope.init = function () {
    }

    $scope.navigateTo = function (path) {
        menuService.navigateTo(path);
    }
    $scope.redirectTo = function (url, isTargetBlank) {
        menuService.redirectTo(url, isTargetBlank);
    }
    $scope.upgradeWT = function() {
        
    }

    $scope.init();
}]);