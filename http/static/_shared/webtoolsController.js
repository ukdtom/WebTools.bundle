angular.module('webtools').controller('webtoolsController', ['$scope', 'webtoolsModel', 'menuModel', 'themeModel', 'gettextCatalog', function ($scope, webtoolsModel, menuModel, themeModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.webtoolsThemeModel = themeModel;
    $scope.webtoolsMenuModel = menuModel;
}]);