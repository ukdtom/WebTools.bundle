angular.module('webtools').directive('subFileDisplay', ['$window', '$document', 'subModel', function ($window, $document, subModel) {
    return {
        restrict: "E",
        scope: {
            data: "="
        },
        link: function (scope, element, attrs) {
            var sub = angular.element(document.querySelector('.sub'));
            sub = sub.parent();

            scope.init = function () {
                //For the best performance (And we do not want HTML/BODY scroll) we have some html inside the JS here..
                var struture = "";
                struture += "<table>";
                for (var i = 1; i <= scope.data.length; i++) {
                    var line = scope.data[i - 1];
                    line = scope.escapeHTML(line);
                    var tr = "<tr id='row" + i + "'>";
                    struture += tr + "<td class='index'>#" + i + "</td><td class='detail'>" + line + "</td></tr>";
                }
                struture += "</table>";
                element.html(struture);
            }

            /* Primary for searching */
            scope.getLineElement = function(id) {
                return angular.element(document.querySelector('#row' + id));
            }
            scope.scrollTo = function (position) {
                sub.stop().animate({ scrollTop: position }, 200);
            }

            scope.revampLine = function () {
                var lineElement = scope.getLineElement(subModel.searchFoundLines[subModel.searchCurrentIndex]);
                lineElement.removeClass("focused");
            }
            scope.changeLine = function () {
                var lineElement = scope.getLineElement(subModel.searchFoundLines[subModel.searchCurrentIndex]);
                lineElement.addClass("focused");
                var scrollTo = lineElement.offset().top + sub.scrollTop();
                scope.scrollTo(scrollTo - 70); //Minus header
            }

            /* Custom for removing html */
            scope.escapeHTML = function(html) {
                return html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }

            /* Broadcast on listeners */
            scope.$on("sub_search_findKeywords", function () {
                subModel.searchCurrentIndex = 0;
                subModel.searchFoundLines = [];
                subModel.searchKeywordValueLast = subModel.searchKeywordValue;

                for (var i = 1; i <= subModel.selectedSub.length; i++) {
                    var detail = subModel.selectedSub[i - 1].toLowerCase();
                    var lineElement = scope.getLineElement(i);
                    if (!lineElement[0]) continue;
                    if (!subModel.searchKeywordValue) {
                        lineElement.removeClass("lineFound");
                        continue;
                    }

                    if (detail.indexOf(subModel.searchKeywordValue.toLowerCase()) !== -1) {
                        subModel.searchFoundLines.push(i);
                        lineElement.addClass("lineFound");
                    } else {
                        lineElement.removeClass("lineFound");
                    }
                }
                if (subModel.searchFoundLines.length > 0) scope.changeLine();
            });

            scope.$on("sub_search_nextLine", function () {
                scope.revampLine();
                subModel.searchCurrentIndex++;
                if (subModel.searchCurrentIndex === subModel.searchFoundLines.length) subModel.searchCurrentIndex = 0;
                scope.changeLine();
            });
            scope.$on("sub_search_previousLine", function () {
                scope.revampLine();
                subModel.searchCurrentIndex--;
                if (subModel.searchCurrentIndex === -1) subModel.searchCurrentIndex = subModel.searchFoundLines.length - 1;
                scope.changeLine();
            });
            scope.$on("sub_search_jumpToTop", function () {
                scope.scrollTo(0);
            });
            
            scope.init();
        }
    }
}]);