angular.module('webtools').controller('themeController', ['$scope', 'themeModel', 'themeService', 'webtoolsModel', function ($scope, themeModel, themeService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.themeModel = themeModel;

    themeService.getThemes();

    $scope.selectTheme = function (theme) {
        $scope.themeModel.activeTheme = theme;
        themeService.saveTheme(theme);
    }
}]);