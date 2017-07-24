angular.module('webtools').directive('ngTitle', function () {
    return {
        restrict: 'A',
        scope: {ngTitle: "="},
        link: function (scope, element, attr) {
            var title = scope.ngTitle;
            element.prop('title', title);
        }
    };
});