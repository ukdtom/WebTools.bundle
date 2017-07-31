'use strict'
var webtools = angular.module('webtools', ['ngRoute', 'ngDialog', 'gettext']);

webtools.config(['$interpolateProvider', '$routeProvider', '$locationProvider', function ($interpolateProvider, $routeProvider, $locationProvider) {
    $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
    $routeProvider
    .when("/", {
        templateUrl: "static/home/home.html",
        controller: "homeController"
    })
    //Tools
    .when("/sub", {
        templateUrl: "static/sub_management/sub.html",
        controller: "subController"
    })
    .when("/logs", {
        templateUrl: "static/logs/logs.html",
        controller: "logsController"
    })
    .when("/uas", {
        templateUrl: "static/uas/uas.html",
        controller: "uasController"
    })
    .when("/fm", {
        templateUrl: "static/findmedia/fm.html",
        controller: "fmController"
    })
    .when("/playlist", {
        templateUrl: "static/playlist/playlist.html",
        controller: "playlistController"
    })
    //Options
    .when("/language", {
        templateUrl: "static/language/language.html",
        controller: "languageController"
    })
    .when("/theme", {
        templateUrl: "static/theme/theme.html",
        controller: "themeController"
    })
    .when("/cl", {
        templateUrl: "static/changelog/cl.html",
        controller: "clController"
    })
    //Otherwise show page doesnt exist 404
    .otherwise({
        templateUrl: "static/404/404.html"
    });
}]);

webtools.run(['$rootScope', 'webtoolsService', 'themeService', 'languageService', 'gettextCatalog', function ($rootScope, webtoolsService, themeService, languageService, gettextCatalog) {
    webtoolsService.loadWebToolsVersion();
    webtoolsService.loadUsers();
    themeService.loadActiveTheme();

    gettextCatalog.baseLanguage = 'en';
    gettextCatalog.currentLanguage = 'en';
    gettextCatalog.debugPrefix = "[!] ";
    gettextCatalog.debug = true; //TODO:: remove

    languageService.loadLanguage();
}]);

webtools.filter('uasSearchBy', ['uasModel', function (uasModel) {
    return function (items, searchValue) {
        if (!searchValue) {
            for (typeName in uasModel.types) {
                var type = uasModel.types[typeName];
                type.viewTotal = type.total;
            }
            return items;
        }

        for (typeName in uasModel.types) {
            var type = uasModel.types[typeName];
            type.viewTotal = 0;
        }

        var filtered = [];
        for (name in items) {
            var item = items[name];
            if (!Number.isInteger(parseInt(name))) items[name].key = name;

            if (item.title.toLowerCase().indexOf(searchValue.toLowerCase()) !== -1) {
                filtered.push(item);

                for (typeName in uasModel.types) {
                    var type = uasModel.types[typeName];
                    for (var i = 0; i < item.type.length; i++) {
                        if (typeName === item.type[i]) {
                            type.viewTotal++;
                        }
                    }
                }
            }
        }

        return filtered;
    };
}]);

webtools.filter('orderObjectBy', function () {
    return function (input, attribute) {
        if (!angular.isObject(input)) return input;

        var array = [];
        for (var objectKey in input) {
            if(!Number.isInteger(parseInt(objectKey))) input[objectKey].key = objectKey;
            array.push(input[objectKey]);
        }

        array.sort(function (a, b) {
            if (a[attribute] < b[attribute]) return -1;
            if (a[attribute] > b[attribute]) return 1;
            return 0;
        });
        return array;
    }
});
//webtools.filter('subSearchFilter', ['subModel', function (subModel) {
//    return function (items, searchResults) {
//        if (searchResults === null) return items;

//        var filtered = [];
//        for (var i = 0; i < items.length; i++) {
//            var item = items[i];
//            for (var searchResult in searchResults) {
//                if (item.key === searchResult) filtered.push(item);
//            }
//        }
//        return filtered;
//    };
//}]);