var webtools = angular.module('webtools', ['ngRoute']);

webtools.config(function ($interpolateProvider, $routeProvider) {
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
})