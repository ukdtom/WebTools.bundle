angular.module('webtools').service('themeService', ['$http', 'themeModel', 'webtoolsModel', 'webtoolsService', function ($http, themeModel, webtoolsModel, webtoolsService) {
    this.getThemes = function (callback) {
        $http.get(webtoolsModel.apiUrl, {
            params: {
                "module": "wt",
                "function": "getCSS"
            }
        }).then(function (resp) {
            if(resp.data) themeModel.themes = resp.data;
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("themeService.getThemes - Themes could not get resolved!", "Theme", true);
        });
    }

    this.loadActiveTheme = function (callback) { 
        $http({
            method: "GET",
            url: webtoolsModel.apiUrl + "?module=settings&function=getSetting&name=wt_csstheme",
        }).then(function (resp) {
            themeModel.activeTheme = resp.data;
            if (callback) callback(resp.data);
        }), function (errorResp) {
            webtoolsService.log("themeService.loadActiveTheme - Theme could not be loaded!", "Theme", true);
        };
    }

    this.saveTheme = function (theme, callback) {
        $http({
            method: "PUT",
            url: webtoolsModel.apiUrl + "?module=settings&function=putSetting&name=wt_csstheme&value=" + theme,
        }).then(function (resp) {
            if (callback) callback(resp.data);
        }), function (errorResp) {
            webtoolsService.log("themeService.saveTheme - Theme could not get saved!", "Theme", true);
        };
    }
}]);