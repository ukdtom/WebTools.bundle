angular.module('webtools').directive('help', ['webtoolsService', 'ngDialog', function (webtoolsService, ngDialog) {
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

            element.on('click', function (event) {
                event.preventDefault();
                ngDialog.open({
                    template: src,
                    //className: 'ngdialog-theme-default',
                    width: "600px"
                });
            });
        }
    };
}]);