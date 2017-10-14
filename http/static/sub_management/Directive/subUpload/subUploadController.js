angular.module('webtools').controller('subUploadController', ['$scope', 'subModel', 'subService', 'languageModel', 'languageService', 'gettext', '$timeout', function ($scope, subModel, subService, languageModel, languageService, gettext, $timeout) {
    $scope.dialog = $scope.$parent;

    $scope.show = $scope.$parent.show;
    $scope.detail = $scope.$parent.detail;

    $scope.subModel = subModel;
    $scope.languageModel = languageModel;
    
    $scope.init = function () {
        subModel.selectedFile = null;
        subModel.selectedPart = null;
        subModel.subUploadLoading = true;

        subService.getParts($scope.detail, function (data) {
            subModel.parts = data;
            subModel.selectedPart = subModel.parts[0].id;
            subModel.subUploadLoading = false;
        });
        languageService.getCodeLanguages();
    }

    $scope.upload = function () {
        if (!subModel.selectedPart) {
            subModel.missingPart = true;
            return;
        }
        if (!subModel.selectedFile) {
            subModel.missingFile = true;
            return;
        }
        subModel.subUploadLoading = true;
        var lang = null;
        if (subModel.selectedLanguage !== "NO_LANG") lang = subModel.selectedLanguage;

        subService.uploadSub($scope.detail, subModel.selectedPart, subModel.selectedFile, lang, function () {
            var show = $scope.show;
            if (show.details && show.type === "movie") {
                show.skip = 0;
                show.full = false;
                show.details = [];
                subService.getMovieDetails(show);
            } else if (show.tvshows && show.type === "show") {
                show.tvshows = [];
                subService.getTvShowDetails(show);
            }
            subModel.subUploadLoading = false; //Not working properly
            $scope.dialog.closeThisDialog();
        });
    }

    $scope.init();
}]);