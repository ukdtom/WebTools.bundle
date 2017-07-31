angular.module('webtools').service('themeService', ['$http', 'themeModel', 'webtoolsModel', 'webtoolsService', function ($http, themeModel, webtoolsModel, webtoolsService) {
    this.getThemes = function (callback) {
        webtoolsModel.themeLoading = true;

        var url = webtoolsModel.apiV3Url + "/wt/getCSS";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if(resp.data) themeModel.themes = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.themeLoading = false;
        }, function (errorResp) {
            webtoolsService.log("themeService.getThemes - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "Theme", true, url);
            webtoolsModel.themeLoading = false;
        });
    }

    this.loadActiveTheme = function (callback) {
        webtoolsModel.themeLoading = true;
        var url = webtoolsModel.apiV3Url + "/settings/getSettings/" + webtoolsModel.wtCssTheme;
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            themeModel.activeTheme = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.themeLoading = false;
        }, function (errorResp) {
            webtoolsService.log("themeService.loadActiveTheme - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "Theme", true, url);
            webtoolsModel.themeLoading = false;
        });
    }

    this.saveTheme = function (theme, callback) {
        var url = webtoolsModel.apiV3Url + "/settings/setSetting";
        var data = {};
        data[webtoolsModel.wtCssTheme] = theme;
        $http({
            method: "PUT",
            url: url,
            data: data
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("themeService.saveTheme - " + (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!")), "Theme", true, url);
        });
    }
}]);