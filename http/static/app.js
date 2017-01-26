var webtools = angular.module('webtools', ['ngRoute']);

webtools.config(function ($interpolateProvider, $routeProvider, $locationProvider) {
    $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
    $routeProvider
    .when("/", {
        templateUrl: "/static/home/home.html",
        controller: "homeController"
    })
    .when("/sub", {
        templateUrl: "/static/sub_management/sub.html",
        controller: "subController"
    })
    .otherwise({
        templateUrl: "/static/404/404.html"
    });

    $locationProvider.html5Mode(true);
})