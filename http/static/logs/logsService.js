angular.module('webtools').service('logsService', ['$http', 'logsModel', 'webtoolsService', 'webtoolsModel', 'gettextCatalog', function ($http, logsModel, webtoolsService, webtoolsModel, translate) {
    this.getLogs = function (callback) {

        var url = webtoolsModel.apiV3Url + "/logs/list/"; //V3
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if (!resp.data || resp.data.length < 1) return;
            logsModel.logs = [];
            for (var i = 0; i < resp.data.length; i++) {
                var log = {
                    id: i + 1,
                    value: resp.data[i]
                };
                logsModel.logs.push(log);
            }
            logsModel.selectedLog = logsModel.logs[0];

            if (callback) callback(logsModel.selectedLog);
        }, function (errorResp) {
            webtoolsService.log("logsService.getLogs - " + webtoolsService.formatError(errorResp), "Logs", true, url);
        });
    }

    this.getLogDetails = function (selectedLog, callback) {
        webtoolsModel.logsLoading = true;

        var url = webtoolsModel.apiV3Url + "/logs/show/" + selectedLog.value; //V3
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            selectedLog.details = resp.data;
            selectedLog.big = false;
            var logLength = selectedLog.details.length;
            var cutLength = 14998;
            if (logLength > cutLength) {
                selectedLog.details.splice(cutLength, logLength - cutLength);
                var warningMsg = translate.getString(" ---------- MORE LINES AVAILABLE IN THE ORIGINAL FILE! If you want to view the rest of the file go download it ---------- ");
                selectedLog.details.push(warningMsg);
                selectedLog.details.push(warningMsg);
                selectedLog.details.push(warningMsg);
                selectedLog.big = true;
            }
            if(callback) callback(resp.data)
            webtoolsModel.logsLoading = false;
        }, function (errorResp) {
            webtoolsService.log("logsService.getLogDetails - " + webtoolsService.formatError(errorResp), "Logs", true, url);
            webtoolsModel.logsLoading = false;
        });
    }
}]);