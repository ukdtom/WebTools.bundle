angular.module('webtools').controller('webtoolsController', ['$scope', 'menuModel', 'themeModel', function ($scope, menuModel, themeModel) {
    $scope.webtoolsThemeModel = themeModel;
    $scope.webtoolsMenuModel = menuModel;
}]);