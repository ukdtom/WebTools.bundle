angular.module('webtools').controller('languageController', ['$scope', 'languageModel', 'languageService', 'webtoolsModel', function ($scope, languageModel, languageService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.languageModel = languageModel;

    $scope.init = function () {
        languageService.getLanguages();
    }

    $scope.changeLang = function (lang) {
        $scope.webtoolsModel.UILanguage = lang;
        languageService.saveLanguage(lang);
    }

    $scope.init();
}]);