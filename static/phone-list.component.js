angular.
    module('phonecatApp').
    component('phoneList', {
	template:
	'<ul>' +
	    '<li ng-repeat="phone in $ctrl.phones">' +
	    '<span>{{phone.name}}</span>' +
	    '<p>{{phone.snippet}}</p>' +
	    '</li>' +
	    '</ul>',
	controller: function PhoneListController() {
	    this.phones = [
		{
		    name: 'Nexus S',
		    snippet: 'Fast just got faster with Nexus S.'
		}
	    ];
	}
    });
