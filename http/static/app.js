var webtools = angular.module('webtools', ['ngRoute']);

webtools.config(function ($interpolateProvider, $routeProvider) {
    $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
    $routeProvider
    .when("/", {
        templateUrl: "/static/home/home.html",
        controller: "homeController"
    })
    .otherwise({ redirectTo: '/' });
})