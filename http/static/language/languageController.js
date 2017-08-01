angular.module('webtools').controller('languageController', ['$scope', 'languageModel', 'languageService', 'webtoolsModel', '$window', function ($scope, languageModel, languageService, webtoolsModel, $window) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.languageModel = languageModel;

    $scope.init = function () {
        languageService.getLanguages();
    }

    $scope.changeLang = function () {
        languageService.saveLanguage($scope.webtoolsModel.UILanguage, function() {
            $window.location.reload(true);
        });
    }

    $scope.init();
}]);