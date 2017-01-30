angular.module('webtools').directive('help', ['webtoolsService', 'DialogFactory', function (webtoolsService, DialogFactory) {
    return {
        restrict: 'E',
        scope: {},
        template: '<div class="fa fa-question-circle" title="Help"></div>',
        link: function (scope, element, attr) {
            var src = attr.src;
            if (!src) {
                webtoolsService.log("Directive Help - src url not defined!", "DirectiveHelp", true);
                return;
            }
            var dialog = new DialogFactory();
            dialog.create(src);

            element.on('click', function (event) {
                event.preventDefault();
                dialog.show();
            });
        }
    };
}]);