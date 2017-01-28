angular.module('webtools').service('webtoolsModel', function () {
    this.version = "";
    this.versionFormated = "";
    this.isNewVersionAvailable = false;

    this.apiUrl = "/webtools2";

    this.repoUrl = "https://github.com/ukdtom/WebTools.bundle";
    this.threadUrl = "https://forums.plex.tv/discussion/126254";
});