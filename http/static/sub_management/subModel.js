angular.module('webtools').service('subModel', function () {
    this.shows = []; //THIS IS BOTH MOVIES & TV SHOWS

    this.selectedTvShowDetails = null;
    this.selectedTvShow = null;
    this.selectedSeason = null;

    this.deleteCountAsyncRunning = 0;
    this.deleteErrorDialogActive = false;
});