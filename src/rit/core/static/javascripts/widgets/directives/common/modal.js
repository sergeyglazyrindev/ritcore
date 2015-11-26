define(function(require) {
    var angular = require('angular'),
        app = angular.module('app'),
        template = '<div><div class="pull-right"><a class="close rit-modal-close" ng-click="close()">x</a></div><div' +
            ' class="modal-header rit-modal-header"><h3' +
            ' class="modal-title">{{modalTitle}}</h3></div><div class="modal-body"' +
            '  >{{modalHtml}}</div></div>';
    app.directive(
        'ritModal', ['$compile', '$uibModal', function
                     ($compile, $uibModal) {
            return {
                link: function (scope, element, attrs) {
                    var ritView = attrs.ritView,
                        html = require(
                        ['text!widgets/templates/modals/' + ritView.toLowerCase() + '.html'],
                        function (html) {
                            template = template.replace('{{modalTitle}}', attrs.ritTitle);
                            template = template.replace('{{modalHtml}}', html);
                            scope.close = function () {
                                modalInstance.close();
                            };
                            var modalInstance = $uibModal.open({
                                template: template,
                                scope: scope,
                                controller: ritView
                            });
                        });
                }
            };
        }]
    );
});
