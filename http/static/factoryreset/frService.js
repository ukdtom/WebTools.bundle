angular.module('webtools').service('frService', ['$http', 'webtoolsModel', 'webtoolsService', 'frModel', function ($http, webtoolsModel, webtoolsService, frModel) {
    _this = this;

    this.factoryReset = function (callback) { 
        webtoolsModel.uasLoading = true;       
        var url = webtoolsModel.apiV3Url + "/wt/reset";
        $http({
            method: "PUT",
            url: url,            
        }).then(function (resp) {
                // Stuff here
        }          
        
    )};                
}]);