angular.module('webtools').service('menuService', ['$http', 'menuModel', '$location', function ($http, menuModel, $location) {

    this.navigateTo = function (path) {
        $location.path(path);
    }
}]);