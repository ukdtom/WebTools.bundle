angular.module('webtools').directive('webtoolsLoading', function () {
    return {
        restrict: 'E',
        template: '<div class="webtoolsLoading fa fa-cog fa-spin fa-3x fa-fw"></div>'
    };
});
angular.module('webtools').directive('contentLoading', function () {
    return {
        restrict: 'E',
        template: '<div class="contentLoading fa fa-cog fa-spin fa-3x fa-fw"></div>'
    };
});
angular.module('webtools').directive('inlineLoading', function () {
    return {
        restrict: 'E',
        template: '<div class="inlineLoading fa fa-cog fa-spin fa-3x fa-fw"></div>'
    };
});
angular.module('webtools').directive('inlineLoading2', function () {
    return {
        restrict: 'E',
        template: '<div class="inlineLoading2 fa fa-cog fa-spin fa-3x fa-fw"></div>'
    };
});