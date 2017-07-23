angular.module('webtools').controller('fmController', ['$scope', 'fmModel', 'fmService', '$interval', function ($scope, fmModel, fmService, $interval) {
    $scope.fmModel = fmModel;

    var intervalScanner;

    $scope.init = function () {
        fmService.getSettings();
        fmService.getSectionsList();

        $scope.scanStatus();
    }

    $scope.resetSettings = function () {
        fmService.resetSettings();
    }
    $scope.saveSettings = function () {
        fmService.setSettings();
    }

    $scope.scanStart = function (section) {
        fmModel.selectedSection = section;
        fmService.scanSection(fmModel.selectedSection.key);
    }

    $scope.scanStatus = function () {
        intervalScanner = $interval(function () {
            fmService.getStatus(function () {
                if (!fmModel.scanning) {
                    $interval.cancel(intervalScanner);
                }
            });
        }, 100);
    }

    $scope.scanResult = function () {
        fmService.getResult();
    }

    $scope.scanStop = function () {
        $interval.cancel(intervalScanner);
        fmService.abort();
    }

    $scope.init();
}]);