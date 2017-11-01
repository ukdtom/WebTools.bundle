angular.module('webtools').service('infoService', ['$http', 'infoModel', 'webtoolsModel', function ($http, infoModel, webtoolsModel) {
    this.getInfo = function (callback) {
        var url = webtoolsModel.apiV3Url + "/techinfo/getInfo";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            var list = [];
            for (var key in resp.data) {
                var item =
                    {
                        key: key,
                        value: resp.data[key]
                    };
                list.push(item);
            }
            infoModel.informations = list;
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("infoService.getInfo - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "Info", true, url);
        });
    }
}]);