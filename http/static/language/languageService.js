angular.module('webtools').service('languageService', ['$http', 'languageModel', 'webtoolsModel', 'webtoolsService', function ($http, languageModel, webtoolsModel, webtoolsService) {

    this.getLanguages = function (callback) {
        var url = webtoolsModel.apiV3Url + "/language/getCountryCodes";
        webtoolsModel.languageLoading++;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.languageLoading--;
        }, function (errorResp) {
            self.log("languageService.getLanguages - " + self.formatError(errorResp), "Language", true, url);
            webtoolsModel.languageLoading--;
        });
    }
}]);