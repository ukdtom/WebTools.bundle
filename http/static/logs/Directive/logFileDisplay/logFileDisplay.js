angular.module('webtools').directive('logFileDisplay', function ($window, $document) {
    return {
        restrict: "E",
        scope: {
            data: "="
        },
        link: function (scope, element, attrs) {
            scope.init = function () {
                //For the best performance (And we do not want HTML/BODY scroll) we have some html inside the JS here..
                var struture = "";
                struture += "<table>";
                for (var i = 1; i <= scope.data.length; i++) {
                    var line = scope.data[i - 1];
                    var tr = (scope.isDanger(line) ? "<tr class='danger'>" : "<tr>");
                    struture += tr + "<td class='index'>#" + i + "</td><td class='detail'>" + line + "</td></tr>";
                }
                struture += "</table>";
                element.html(struture);
            }

            scope.isDanger = function (detail) {
                var detailLower = detail.toLowerCase();
                return detailLower.indexOf('critical') !== -1 || detailLower.indexOf('exception') !== -1 || detailLower.indexOf('error') !== -1;
            }
            scope.init();
        }
    }
});