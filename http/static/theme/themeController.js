angular.module('webtools').controller('themeController', ['$scope', 'themeModel', 'themeService', function ($scope, themeModel, themeService) {
    $scope.themeModel = themeModel;

    themeService.getThemes();

    $scope.selectTheme = function (theme) {
        $scope.themeModel.activeTheme = theme;
        themeService.saveTheme(theme);
    }
}]);