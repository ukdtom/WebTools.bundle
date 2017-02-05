angular.module('webtools').service('logsService', ['$http', 'logsModel', 'webtoolsService', 'webtoolsModel', function ($http, logsModel, webtoolsService, webtoolsModel) {
    this.getLogs = function (callback) {

        var url = webtoolsModel.apiUrl + "?module=logs&function=list";
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

        var url = webtoolsModel.apiUrl + "?module=logs&function=show&fileName=" + selectedLog.value;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            selectedLog.details = resp.data;
            if(callback) callback(resp.data)
            webtoolsModel.logsLoading = false;
        }, function (errorResp) {
            webtoolsService.log("logsService.getLogDetails - " + webtoolsService.formatError(errorResp), "Logs", true, url);
            webtoolsModel.logsLoading = false;
        });
    }

    this.downloadLogs = function () {

    }
}]);