angular.module('webtools').service('menuService', ['$http', 'menuModel', '$location', '$window', function ($http, menuModel, $location, $window) {

    this.navigateTo = function (path) {
        $location.path(path);
    }

    this.logout = function () {
        $window.location.href = '/logout';
    }
}]);