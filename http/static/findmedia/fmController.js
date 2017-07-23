angular.module('webtools').controller('fmController', ['$scope', 'fmModel', 'fmService', function ($scope, fmModel, fmService) {
    $scope.fmModel = fmModel;

    fmService.getSettings();
    fmService.getSectionsList();

    $scope.resetSettings = function () {
        fmService.resetSettings();
    }
    $scope.saveSettings = function () {
        fmService.setSettings();
    }

    $scope.scanStart = function () {

    }

    $scope.scanStatus = function () {

    }

    $scope.scanResult = function () {

    }

    $scope.scanStop = function () {

    }
}]);