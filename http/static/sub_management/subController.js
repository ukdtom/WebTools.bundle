angular.module('webtools').controller('subController', ['$scope', 'subModel', 'subService', function ($scope, subModel, subService) {
    $scope.subModel = subModel;

    subService.getShows();

    $scope.expandShow = function (show) {
        show.expanded = !show.expanded;
        if (!show.details) {
            subService.getShowDetails(show);
        }
    }
}]);