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
    db.session.commit()


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

        if fixtures.count() == 0:
            continue

        home_goals = db.session.query(
            func.sum(fixtures.subquery().columns.home_goals)).scalar()
        away_goals = db.session.query(
            func.sum(fixtures.subquery().columns.away_goals)).scalar()

        league_stats = db.session.query(League_Stats).filter_by(
            league=league).first()
        if not league_stats:
            league_stats = League_Stats(league)

        league_stats.avg_home_goals = home_goals / fixtures.count()
        league_stats.avg_away_goals = away_goals / fixtures.count()
    db.session.commit()


def _reset_team(team):
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
    leagues = db.session.query(League).filter_by(active=True)

    for league in leagues:
        fixtures = db.session.query(Fixture).filter_by(
            league_id=league.id,
            completed=True
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

        for team in league.teams:
            team.goal_difference = (
                team.goals_for - team.goals_against)

    db.session.commit()
