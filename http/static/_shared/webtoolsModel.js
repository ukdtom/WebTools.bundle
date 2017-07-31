angular.module('webtools').service('webtoolsModel', function () {
    this.version = "";
    this.versionFormated = "";
    this.UILanguage = "en";
    this.users = {};
    this.isNewVersionAvailable = false;

    this.globalLoading = 0;
    this.languageLoading = 0;
    this.subLoading = false;
    this.logsLoading = false;
    this.themeLoading = false;
    this.uasLoading = false;
    this.fmLoading = false;
    this.playlistLoading = false;

    this.basePath = "/";
    try {
        var locations = $(location).prop('pathname').split('/');
        if (locations[2]) basePath = "/" + locations[1] + "/";
    }
    catch (err) {
        this.basePath = "/";
    }

    this.apiUrl = "webtools2";
    this.apiV3Url = "api/v3";

    this.optionOnlyMultiple = "options_only_multiple";
    this.optionHideLocal = "options_hide_local";
    this.optionHideIntegrated = "options_hide_integrated";
    this.itemsPerPage = "items_per_page";
    this.wtCssTheme = "wt_csstheme";
    this.UILanguageKey = "UILanguage";

    this.repoUrl = "https://github.com/ukdtom/WebTools.bundle";
    this.threadUrl = "https://forums.plex.tv/discussion/126254";
});