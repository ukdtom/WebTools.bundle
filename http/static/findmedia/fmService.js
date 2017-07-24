angular.module('webtools').service('fmService', ['$http', 'fmModel', 'webtoolsModel', 'webtoolsService', function ($http, fmModel, webtoolsModel, webtoolsService) {
    _this = this;

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
        fmModel.settingsLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/getSettings";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            fmModel.settings = resp.data;

            fmModel.settings.VALID_EXTENSIONS_TEMP = "";
            if(fmModel.settings.VALID_EXTENSIONS){
                for (var i = 0; i < fmModel.settings.VALID_EXTENSIONS.length; i++) {
                    var validExtension = fmModel.settings.VALID_EXTENSIONS[i];
                    fmModel.settings.VALID_EXTENSIONS_TEMP += validExtension;
                    if (i + 1 !== fmModel.settings.VALID_EXTENSIONS.length) {
                        fmModel.settings.VALID_EXTENSIONS_TEMP += ",";
                    }
                }
            }

            if (callback) callback(resp.data);
            fmModel.settingsLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.getSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            fmModel.settingsLoading = false;
        });
    }
    
    this.setSettings = function (callback) {
        if (!fmModel.settings) {
            console.log("No settings!?");
            return;
        }
        fmModel.settingsLoading = true;

        if (!fmModel.settings.VALID_EXTENSIONS_TEMP) {
            fmModel.settings.VALID_EXTENSIONS = [];
        }
        else {
            fmModel.settings.VALID_EXTENSIONS_TEMP = fmModel.settings.VALID_EXTENSIONS_TEMP.replace(/\s/g, '');
            fmModel.settings.VALID_EXTENSIONS = fmModel.settings.VALID_EXTENSIONS_TEMP.split(',');
        }

        var url = webtoolsModel.apiV3Url + "/findMedia/setSettings";
        $http({
            method: "POST",
            url: url,
            data: {
                IGNORE_HIDDEN: fmModel.settings.IGNORE_HIDDEN,
                IGNORE_EXTRAS: fmModel.settings.IGNORE_EXTRAS,
                IGNORED_DIRS: fmModel.settings.IGNORED_DIRS,
                VALID_EXTENSIONS: fmModel.settings.VALID_EXTENSIONS,
            }
        }).then(function (resp) {
            //fmModel.settings = resp.data;
            if (callback) callback(resp.data);
            fmModel.settingsLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.setSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            fmModel.settingsLoading = false;
        });
    }
    
    this.resetSettings = function (callback) {
        fmModel.settingsLoading = true;
        var url = webtoolsModel.apiV3Url + "/findMedia/resetSettings";
        $http({
            method: "PUT",
            url: url,
        }).then(function (resp) {
            _this.getSettings();
            if (callback) callback(resp.data);
            fmModel.settingsLoading = false;
        }, function (errorResp) {
            webtoolsService.log("fmService.resetSettings - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            fmModel.settingsLoading = false;
        });
    }
    
    this.getStatus = function (callback) {
        var url = webtoolsModel.apiV3Url + "/findMedia/getStatus";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            if (resp.data === "Idle" && fmModel.scanning) {
                _this.getResult();
            }
            fmModel.statusText = resp.data;
            fmModel.scanning = resp.data !== "Idle"; //Meeeh not good to check for Idle..
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("fmService.getStatus - " + webtoolsService.formatError(errorResp), "Fm", true, url);
        });
    }
    
    this.getResult = function (callback) {
        var url = webtoolsModel.apiV3Url + "/findMedia/getResult";
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            fmModel.selectedSection.result = resp.data;
            if (fmModel.selectedSection) {
                for (var i = 0; i < fmModel.sections.length; i++) {
                    var section = fmModel.sections[i];
                    if (section.key === fmModel.selectedSection.key) {
                        section.result = resp.data;
                    }
                }
            }
            fmModel.scanning = false;
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("fmService.getResult - " + webtoolsService.formatError(errorResp), "Fm", true, url);
        });
    }
    
    this.abort = function (callback) {
        var url = webtoolsModel.apiV3Url + "/findMedia/abort";
        $http({
            method: "PUT",
            url: url,
        }).then(function (resp) {
            fmModel.scanning = false;
            _this.getStatus();
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("fmService.abort - " + webtoolsService.formatError(errorResp), "Fm", true, url);
        });
    }
    
    this.scanSection = function (sectionNr, callback) {
        var url = webtoolsModel.apiV3Url + "/findMedia/scanSection/" + sectionNr;

        fmModel.scanning = true;
        $http({
            method: "GET",
            url: url,
        }).then(function (resp) {
            _this.getStatus();
            if (callback) callback(resp.data);
        }, function (errorResp) {
            webtoolsService.log("fmService.scanSection - " + webtoolsService.formatError(errorResp), "Fm", true, url);
            fmModel.scanning = false;
        });
    }
}]);