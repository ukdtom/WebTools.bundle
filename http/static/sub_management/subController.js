angular.module('webtools').controller('subController', ['$scope', 'subModel', 'subService', function ($scope, subModel, subService) {
    $scope.subModel = subModel;

    subService.getShows();

    $scope.expandShow = function (show) {
        show.expanded = !show.expanded;
        if (!show.details && show.type === "movie") {
            subService.getMovieDetails(show);
        } else if (!show.details && show.type === "show") {
            subService.getTvShowDetails(show);
        }
    };

    $scope.expandTvShow = function (tvshow) {
        $scope.subModel.selectedTvShow = tvshow;
        if (!tvshow.seasons) {
            subService.getTvShowSeasons(tvshow);
        }
    };
    $scope.expandTvShowSeason = function (season) {
        $scope.subModel.selectedSeason = season;
        if (!season.details) {
            subService.getTvShowSeasonDetails(season);
        }
    };

    $scope.getAllSubtitlesChecked = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].location !== "Embedded" && !detail.subtitles[i].checked) return false;
        }
        return true;
    };

    $scope.toggleAllSubtitles = function (detail) {
        var allChecked = $scope.getAllSubtitlesChecked(detail);
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].location === "Embedded") continue;
            detail.subtitles[i].checked = !allChecked;
        }
        detail.subAllChecked = !allChecked;
    };

    $scope.upload = function () {

    };

    $scope.delete = function (detail, subtitle) {
        subService.deleteSubtitle(detail, subtitle);
    };
    $scope.deleteSelected = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].checked) $scope.delete(detail, detail.subtitles[i]);
        }
    };
}]);