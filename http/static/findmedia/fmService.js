angular.module('webtools').service('fmService', ['$http', 'fmModel', 'webtoolsModel', function ($http, fmModel, webtoolsModel) {

    this.getSectionsList = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/getSectionsList";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            fmModel.sections = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.getSectionsList - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.getSettings = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/getSettings";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            fmModel.settings = resp.data;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.getSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.setSettings = function (ignoreHidden, ignoreDirs, callback) {
        if(!ignoreHidden) ignoreHidden = false;
        if(!ignoreDirs) ignoreDirs = [];
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/setSettings";
        $http({
            method: "GET",
            url: url,
            data: {
                IGNORE_HIDDEN: ignoreHidden,
                IGNORE_DIRS: ignoreDirs,
            }
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.setSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.resetSettings = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/resetSettings";
        $http({
            method: "PUT",
            url: url,
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.resetSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.getStatus = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/getStatus";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.getStatus - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.getResult = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/getResult";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.getResult - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.abort = function (callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/abort";
        $http({
            method: "PUT",
            url: url,
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.abort - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
    
    this.scanSection = function (sectionNr, callback) {
        webtoolsModel.fmLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/scanSection/" + sectionNr;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            debugger;
            if (callback) callback(resp.data);
            webtoolsModel.fmLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.scanSection - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            webtoolsModel.fmLoading = false;
        });
    }
}]);