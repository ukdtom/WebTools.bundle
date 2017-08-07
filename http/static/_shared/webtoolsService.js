angular.module('webtools').service('webtoolsService', ['$http', '$window', '$log', 'webtoolsModel', 'DialogFactory', 'gettextCatalog', function ($http, $window, $log, webtoolsModel, DialogFactory, gettextCatalog) {
    var self = this;
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
    var checkIsNewVersionAvailable = function (callback) {
        if (localStorage.wtGITcheck) return;

        webtoolsModel.globalLoading++;

        var url = webtoolsModel.apiV3Url + "/git/getReleaseInfo/url/" + encodeURIComponent(webtoolsModel.repoUrl) + "/version/latest";
        //var url = webtoolsModel.apiUrl + "?module=git&function=getReleaseInfo&url=" + webtoolsModel.repoUrl + "&version=latest";
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            localStorage.wtGITcheck = true;

            if (resp.data.published_at && anyNewVersion(webtoolsModel.version, resp.data.tag_name)) {
                webtoolsModel.isNewVersionAvailable = true;
            }
            if (callback) callback(resp.data);
            webtoolsModel.globalLoading--;
        }, function (errorResp) {
            self.log("var checkIsNewVersionAvailable - " + self.formatError(errorResp), "Core", true, url);
            webtoolsModel.globalLoading--;
        });
    }

    //Public
    this.formatError = function (errorResp) {
        return (errorResp.data ? errorResp.data : (errorResp ? errorResp : "NO ERROR MSG!"));
    }

    this.loadWebToolsVersion = function (callback) {
        webtoolsModel.globalLoading++;

        var url = "version";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            webtoolsModel.version = resp.data.version;
            webtoolsModel.versionFormated = "WebTools - v" + resp.data.version;
            webtoolsModel.globalLoading--;
            checkIsNewVersionAvailable();
            if (callback) callback(resp.data);
        }, function (errorResp) {
            self.log("webtoolsService.loadWebToolsVersion - " + self.formatError(errorResp), "Core", true, url);
            webtoolsModel.globalLoading--;
        });
    };
    this.loadUsers = function (callback) {
        webtoolsModel.globalLoading++;

        var url = webtoolsModel.apiV3Url + "/wt/getUsers";
        $http({
            method: "GET",
            url: url
        }).then(function (resp) {
            webtoolsModel.users = resp.data;
            console.log(webtoolsModel.users);
            webtoolsModel.globalLoading--;
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsModel.globalLoading--;
        });
    }

    this.upgradeWT = function () {
        webtoolsModel.globalLoading++;
        var url = webtoolsModel.apiV3Url + "/wt/upgradeWT";
        $http({
            method: "PUT",
            url: url
        }).then(function (resp) {
            $window.location.reload(true);
            webtoolsModel.globalLoading--;
        }, function (errorResp) {
            //self.log("webtoolsService.upgradeWT - " + self.formatError(errorResp), "Core", true, url);
            $window.location.reload(true);
            webtoolsModel.globalLoading--;
        });
    }

    //this.getLanguage = function (callback) {
    //    webtoolsModel.globalLoading++;

    //    var url = webtoolsModel.apiV3Url + "/settings/getSettings/UILanguage";
    //    $http({
    //        method: "GET",
    //        url: url
    //    }).then(function (resp) {
    //        debugger;
    //        webtoolsModel.globalLoading--;
    //        if (callback) callback(resp.data);
    //    }, function (errorResp) {
    //        self.log("webtoolsService.getLanguage - " + self.formatError(errorResp), "Core", true, url);
    //        webtoolsModel.globalLoading--;
    //    });
    //}

    this.log = function (text, location, error, errorUrl) {
        if (!location) location = "Empty";

        var text = "Location: " + location + "<br />" + "Error: " + text;
        
        if (text.indexOf("Unexpected token F in JSON at position") !== -1) {
            text += "<br />REQUEST HEADER SET TO JSON, BUT NO JSON.DUMPS";
        }

        if (error) var dialog = new DialogFactory();
        var url = webtoolsModel.apiV3Url + "/logs/entry"; //V3
        $http({
            method: "PUT",
            url: url,
            data: {
                text: text
            }
        }).then(function (resp) {
            if (error) {
                $log.error("Error occurred! " + text);
                dialog.create("<p class='textSize3'>Error occurred!</p><a href='https://github.com/ukdtom/WebTools.bundle' target='_blank'>WebTools</a></p><br /><p><b>Technical Info:</b> <br />Url: " + errorUrl + "<br /> " + text + "</p>");
            }
        }, function (errorResp) {
            $log.error("webtoolsService.log - LOGGING NOT AVAILABLE! - RESPONSE: " + errorResp);
            $log.error("Tried to log: " + text + " " + location);
            if (error) {
                dialog.create("<p class='textSize4'>Fatal error!</p><p class='textSize3'>Please contact DEV</p><p><a href='https://github.com/ukdtom/WebTools.bundle' target='_blank'>WebTools</a></p><br /><p><b>Technical Info:</b> <br />Url: " + errorUrl + "<br /> " + text + "</p><br /><p>LOGGING FAILED! URL: " + url + "</p><p>RESPONSE: " + (errorResp && typeof errorResp.data === 'string' ? errorResp.data : "Response data is not a string!!") + "</p>");
            }
        }).finally(function () {
            if (error) {
                dialog.setPlain();
                dialog.showError();
            }
        });
    };
}]);