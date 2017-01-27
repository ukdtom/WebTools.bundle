angular.module('webtools').controller('headController', ['$scope', 'headModel', 'headService', function ($scope, headModel, headService) {
    $scope.headModel = headModel;

    $scope.init = function () {
        headService.initWebToolsVersion();
    }

    $scope.init();
}]);