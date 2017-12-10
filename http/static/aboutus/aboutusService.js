angular.module('webtools').service('aboutusService', ['$http', 'aboutusModel', 'webtoolsModel', function ($http, aboutusModel, webtoolsModel) {
    this.getTranslators = function (callback) {
        var url = webtoolsModel.apiV3Url + "/wt/getTranslatorList";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if (resp.data) aboutusModel.translators = resp.data;
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("aboutusService.getTranslators - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "Aboutus", true, url);
        });
    }
}]);