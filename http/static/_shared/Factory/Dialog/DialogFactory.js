angular.module('webtools').factory('DialogFactory', ['ngDialog', function (ngDialog) {
    var DialogFactory = function () {
        var src = "", controller, scope, plain = false, closeCallback;

        function create(_src, _controller, _scope) {
            src = _src;
            if (_controller) controller = _controller;
            if (_scope) scope = _scope;
        }
        function setPlain() {
            plain = true;
        }
        function closeEvent(_callback) {
            closeCallback = _callback;
        }

        function show() {
            var dialog;

            if (controller && scope) {
                dialog = ngDialog.open({
                    template: src,
                    width: "600px",
                    plain: plain,
                    controller: controller,
                    scope: scope
                });
            } else {
                dialog = ngDialog.open({
                    template: src,
                    width: "600px",
                    plain: plain
                });
            }

            if(closeCallback){
                dialog.closePromise.then(function (data) {
                    closeCallback();
                });
            }
        }
        function showError() {
            var dialog = ngDialog.open({
                template: src,
                width: "600px",
                plain: plain,
                className: 'ngdialog-theme-default error-dialog'
            });

            if (closeCallback) {
                dialog.closePromise.then(function (data) {
                    closeCallback();
                });
            }
        }

        return {
            create: create,
            setPlain: setPlain,
            closeEvent: closeEvent,

            show: show,
            showError: showError
        }
    };
    return DialogFactory;
}]);