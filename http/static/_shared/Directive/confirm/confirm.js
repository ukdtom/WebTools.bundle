angular.module('webtools').directive('confirm', ['ngDialog', function (ngDialog) {
    return {
        restrict: 'A',
        scope: {
            confirm: "=",
            cData: "=",
            cBtnText: "=",
            cText: "="
        },
        link: function (scope, element, attrs) {
            element.on('click', function (event) {
                ngDialog.openConfirm({
                    scope: scope,
                    template: "static/_shared/Directive/confirm/confirm.html",
                }).then(function (confirm) {
                    if (scope.cData) scope.confirm(scope.cData);
                    else scope.confirm();
                }, function (reject) {
                });

            });
        },

    }
}]);