angular.module('webtools').service('logsModel', function () {
    this.logs = [];
    this.selectedLog = null;
    this.detailsLimit = 500;
});