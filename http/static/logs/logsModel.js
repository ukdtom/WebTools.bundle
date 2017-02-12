angular.module('webtools').service('logsModel', function () {
    this.logs = [];
    this.selectedLog = null;
    this.detailsLimit = 500;

    this.searchVisible = true;
    this.searchKeywordValue = "";
    this.searchKeywordValueLast = "";
    this.searchCurrentIndex = 0;
    this.searchFoundLines = [];
    
});