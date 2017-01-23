var webtools = angular.module('webtools', ['ngRoute']);

webtools.config(function ($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl: "home.html"
    })
    .otherwise({ redirectTo: '/' });
})