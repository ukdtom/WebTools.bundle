angular.module('webtools').directive('logFileDisplay', ['$window', '$document', 'logsModel', function ($window, $document, logsModel) {
    return {
        restrict: "E",
        scope: {
            data: "="
        },
        link: function (scope, element, attrs) {
            var logs = angular.element(document.querySelector('.logs'));

            scope.init = function () {
                //For the best performance (And we do not want HTML/BODY scroll) we have some html inside the JS here..
                var struture = "";
                struture += "<table>";
                for (var i = 1; i <= scope.data.length; i++) {
                    var line = scope.data[i - 1];
                    var tr = "<tr id='row" + i + "' class='" + (scope.isDanger(line) ? "danger" : "") + "'>";
                    struture += tr + "<td class='index'>#" + i + "</td><td class='detail'>" + line + "</td></tr>";
                }
                struture += "</table>";
                element.html(struture);
            }
            scope.isDanger = function (detail) {
                var detailLower = detail.toLowerCase();
                
                var index = detailLower.indexOf(" - "); //All occurrences before this part can we check for...
                if(index !== -1){
                    detailLower = detailLower.substring(0, index);
                }
                return detailLower.indexOf('critical') !== -1 || detailLower.indexOf('exception') !== -1 || detailLower.indexOf('error') !== -1;
            }

            /* Primary for searching */
            scope.getLineElement = function(id){
                return angular.element(document.querySelector('#row' + id))
            }
            scope.scrollTo = function (position) {
                logs.stop().animate({ scrollTop: position }, 200);
            }

            scope.revampLine = function () {
                var lineElement = scope.getLineElement(logsModel.searchFoundLines[logsModel.searchCurrentIndex]);
                lineElement.removeClass("focused");
            }
            scope.changeLine = function () {
                var lineElement = scope.getLineElement(logsModel.searchFoundLines[logsModel.searchCurrentIndex]);
                lineElement.addClass("focused");
                var scrollTo = lineElement.offset().top + logs.scrollTop();
                scope.scrollTo(scrollTo - 80); //Minus header
            }

            scope.$on("logs_search_findKeywords", function () {
                logsModel.searchCurrentIndex = 0;
                logsModel.searchFoundLines = [];
                logsModel.searchKeywordValueLast = logsModel.searchKeywordValue;

                for (var i = 1; i <= logsModel.selectedLog.details.length; i++) {
                    var detail = logsModel.selectedLog.details[i - 1].toLowerCase();
                    var lineElement = scope.getLineElement(i);
                    if (!lineElement[0]) continue;
                    if (!logsModel.searchKeywordValue) {
                        lineElement.removeClass("lineFound");
                        continue;
                    }

                    if (detail.indexOf(logsModel.searchKeywordValue.toLowerCase()) !== -1) {
                        logsModel.searchFoundLines.push(i);
                        lineElement.addClass("lineFound");
                    } else {
                        lineElement.removeClass("lineFound");
                    }
                }
                if (logsModel.searchFoundLines.length > 0) scope.changeLine();
            });

            scope.$on("logs_search_nextLine", function () {
                scope.revampLine();
                logsModel.searchCurrentIndex++;
                if (logsModel.searchCurrentIndex === logsModel.searchFoundLines.length) logsModel.searchCurrentIndex = 0;
                scope.changeLine();
            });
            scope.$on("logs_search_previousLine", function () {
                scope.revampLine();
                logsModel.searchCurrentIndex--;
                if (logsModel.searchCurrentIndex === -1) logsModel.searchCurrentIndex = logsModel.searchFoundLines.length - 1;
                scope.changeLine();
            });
            scope.$on("logs_search_jumpToTop", function () {
                scope.scrollTo(0);
            });
            
            scope.init();
        }
    }
}]);