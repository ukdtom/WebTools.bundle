angular.module('webtools').controller('homeController', ['$scope', 'webtoolsModel', function ($scope, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
}]);