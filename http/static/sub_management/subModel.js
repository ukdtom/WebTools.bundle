angular.module('webtools').service('subModel', function () {
    this.settings = {
        hideWithoutSub: false
    };

    this.shows = []; //THIS IS BOTH MOVIES & TV SHOWS

    this.searchValue = "";

    this.deleteCountAsyncRunning = 0;
    this.deleteErrorDialogActive = false;

    this.selectedSub = null;

    this.searchVisible = true;
    this.searchKeywordValue = "";
    this.searchKeywordValueLast = "";
    this.searchCurrentIndex = 0;
    this.searchFoundLines = [];


    /* SubUpload */
    this.subUploadLoading = false;
    this.showParts = false;
    this.parts = [];
    this.selectedPart = null;
    this.selectedFile = null;
    this.selectedLanguage = "NO_LANG";
    this.missingPart = false;
    this.missingFile = false;
});