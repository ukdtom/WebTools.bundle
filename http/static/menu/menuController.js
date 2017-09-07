angular.module('webtools').controller('menuController', ['$scope', 'menuModel', 'menuService', 'webtoolsModel', '$location', function ($scope, menuModel, menuService, webtoolsModel, $location) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.menuModel = menuModel;

    $scope.path = $location.path();

    $scope.init = function () {
    }

    $scope.navigateTo = function (path) {
        menuService.navigateTo(path);
        $scope.path = $location.path();
    }
    $scope.redirectTo = function (url, isTargetBlank) {
        menuService.redirectTo(url, isTargetBlank);
    }
    $scope.upgradeWT = function() {
        
    }

    $scope.init();
}]);