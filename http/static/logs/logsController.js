angular.module('webtools').controller('logsController', ['$scope', 'logsModel', 'logsService', 'webtoolsModel', '$window', function ($scope, logsModel, logsService, webtoolsModel, $window) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.logsModel = logsModel;

    $scope.init = function () {
        logsService.getLogs(function (defaultSelectedLog) {
            $scope.loadLog(defaultSelectedLog);
        });
    }

    $scope.loadLog = function (selectedLog) {
        logsService.getLogDetails(selectedLog);
    }

    $scope.downloadLogs = function () {
        $window.location.href = '/webtools2?module=logs&function=download';
    }

    $scope.downloadLog = function () {
        $window.location.href = '/webtools2?module=logs&function=download&fileName=' + logsModel.selectedLog.value;
    }

    $scope.$on("$destroy", function () {
        $scope.logsModel.selectedLog = null;
    });

    $scope.init();
}]);