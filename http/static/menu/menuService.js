angular.module('webtools').service('menuService', ['$http', 'menuModel', '$location', '$window', function ($http, menuModel, $location, $window) {
    
    this.navigateTo = function (path) {
        $location.path(path);
    }

    this.redirectTo = function (url, isTargetBlank) {
        if (isTargetBlank)
            window.open(url, '_blank');
        else
            $window.location.href = url;
    }
}]);