angular.module('webtools').controller('logsController', ['$scope', 'logsModel', 'logsService', 'webtoolsModel', function ($scope, logsModel, logsService, webtoolsModel) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.logsModel = logsModel;

    $scope.init = function () {
        logsService.getLogs(function (defaultSelectedLog) {
            $scope.loadLog(defaultSelectedLog);
        });
    }

    $scope.loadLog = function (selectedLog) {
        logsModel.detailsLimit = 500;
        logsService.getLogDetails(selectedLog);
    }

    $scope.increaseLimit = function () {
        logsModel.detailsLimit += 100;
    }

    $scope.downloadLogs = function () {
    }

    $scope.downloadLog = function () {
    }

    $scope.init();
}]);