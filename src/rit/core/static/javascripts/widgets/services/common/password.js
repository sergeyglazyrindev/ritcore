define(function (require) {
    var angular = require('angular'),
        app = angular.module('app');
    app.service('PasswordService', ['$q', function ($q) {
        this.validate = function (password) {
            var defer = $q.defer();
            setTimeout(function () {
                if (!password) {
                    defer.resolve();
                    return;
                }
                var error = '';
                if (password.length < 8) {
                    error = '8 characters or more! Be tricky.';
                }
                else if (!/[a-z]{1,}/.test(password)) {
                    error = 'Add at least one small letter (i.e. a)';
                }
                else if (!/\d{1,}/i.test(password)) {
                    error = 'Add at least one number (i.e. 12)';
                }
                else if (!/[A-Z]{1,}/.test(password)) {
                    error = 'Add at least one letter (i.e. A)';
                }
                else if (!/[\^\&\!\@\#\$\%\&\*\(\)<\>\?]{1,}/.test(password)) {
                    error = 'Add at least one special character (i.e. ^&!@#$%&*()<>?)';
                }
                error && defer.reject(error);
                error || defer.resolve();
            }, 2);
            return defer.promise;
        };
    }]);
});
