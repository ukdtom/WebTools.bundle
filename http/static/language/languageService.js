angular.module('webtools').service('languageService', ['$http', 'languageModel', 'webtoolsModel', 'webtoolsService', function ($http, languageModel, webtoolsModel, webtoolsService) {

    this.getLanguages = function (callback) {
        var url = webtoolsModel.apiV3Url + "/language/getLangCodeList";
        webtoolsModel.languageLoading++;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            languageModel.languages = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.languageLoading--;
        }, function (errorResp) {
            self.log("languageService.getLanguages - " + self.formatError(errorResp), "Language", true, url);
            webtoolsModel.languageLoading--;
        });
    }

    this.saveLanguage = function (lang, callback) {
        var url = webtoolsModel.apiV3Url + "/settings/setSetting"; //V3
        var data = {};
        data[webtoolsModel.UILanguage] = lang;
        $http({
            method: "PUT",
            url: url,
            data: data
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            self.log("languageService.saveLang - " + self.formatError(errorResp), "Language", true, url);
        });
    }
}]);