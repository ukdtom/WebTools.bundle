angular.module('webtools').service('uasModel', function () {
    this.selectedType = null;
    this.types = [];

    this.list = [];
    this.installedList = [];
});