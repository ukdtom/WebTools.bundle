angular.module('webtools').service('languageService', ['$http', 'languageModel', 'webtoolsModel', 'webtoolsService', 'gettextCatalog', function ($http, languageModel, webtoolsModel, webtoolsService, gettextCatalog) {
    var self = this;

    this.getLanguages = function (callback) {
        var url = webtoolsModel.apiV3Url + "/wt/getLanguageList";
        webtoolsModel.languageLoading++;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            languageModel.languages = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.languageLoading--;
        }, function (errorResp) {
            webtoolsService.log("languageService.getLanguages - " + webtoolsService.formatError(errorResp), "Language", true, url);
            webtoolsModel.languageLoading--;
        });
    }

    this.getCodeLanguages = function (callback) {
        var url = webtoolsModel.apiV3Url + "/language/getLangCodeList";
        webtoolsModel.languageLoading++;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            var list = [];
            for (var key in resp.data) {
                var item = resp.data[key];
                list.push({
                    code: item,
                    name: key
                });
            }
            languageModel.codeLanguages = list;
            if (callback) callback(resp.data);
            webtoolsModel.languageLoading--;
        }, function (errorResp) {
            webtoolsService.log("languageService.getCodeLanguages - " + webtoolsService.formatError(errorResp), "Language", true, url);
            webtoolsModel.languageLoading--;
        });
    }

    this.loadLanguage = function (callback) {
        var url = webtoolsModel.apiV3Url + "/settings/getSettings/" + webtoolsModel.UILanguageKey;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            webtoolsModel.UILanguage = resp.data;
            gettextCatalog.currentLanguage = webtoolsModel.UILanguage;
            gettextCatalog.setCurrentLanguage(webtoolsModel.UILanguage);
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("languageService.loadLanguage - " + webtoolsService.formatError(errorResp), "Language", true, url);
        });
    }

    this.saveLanguage = function (lang, callback) {
        gettextCatalog.currentLanguage = lang;

        var url = webtoolsModel.apiV3Url + "/settings/setSetting";
        var data = {};
        data[webtoolsModel.UILanguageKey] = lang;
        $http({
            method: "PUT",
            url: url,
            data: data
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("languageService.saveLang - " + webtoolsService.formatError(errorResp), "Language", true, url);
        });
    }

    this.forceLangUpdate = function(lang, callback) {
        var url = webtoolsModel.apiV3Url + "/wt/updateLanguage/lang/" + lang;
        webtoolsModel.languageLoading++;
        $http({
            method: "POST",
            url: url
        }).then(function (resp) {
            if (callback) callback(resp.data);
            webtoolsModel.languageLoading--;
        }, function (errorResp) {
            webtoolsService.log("languageService.forceLangUpdate - " + webtoolsService.formatError(errorResp), "Language", true, url);
            webtoolsModel.languageLoading--;
        });
    }
}]);