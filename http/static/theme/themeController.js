angular.module('webtools').controller('themeController', ['$scope', 'themeModel', 'themeService', function ($scope, themeModel, themeService) {
    $scope.themeModel = themeModel;

    themeService.getThemes();
}]);