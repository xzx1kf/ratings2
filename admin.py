from flask import abort, json, request, Response
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.model.ajax import DEFAULT_PAGE_SIZE
from sqlalchemy import or_
from sqlalchemy.sql import func

from app import app, db
from models import Fixture, League, League_Stats, Team, Team_Stats

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
                    ) == filter_by.id)
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

    def calculate_league_stats(self):
        leagues = db.session.query(League).filter_by(
            id=6)

        for league in leagues:
            fixtures = db.session.query(Fixture).filter_by(
                league_id=league.id,
                completed=True)

            league_stats = db.session.query(League_Stats).filter_by(
                league=league).first()
            if not league_stats:
                league_stats = League_Stats(league)
            home_goals = 0
            away_goals = 0

            # Need to make sure that the number of fixtures is the count
            # of home/away matches for each team. Or do I?
            for fixture in fixtures:
                home_goals += fixture.home_goals
                away_goals += fixture.away_goals

            league_stats.avg_home_goals = home_goals / fixtures.count()
            league_stats.avg_away_goals = away_goals / fixtures.count()
        db.session.commit()

    def calculate_team_stats(self, number_of_games):
        teams = db.session.query(Team).all()

        for team in teams:
            league_stats = db.session.query(League_Stats).filter_by(
                league_id=team.league_id).first()
            team_stats = db.session.query(Team_Stats).filter_by(
                team=team).first()
            if not team_stats:
                team_stats = Team_Stats(team)

            # By using the subquery function I first select the records
            # that I'm interested in, then use this as a subquery for the
            # sum function query.
            home_fixtures = db.session.query(Fixture).filter_by(
                home_team=team).order_by(Fixture.date.desc()).limit(
                    number_of_games)
            team_stats.home_goals = db.session.query(
                func.sum(home_fixtures.subquery().columns.home_goals)).scalar()
            team_stats.home_goals_conceded = db.session.query(
                func.sum(home_fixtures.subquery().columns.away_goals)).scalar()

            away_fixtures = db.session.query(Fixture).filter_by(
                away_team=team).order_by(Fixture.date.desc()).limit(
                    number_of_games)
            team_stats.away_goals = db.session.query(
                func.sum(away_fixtures.subquery().columns.away_goals)).scalar()
            team_stats.away_goals_conceded = db.session.query(
                func.sum(away_fixtures.subquery().columns.home_goals)).scalar()

            atk_sth = team_stats.home_goals / number_of_games
            team_stats.home_attack_strength = \
                atk_sth / league_stats.avg_home_goals

            def_sth = team_stats.away_goals_conceded / number_of_games
            team_stats.away_defense_strength = \
                def_sth / league_stats.avg_home_goals

            atk_sth = team_stats.away_goals / number_of_games
            team_stats.away_attack_strength = \
                atk_sth / league_stats.avg_away_goals

            def_sth = team_stats.home_goals_conceded / number_of_games
            team_stats.home_defense_strength = \
                def_sth / league_stats.avg_away_goals

        db.session.commit()

    def calculate_fixture_stats(self):
        tot = db.session.query(Team).filter_by(name="Tottenham").first()
        tot_stats = db.session.query(Team_Stats).filter_by(
            team_id=tot.id).first()

        league_stats = db.session.query(League_Stats).filter_by(
            league_id=tot.league_id).first()

        eve = db.session.query(Team).filter_by(name="Everton").first()
        eve_stats = db.session.query(Team_Stats).filter_by(
            team_id=eve.id).first()

        tot_pred_goals = (tot_stats.home_attack_strength) * (
            eve_stats.away_defense_strength) * (
                league_stats.avg_home_goals)

        eve_pred_goals = (eve_stats.away_attack_strength) * (
            tot_stats.home_defense_strength) * (
                league_stats.avg_away_goals)

        print("{} {} vs {} {}".format(
            tot.name,
            tot_pred_goals,
            eve_pred_goals,
            eve.name))

    def update_league_tables(self):
        try:
            leagues = db.session.query(League).filter_by(
                 active=True)

            for league in leagues:
                fixtures = db.session.query(Fixture).filter_by(
                    league_id=league.id,
                    completed=True).order_by(
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
                self.update_league_tables()
            elif "calculate_league_stats" in request.form:
                self.calculate_league_stats()
                self.calculate_team_stats(number_of_games=19)
                self.calculate_fixture_stats()
        return self.render('admin/options.html')


class TeamView(ModelView):
    form_excluded_columns = ['team_stats', ]


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
admin.add_view(ModelView(League_Stats, db.session))
admin.add_view(TeamView(Team, db.session))
admin.add_view(ModelView(Team_Stats, db.session))
