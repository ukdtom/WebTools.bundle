angular.module('webtools').service('subModel', function () {
    this.shows = []; //THIS IS BOTH MOVIES & TV SHOWS

    this.deleteCountAsyncRunning = 0;
    this.deleteErrorDialogActive = false;
});