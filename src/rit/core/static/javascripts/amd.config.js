requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: '/static/javascripts/',
    paths: {
        'angular': 'ritcore/vendor/angular.min',
        'angular.router': 'ritcore/vendor/angular-ui-router.min',
        'underscore': 'ritcore/vendor/underscore-min',
        'angular.ui': 'ritcore/vendor/ui-bootstrap-tpls-0.14.3.min',
        'text': 'ritcore/vendor/require/text',
        'angular.sanitize': 'ritcore/vendor/angular/angular-sanitize.min'
    },
    shim: {
        'angular.router': {
            deps: ['angular']
        },
        'angular': {
            exports: 'angular'
        },
        'angular.ui': {
            deps: ['angular']
        }
    },
    urlArgs: "bust=" + (new Date()).getTime()
});
