angular.module('webtools').controller('contentController', ['$scope', 'menuModel', function ($scope, menuModel) {
    $scope.menuModel = menuModel;
}]);