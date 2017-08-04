angular.module('webtools').directive('ngPlaceholder', function () {
    return {
        restrict: 'A',
        scope: { ngPlaceholder: "=" },
        link: function (scope, element, attr) {
            var placeholder = scope.ngPlaceholder;
            element.prop('placeholder', placeholder);
        }
    };
});