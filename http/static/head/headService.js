angular.module('webtools').service('headService', ['$http', 'headModel', 'menuModel', 'webtoolsModel', function ($http, headModel, menuModel, webtoolsModel) {

    //Private
    var anyNewVersion = function (currentVersion, latestVersion) {
        currentVersion = currentVersion.split(" ")[0].toString().split('.');
        latestVersion = latestVersion.split(" ")[0].toString().split('.');
        for (var i = 0; i < (Math.max(currentVersion.length, latestVersion.length)) ; i++) {
            if (!currentVersion[i]) currentVersion[i] = 0;
            if (!latestVersion[i]) latestVersion[i] = 0;
            if (Number(currentVersion[i]) < Number(latestVersion[i])) {
                return true;
            }
            if (Number(currentVersion[i]) > Number(latestVersion[i])) {
                return false;
            }
        }
        return false;
    }

    //Private
    var checkIsNewVersionAvailable = function (callback) {
        var log_name = "var checkIsNewVersionAvailable - ";
        $http.get("/webtools2", {
            params: {
                "module": "git",
                "function": "getReleaseInfo",
                "url": webtoolsModel.repoUrl,
                "version": "latest",
            }
        }).then(function (resp) {
            if (resp.data.published_at && anyNewVersion(headModel.webtoolsVersion, resp.data.tag_name)) {
                menuModel.isNewVersionAvailable = true;
            }
            if (callback) callback(resp.data);
        }, function (errroResp) {
            console.log(log_name + "Error occurred! Response: " + errroResp);
        });
    }

    this.initWebToolsVersion = function (callback) {
        $http.get("/version")
            .then(function (resp) {
                headModel.webtoolsVersion = resp.data.version;
                headModel.webtoolsVersionFormated = "WebTools - v" + resp.data.version;
                checkIsNewVersionAvailable();
                if (callback) callback(resp.data);
            });
    };
}]);