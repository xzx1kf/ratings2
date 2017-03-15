from scipy.stats import poisson
from sqlalchemy.sql import func

from app import db
from models import Fixture, League, League_Stats, Prediction, Team, Team_Stats


def fixture_stats():
    """
    Calculate the predicted home and away goals for a fixture
    and store those values in the database.
    """
    fixtures = db.session.query(Fixture).filter_by(completed=False)
    for fixture in fixtures:
        league_stats = db.session.query(League_Stats).filter_by(
            league_id=fixture.league_id).one()

        home_stats = db.session.query(Team_Stats).filter_by(
            team_id=fixture.home_team_id).one()

        away_stats = db.session.query(Team_Stats).filter_by(
            team_id=fixture.away_team_id).one()

        home_goals = (home_stats.home_attack_strength) * (
            away_stats.away_defense_strength) * (
                league_stats.avg_home_goals)

        away_goals = (away_stats.away_attack_strength) * (
            home_stats.home_defense_strength) * (
                league_stats.avg_away_goals)

        prediction = db.session.query(Prediction).filter_by(
            fixture_id=fixture.id).first()

        if not prediction:
            prediction = Prediction(fixture)

        prediction.home_goals = home_goals
        prediction.away_goals = away_goals

        _fixture_probabilities(fixture, prediction)
    db.session.commit()


def _fixture_probabilities(fixture, prediction):
    """
    Given some fixtures calculate the probability of a home, draw
    or away result using the poisson probability mass function.
    """
    home = {"probability": 0}
    away = {"probability": 0}
    draw = {"probability": 0}
    under_over = {"under": 0, "over": 0}

    for i in range(6):
        home[i] = poisson.pmf(i, fixture.prediction.home_goals)
        away[i] = poisson.pmf(i, fixture.prediction.away_goals)

    for a in range(5):
        for h in range(a+1, 6):
            home['probability'] += home[h] * away[a]
            away['probability'] += away[h] * home[a]

            if h + a <= 2:
                under_over['under'] += home[h] * away[a]
                under_over['under'] += away[h] * home[a]
            else:
                under_over['over'] += home[h] * away[a]
                under_over['over'] += away[h] * home[a]

    for i in range(6):
        draw['probability'] += home[i] * away[i]
        if i < 2:
            under_over['under'] += home[i] * away[i]
        else:
            under_over['over'] += home[i] * away[i]

    prediction.home_win = home['probability']
    prediction.away_win = away['probability']
    prediction.draw = draw['probability']
    prediction.over = under_over['over']
    prediction.under = under_over['under']
    prediction.home_goals_pmf = home
    prediction.away_goals_pmf = away


def league_stats():
    """
    Calculate the average home and away goals for each league.
    """
    leagues = db.session.query(League).filter_by(
        active=True)

    for league in leagues:
        fixtures = db.session.query(Fixture).filter_by(
            league_id=league.id,
            completed=True).limit(380)

        league_stats = db.session.query(League_Stats).filter_by(
            league=league).first()

        if not league_stats:
            league_stats = League_Stats(league)

        if fixtures.count() == 0:
            league_stats.avg_home_goals = 1
            league_stats.avg_away_goals = 1
        else:
            home_goals = db.session.query(
                func.sum(fixtures.subquery().columns.home_goals)).scalar()
            away_goals = db.session.query(
                func.sum(fixtures.subquery().columns.away_goals)).scalar()

            league_stats.avg_home_goals = home_goals / fixtures.count()
            league_stats.avg_away_goals = away_goals / fixtures.count()
    db.session.commit()


def _reset_team(team):
    """
    A private function that resets a given teams league table data to zero.

    Returns: a team
    """
    team.played = 0
    team.won = 0
    team.drawn = 0
    team.lost = 0
    team.goals_for = 0
    team.goals_against = 0
    team.goal_difference = 0
    team.points = 0
    return team


def team_stats(number_of_games):
    """
    Calculates a teams home attack and defense strength and their away
    attack and defense strength and stores it in the database.
    """
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
            home_team=team,
            completed=True).order_by(Fixture.date.desc()).limit(
                number_of_games)
        team_stats.home_goals = db.session.query(
            func.sum(home_fixtures.subquery().columns.home_goals)).scalar()
        team_stats.home_goals_conceded = db.session.query(
            func.sum(home_fixtures.subquery().columns.away_goals)).scalar()

        away_fixtures = db.session.query(Fixture).filter_by(
            away_team=team,
            completed=True).order_by(Fixture.date.desc()).limit(
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


def league_tables():
    """
    Calculates a league table for each league and stores it in the
    database.
    """
    leagues = db.session.query(League).filter_by(active=True)

    for league in leagues:
        fixtures = db.session.query(Fixture).filter(
            Fixture.league_id == league.id,
            Fixture.completed == True,
            Fixture.date >= league.start_date
        ).order_by(Fixture.date.desc())

        for team in league.teams:
            team = _reset_team(team)

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

        for pos, team in enumerate(league.teams):
            team.goal_difference = (
                team.goals_for - team.goals_against)
            team.position = pos + 1

    db.session.commit()
