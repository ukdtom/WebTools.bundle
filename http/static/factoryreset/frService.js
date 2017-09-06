angular.module('webtools').service('frService', ['$http', 'webtoolsModel', 'webtoolsService', 'frModel', '$interval', '$window', function ($http, webtoolsModel, webtoolsService, frModel, $interval, $window) {
    this.factoryReset = function (callback) {
        webtoolsModel.globalLoading++;
        var url = webtoolsModel.apiV3Url + "/wt/reset";
        $http({
            method: "PUT",
            url: url,
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsModel.globalLoading--;
            webtoolsService.log("frService.factoryReset - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "FactoryReset", true, url);
        });

        $interval(function () {
            $http({
                method: "GET",
                url: "/",
            }).then(function (resp) {
                webtoolsModel.globalLoading--;
                $window.location.reload(true);
            }, function (errorResp) {
            });
        }, 5000);
    };
}]);