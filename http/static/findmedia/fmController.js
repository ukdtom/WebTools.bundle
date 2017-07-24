angular.module('webtools').controller('fmController', ['$scope', 'fmModel', 'fmService', '$interval', 'gettextCatalog', function ($scope, fmModel, fmService, $interval, translate) {
    $scope.fmModel = fmModel;

    var intervalScanner;

    $scope.translate = function () {
        $scope.lang = {
            deleteIgnoredFolder: translate.getString("Delete ignored folder"),
            addIgnoredFolder: translate.getString("Add ignored folder"),
            resetSettings: translate.getString("Reset settings"),
            saveSettings: translate.getString("Save settings"),
            abortScan: translate.getString("Abort scan"),
            downloadResult: translate.getString("Download result"),
            hideShowMenu: translate.getString("Hide/Show settings menu")
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

    $scope.downloadResult = function (section) {
        var filename = "no", text = "";
        filename = (section.title ? section.title : "NoFileName");
        filename = section.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();

        text += "PLEX DATABASE: \r\n";
        for (var i = 0; i < section.result.MissingFromDB.length; i++) {
            var mfdb = section.result.MissingFromDB[i];
            text += mfdb + " \r\n";
        }
        text += "\r\nHARDDRIVE: \r\n";
        for (var x = 0; x < section.result.MissingFromFS.length; x++) {
            var mffs = section.result.MissingFromFS[x];
            text += mffs + " \r\n";
        }

        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    $scope.init();
}]);