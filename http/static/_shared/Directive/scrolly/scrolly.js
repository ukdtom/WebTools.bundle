angular.module('webtools').directive('scrolly', function ($window, $document) {
    return {
        link: function (scope, element, attrs) {
            element.on('scroll', function () {
                if (element[0].scrollTop + element.innerHeight() == element[0].scrollHeight - 100) {
                    scope.$eval(attrs.scrolly);
                }
            })
        }
    }
});