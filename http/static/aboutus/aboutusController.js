angular.module('webtools').controller('aboutusController', ['$scope', 'aboutusModel', 'aboutusService', 'webtoolsModel', function ($scope, aboutusModel, aboutusService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.aboutusModel = aboutusModel;

    $scope.init = function () {
        aboutusService.getTranslators();
    }

    $scope.init();
}]);