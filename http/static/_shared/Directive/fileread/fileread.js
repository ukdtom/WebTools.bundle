angular.module('webtools').directive("fileread", [function () {
    return {
        scope: {
            fileread: "="
        },
        link: function (scope, element, attr) {
            element.bind("change", function (changeEvent) {
                var reader = new FileReader();
                reader.onload = function (loadEvent) {
                    scope.$apply(function () {
                        scope.fileread = element[0].files[0];
                        scope.fileread.body = loadEvent.target.result;
                    });
                }
                if (!changeEvent.target.files[0]) return;
                reader.readAsDataURL(changeEvent.target.files[0]);
            });
        }
    }
}]);