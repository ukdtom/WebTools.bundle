angular.module('webtools').controller('subController', ['$scope', 'subModel', 'subService', function ($scope, subModel, subService) {
    $scope.subModel = subModel;

    subService.getShows();

    $scope.expandShow = function (show) {
        show.expanded = !show.expanded;
        if (!show.details) {
            subService.getShowDetails(show);
        }
    };

    $scope.getAllSubtitlesChecked = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (!detail.subtitles[i].checked) return false;
        }
        return true;
    }
    $scope.toggleAllSubtitlesChecked = function (detail) {
        var allChecked = $scope.getAllSubtitlesChecked(detail);
        for (var i = 0; i < detail.subtitles.length; i++) {
            detail.subtitles[i].checked = !allChecked;
        }
        detail.subAllChecked = !allChecked;
    }
}]);