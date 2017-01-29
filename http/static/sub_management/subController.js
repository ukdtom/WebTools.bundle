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
    };
    $scope.toggleAllSubtitles = function (detail) {
        var allChecked = $scope.getAllSubtitlesChecked(detail);
        for (var i = 0; i < detail.subtitles.length; i++) {
            detail.subtitles[i].checked = !allChecked;
        }
        detail.subAllChecked = !allChecked;
    };

    $scope.upload = function () {

    }

    $scope.delete = function (detail, subtitle) {
        subService.deleteSubtitle(detail, subtitle);
    }
    $scope.deleteSelected = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].checked) $scope.delete(detail, detail.subtitles[i]);
        }
    };
}]);