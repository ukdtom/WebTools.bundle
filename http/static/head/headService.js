angular.module('webtools').service('headService', ['$http', 'headModel', function ($http, headModel) {

    this.getWebToolsVersion = function (callback) {
        $http.get("/version")
            .then(function (resp) {
                headModel.webtoolsVersion = "WebTools - v" + resp.data.version;
                if (callback) callback(resp.data);
            });
    };
}]);