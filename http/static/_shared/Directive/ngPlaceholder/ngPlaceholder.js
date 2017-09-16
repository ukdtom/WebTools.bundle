angular.module('webtools').directive('ngPlaceholder', function () {
    return {
        restrict: 'A',
        scope: { ngPlaceholder: "=" },
        link: function (scope, element, attr) {
            var placeholder = scope.ngPlaceholder;
            scope.$watch("ngPlaceholder", function (newval) {
                element.prop('placeholder', newval);
            });
            element.prop('placeholder', placeholder);
        }
    };
});