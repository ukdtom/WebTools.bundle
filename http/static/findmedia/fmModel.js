angular.module('webtools').service('fmModel', function () {
    this.settingsVisible = false;
    this.settingsLoading = false;
    this.settings = {};
    this.sections = [];

    this.scanning = false;
    this.statusText = "";
    this.selectedSection = {};
});