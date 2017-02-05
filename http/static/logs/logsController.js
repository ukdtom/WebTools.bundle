angular.module('webtools').controller('logsController', ['$scope', 'logsModel', 'logsService', 'webtoolsModel', '$window', function ($scope, logsModel, logsService, webtoolsModel, $window) {
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
        $window.location.href = '/webtools2?module=logs&function=download';
    }

    $scope.downloadLog = function () {
        $window.location.href = '/webtools2?module=logs&function=download&fileName=' + logsModel.selectedLog.value;
    }

    $scope.isDanger = function (detail) {
        var detailLower = detail.toLowerCase();
        return detailLower.indexOf('critical') !== -1 || detailLower.indexOf('exception') !== -1 || detailLower.indexOf('error') !== -1;
    }

    $scope.init();
}]);