angular.module('webtools').controller('headController', ['$scope', 'headModel', 'headService', 'webtoolsModel', function ($scope, headModel, headService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.headModel = headModel;
}]);