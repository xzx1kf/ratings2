from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from app import app, db
from models import Fixture, League, Team, Team_Stats

from flask_admin.model.ajax import DEFAULT_PAGE_SIZE
from flask import request
from sqlalchemy import or_
from flask import Response
from flask import json


admin = Admin(app, name='Football Ratings', template_mode='bootstrap3')

class FilteredAjaxModelLoader(QueryAjaxModelLoader):
    def get_list(self, term, offset=0,
                 limit=DEFAULT_PAGE_SIZE, filter_by=None):
        query = self.session.query(self.model)
        filter_by_options = self.options.get('filter_by')
        if filter_by_options and filter_by:
            filter_by = self.session.query(
                filter_by_options[0]).filter_by(
                    id=filter_by).first()
            if filter_by:
                query = query.filter(
                    getattr(
                        self.model,
                        filter_by_options[1]
                    )
                    ==filter_by.id)
        filters = (
            field.ilike(
                u'%%%s%%' % term) for field in self._cached_fields)
        query = query.filter(or_(*filters))

        if self.order_by:
            query = query.order_by(self.order_by)

        return query.offset(offset).limit(limit).all()

class OptionsView(BaseView):
    def reset_team(self, team):
        team.played = 0
        team.won = 0
        team.drawn = 0
        team.lost = 0
        team.goals_for = 0
        team.goals_against = 0
        team.goal_difference = 0
        team.points = 0
        return team
        
    def update_league_tables(self):
        try:
            leagues = db.session.query(League).filter_by(
                 active = True)

            for league in leagues:
                fixtures = db.session.query(Fixture).filter_by(
                    league_id = league.id,
                    completed = True).order_by(
                        Fixture.date.desc())

                for team in league.teams:
                    team = self.reset_team(team)

                for fixture in fixtures:
                    home_team = fixture.home_team
                    away_team = fixture.away_team

                    home_team.played += 1
                    away_team.played += 1

                    home_team.goals_for += fixture.home_goals
                    home_team.goals_against += fixture.away_goals
                    away_team.goals_for += fixture.away_goals
                    away_team.goals_against += fixture.home_goals

                    if fixture.fulltime_result == 'H':
                        home_team.won += 1
                        home_team.points += 3
                        away_team.lost += 1
                    elif fixture.fulltime_result == 'D':
                        home_team.drawn += 1
                        away_team.drawn += 1
                        home_team.points += 1
                        away_team.points += 1
                    else:
                        home_team.lost += 1
                        away_team.won += 1
                        away_team.points += 3

                for team in league.teams:
                    team.goal_difference = (
                        team.goals_for - team.goals_against)

            db.session.commit()
        except:
            db.session.rollback()
            
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        if request.method == "POST":
            if "update_league" in request.form:
                print("Put logic to handle update league table here.")
                self.update_league_tables()
                
        return self.render('admin/options.html')

class TeamView(ModelView):
    form_excluded_columns = ['team_stats',]

class FixtureView(ModelView):
    column_filter_by = ('home_team')
    column_filter_by = ('away_team')

    form_widget_args = {
        'home_team': {
            'data-filter-by': 'league',
            },
        'away_team': {
            'data-filter-by': 'league',
            },
        }

    form_ajax_refs = {
        'home_team': FilteredAjaxModelLoader(
            'home_team', db.session, Team,
            fields=('name',),
            page_size=10,
            placeholder='Select home team...',
            filter_by=(League, 'league_id'),
            ),
        'away_team': FilteredAjaxModelLoader(
            'away_team', db.session, Team,
            fields=('name',),
            page_size=10,
            placeholder='Select away team...',
            filter_by=(League, 'league_id'),
            )
        }

    column_list = ('date',
                    'league',
                    'home_team',
                    'away_team',
                    'fulltime_result',
                    'completed')

    form_columns = ('date',
                    'league',
                    'home_team',
                    'away_team',
                    'fulltime_result',
                    'completed')
    


    @expose('/ajax/lookup/')
    def ajax_lookup(self):
        name = request.args.get('name')
        query = request.args.get('query')
        offset = request.args.get('offset', type=int)
        limit = request.args.get('limit', 10, type=int)
        filter_by = request.args.get('filter_by')

        loader = self._form_ajax_refs.get(name)

        if not loader:
            abort(404)

        if name in self.column_filter_by:
            data = [loader.format(m) for m in loader.get_list(
                query, offset, limit, filter_by)]
        else:
            data = [loader.format(m) for m in loader.get_list(
                query, offset, limit)]
        return Response(json.dumps(data), mimetype='application/json')

    """
    The on_model_change allows me to insert some logic. So in the case
    of the fixture save I can calculate fixture stats etc
    """
    def on_model_change(self, form, model, is_created):
        print("{}".format(model.home_team.name))

admin.add_view(OptionsView(name='Options', endpoint='options'))
admin.add_view(FixtureView(Fixture, db.session))
admin.add_view(ModelView(League, db.session))    
admin.add_view(TeamView(Team, db.session))
admin.add_view(ModelView(Team_Stats, db.session))
