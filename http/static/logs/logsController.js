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
        $window.location.href = webtoolsModel.apiV3Url + '/logs/download';
    }
    $scope.downloadLog = function () {
        $window.location.href = webtoolsModel.apiV3Url + '/logs/download/' + $scope.logsModel.selectedLog.value;
    }

    $scope.searchKeyword = function () {

    }
    $scope.searchPrevious = function () {

    }
    $scope.searchNext = function () {

    }
    $scope.searchJumpToTop = function () {

    }

    $scope.$on("$destroy", function () {
        $scope.logsModel.selectedLog = null;
    });

    $scope.init();
}]);