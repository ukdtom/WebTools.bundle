angular.module('webtools').controller('subController', ['$scope', 'subModel', 'subService', 'gettext', function ($scope, subModel, subService, gettext) {
    $scope.subModel = subModel;

    $scope.translate = function () {
        var lang = {
            searchPlaceholder: gettext("Search..."),
            searchKeyword: gettext("Search keyword"),
            clearSearch: gettext("Clear search"),
            previous: gettext("Previous"),
            next: gettext("Next"),
            jumpToTop: gettext("Jump to top"),
            hideShowMenu: gettext("Hide/Show search menu"),

            search: gettext("Search..."),
            expandShowToSearch: gettext("Expand a library to search"),

            /* subDetails.html */
            selectAll: gettext("Select All"),
            deselectAll: gettext("Deselect All"),
            uploadSubtitle: gettext("Upload Subtitle"),
            deleteSelected: gettext("Delete Selected"),
            viewSubtitle: gettext("View Subtitle"),
            downloadSubtitle: gettext("Download Subtitle"),
            confirmDeleteQuestion: gettext("Are you sure you want to delete the selected subtitles?"),
            confirmDelete: gettext("Delete")
        };
        $scope.lang = lang;
        $scope.searchPlaceholder = $scope.lang.search;
    }

    $scope.init = function () {
        $scope.translate();
        subService.getSettings();
        subService.getShows();
    }

    $scope.isAnyShowExpanded = function () {
        var isExpanded = false;
        for (var i = 0; i < subModel.shows.length; i++) {
            var show = subModel.shows[i];
            if (show.expanded) isExpanded = true;
        }

        if (isExpanded) $scope.searchPlaceholder = $scope.lang.search;
        else $scope.searchPlaceholder = $scope.lang.expandShowToSearch;
        return isExpanded;
    }

    $scope.filterSub = function () {
        subService.setSettings(function () {
            $scope.searchSub();
        });
    }

    $scope.searchSub = function () {
        for (var i = 0; i < subModel.shows.length; i++) {
            var show = subModel.shows[i];
            $scope.reloadShow(show);
        }
    }

    $scope.reloadShow = function (show) {
        if (show.details && show.type === "movie") {
            show.skip = 0;
            show.full = false;
            show.details = [];
            subService.getMovieDetails(show);
        } else if (show.selectedSeason && show.selectedSeason.details && show.type === "show") {
            show.skip = 0;
            show.full = false;
            show.selectedSeason.details = [];
            subService.getTvShowSeasonDetails(show.selectedSeason);
        }
    }

    $scope.expandShow = function (show) {
        show.expanded = !show.expanded;

        if (!show.letterOptions) { //letterOptions & letter
            subService.getSectionLetterList(show);
        }

        if (!show.details && show.type === "movie") {
            show.details = [];
            subService.getMovieDetails(show);
        } else if (!show.tvshows && show.type === "show") {
            subService.getTvShowDetails(show);
        }
    };

    $scope.expandTvShow = function (show, tvshow) {
        show.selectedTvShow = tvshow;
        if (!tvshow.seasons) {
            subService.getTvShowSeasons(tvshow);
        }
    };
    $scope.expandTvShowSeason = function (show, season) {
        show.selectedSeason = season;
        if (!season.details) {
            subService.getTvShowSeasonDetails(season);
        }
    };

    $scope.loadmore = function (show) {
        if (show.details && show.type === "movie") {
            subService.getMovieDetails(show);
        } else if (show.tvshows && show.type === "show") {
            subService.getTvShowDetails(show);
        }
    }

    $scope.getAllSubtitlesChecked = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].location !== "Embedded" && !detail.subtitles[i].checked) return false;
        }
        return true;
    };

    $scope.toggleAllSubtitles = function (detail) {
        var allChecked = $scope.getAllSubtitlesChecked(detail);
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].location === "Embedded") continue;
            detail.subtitles[i].checked = !allChecked;
        }
        detail.subAllChecked = !allChecked;
    };

    $scope.isCodexView = function (subtitle) {
        return subtitle.codec === "srt"
            || subtitle.codec === "subrip"
            || subtitle.codec === "smi"
            || subtitle.codec === "ssa"
            || subtitle.codec === "vtt"
            || subtitle.codec === "ass";
    }

    $scope.getParts = function(detail) {
        subService.getParts(detail);
    }

    $scope.upload = function (detail) {
        subService.uploadSub(detail, "file");
    };

    $scope.download = function (subtitle, $event) {
        $event.stopPropagation();
        subService.downloadSubtitle(subtitle.key);
    }
    
    $scope.view = function (subtitle, $event) {
        $event.stopPropagation();
        subService.viewSubtitle(subtitle.key);
    }

    $scope.delete = function (detail, subtitle) {
        subService.deleteSubtitle(detail, subtitle);
    };
    $scope.deleteSelected = function (detail) {
        for (var i = 0; i < detail.subtitles.length; i++) {
            if (detail.subtitles[i].checked) $scope.delete(detail, detail.subtitles[i]);
        }
    };


    $scope.searchKeyword = function () {
        if ($scope.subModel.searchKeywordValue && $scope.subModel.searchKeywordValue === $scope.subModel.searchKeywordValueLast) {
            if ($scope.subModel.searchFoundLines.length > 0) $scope.$broadcast("sub_search_nextLine");
        }
        else {
            $scope.$broadcast("sub_search_findKeywords");
        }
    }
    $scope.searchClear = function () {
        $scope.subModel.searchKeywordValue = "";
        $scope.$broadcast("sub_search_findKeywords");
    }
    $scope.searchPrevious = function () {
        if ($scope.subModel.searchFoundLines.length > 0) $scope.$broadcast("sub_search_previousLine");
    }
    $scope.searchJumpToTop = function () {
        $scope.$broadcast("sub_search_jumpToTop");
    }

    $scope.$on("$destroy", function () {
        subModel.selectedSub = null;
    });

    $scope.init();
}]);