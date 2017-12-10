angular.module('webtools').controller('infoController', ['$scope', 'infoModel', 'infoService', 'webtoolsModel', function ($scope, infoModel, infoService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.infoModel = infoModel;

    $scope.init = function () {
        infoService.getInfo();
    }

    $scope.init();
}]);