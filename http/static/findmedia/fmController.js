angular.module('webtools').controller('fmController', ['$scope', 'fmModel', 'fmService', '$interval', 'gettextCatalog', function ($scope, fmModel, fmService, $interval, translate) {
    $scope.fmModel = fmModel;

    var intervalScanner;

    $scope.translate = function () {
        $scope.lang = {
            deleteIgnoredFolder: translate.getString("Delete ignored folder"),
            addIgnoredFolder: translate.getString("Add ignored folder"),
            resetSettings: translate.getString("Reset settings"),
            saveSettings: translate.getString("Save settings"),
            abortScan: translate.getString("Abort scan")
        };
    }
    
    $scope.init = function () {
        fmService.getSettings();
        fmService.getSectionsList();

        $scope.translate();
        $scope.scanStatus();
    }

    $scope.resetSettings = function () {
        fmService.resetSettings();
    }
    $scope.saveSettings = function () {
        fmService.setSettings();
    }

    $scope.scanStart = function (section) {
        if (section.result) {
            section.result = null;
            return;
        }

        fmModel.selectedSection = section;
        fmService.scanSection(fmModel.selectedSection.key);

        $scope.scanStatus();
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