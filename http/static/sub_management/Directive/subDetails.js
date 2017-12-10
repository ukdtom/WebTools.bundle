angular.module('webtools').directive('subDetails', ['webtoolsService', 'DialogFactory', function (webtoolsService, DialogFactory) {
    return {
        restrict: 'A',
        templateUrl: "static/sub_management/Directive/subDetails.html",
        link: function (scope, element, attr) {
        }
    };
}]);