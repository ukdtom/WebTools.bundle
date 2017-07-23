
angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
    gettextCatalog.setStrings('en', {"Home":"Home"});
    gettextCatalog.setStrings('da', {"Home":"Hjem"});
}]);