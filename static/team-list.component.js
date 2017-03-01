angular.
    module('footballRatings').
    component('teamList', {
	template:
	'<ul>' +
	    '<li ng-repeat="team in $ctrl.teams">' +
	    '<span>{{team.name}}</span>' +
	    '<span>{{team.played}}</span>' +
	    '<span>{{team.won}}</span>' +
	    '</li>' +
	    '</ul>',
	controller: function TeamListController() {
	    this.teams = [
		{
		    name: 'Liverpool',
		    played: '4',
		    won: '4'
		}
	    ];
	}
    });
