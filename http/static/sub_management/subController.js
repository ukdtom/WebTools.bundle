angular.module('webtools').controller('menuController', ['$scope', 'menuModel', 'menuService', function ($scope, menuModel, menuService) {
    $scope.menuModel = menuModel;

    $scope.navigateTo = function (path) {
        menuService.navigateTo(path);
    }
}]);