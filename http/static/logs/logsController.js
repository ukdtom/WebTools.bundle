angular.module('webtools').controller('logsController', ['$scope', 'logsModel', 'logsService', 'webtoolsModel', '$window', 'gettext', function ($scope, logsModel, logsService, webtoolsModel, $window, gettext) {
    $scope.webtoolsModel = webtoolsModel;
    $scope.logsModel = logsModel;

    $scope.translate = function () {
        var lang = {
            searchPlaceholder: gettext("search..."),
            searchKeyword: gettext("Search keyword"),
            clearSearch: gettext("Clear search"),
            previous: gettext("Previous"),
            next: gettext("Next"),
            jumpToTop: gettext("Jump to top"),
            hideShowMenu: gettext("Hide/Show search menu")
        };
        $scope.lang = lang;
    }

    $scope.init = function () {
        logsService.getLogs(function (defaultSelectedLog) {
            $scope.loadLog(defaultSelectedLog);
        });
        $scope.translate();
    }

    $scope.loadLog = function (selectedLog) {
        $scope.logsModel.searchKeywordValue = "";
        $scope.logsModel.searchKeywordValueLast = "";
        $scope.logsModel.searchFoundLine = [];
        logsService.getLogDetails(selectedLog);
    }

    $scope.downloadLogs = function () {
        $window.location.href = webtoolsModel.apiV3Url + '/logs/download';
    }
    $scope.downloadLog = function () {
        $window.location.href = webtoolsModel.apiV3Url + '/logs/download/' + $scope.logsModel.selectedLog.value;
    }

    $scope.searchKeyword = function () {
        if ($scope.logsModel.searchKeywordValue && $scope.logsModel.searchKeywordValue === $scope.logsModel.searchKeywordValueLast) {
            if ($scope.logsModel.searchFoundLines.length > 0) $scope.$broadcast("logs_search_nextLine");
        }
        else {
            $scope.$broadcast("logs_search_findKeywords");
        }
    }
    $scope.searchClear = function () {
        $scope.logsModel.searchKeywordValue = "";
        $scope.$broadcast("logs_search_findKeywords");
    }
    $scope.searchPrevious = function () {
        if ($scope.logsModel.searchFoundLines.length > 0) $scope.$broadcast("logs_search_previousLine");
    }
    $scope.searchJumpToTop = function () {
        $scope.$broadcast("logs_search_jumpToTop");
    }

    $scope.previousFile = function () {
        if (!logsModel.selectedLog) {
            console.log("No selected log?");
            return;
        }
        var available = false;
        for (var i = logsModel.logs.length - 1; i > 0; i--) {
            var log = logsModel.logs[i];
            if (log.id === logsModel.selectedLog.id) {
                logsModel.selectedLog = logsModel.logs[i - 1];
                available = true;
                break;
            }
        }
        if (!available) logsModel.selectedLog = logsModel.logs[logsModel.logs.length - 1];
        $scope.loadLog(logsModel.selectedLog);
    }
    $scope.reloadFile = function () {
        $scope.loadLog(logsModel.selectedLog);
    }
    $scope.nextFile = function () {
        if (!logsModel.selectedLog) {
            console.log("No selected log?");
            return;
        }
        var available = false;
        for (var i = 0; i < logsModel.logs.length - 1; i++) {
            var log = logsModel.logs[i];
            if (log.id === logsModel.selectedLog.id) {
                logsModel.selectedLog = logsModel.logs[i + 1];
                available = true;
                break;
            }
        }
        if(!available) logsModel.selectedLog = logsModel.logs[0];
        $scope.loadLog(logsModel.selectedLog);
    }

    $scope.$on("$destroy", function () {
        logsModel.selectedLog = null;
    });

    $scope.init();
}]);