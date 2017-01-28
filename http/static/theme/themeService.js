angular.module('webtools').service('themeService', ['$http', 'themeModel', 'webtoolsService', function ($http, themeModel, webtoolsService) {
    this.getThemes = function (callback) {
        $http.get("/webtools2", {
            params: {
                "module": "wt",
                "function": "getCSS"
            }
        }).then(function (resp) {
            if(resp.data) themeModel.themes = resp.data;
            if (callback) callback(resp.data);
        }, function (errroResp) {
            webtoolsService.log("themeService.getThemes - Themes could not get resolved!", "Theme", true);
        });
    }
}]);