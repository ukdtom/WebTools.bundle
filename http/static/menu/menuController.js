angular.module('webtools').controller('menuController', ['$scope', 'menuModel', 'menuService', function ($scope, menuModel, menuService) {
    $scope.menuModel = menuModel;

    $scope.init = function () {
    }

    $scope.navigateTo = function (path) {
        menuService.navigateTo(path);
    }
    $scope.logout = function () {
        menuService.logout();
    }

    $scope.init();
}]);