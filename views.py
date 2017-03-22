from flask import render_template
from sqlalchemy import or_

from app import app, db
from models import Fixture, Team, League


@app.route('/')
def index():
    teams = db.session.query(Team).order_by(Team.name)
    return render_template('index.html', teams=teams)


@app.route('/<league_name>/fixtures')
def fixtures(league_name):
    league = db.session.query(League).filter_by(
        slug=league_name,
        active=True).one()
    fixtures = db.session.query(Fixture).filter_by(
        completed=False,
        league_id=league.id).order_by(Fixture.date)
    return render_template('fixtures.html', fixtures=fixtures)


@app.route('/<league_name>/fixtures/<fixture_id>')
def fixture(league_name, fixture_id):
    fixture = db.session.query(Fixture).get(fixture_id)
    home_fixtures = db.session.query(Fixture).filter_by(
        completed=True,
        home_team_id=fixture.home_team_id).order_by(Fixture.date.desc())[:5]
    home_all_fixtures = db.session.query(Fixture).filter(
        Fixture.completed == True,
        (or_(
            Fixture.home_team_id == fixture.home_team_id,
            Fixture.away_team_id == fixture.home_team_id
        ))).order_by(Fixture.date.desc())[:5]
    away_fixtures = db.session.query(Fixture).filter_by(
        completed=True,
        away_team_id=fixture.away_team_id).order_by(Fixture.date.desc())[:5]
    away_all_fixtures = db.session.query(Fixture).filter(
        Fixture.completed == True,
        (or_(
            Fixture.home_team_id == fixture.away_team_id,
            Fixture.away_team_id == fixture.away_team_id
        ))).order_by(Fixture.date.desc())[:5]
    return render_template('fixture.html',
                           fixture=fixture,
                           home_fixtures=home_fixtures,
                           home_all_fixtures=home_all_fixtures,
                           away_fixtures=away_fixtures,
                           away_all_fixtures=away_all_fixtures)


@app.route('/<league_name>/results')
def results(league_name):
    league = db.session.query(League).filter_by(
        slug=league_name,
        active=True).one()
    results = db.session.query(Fixture).filter_by(
        league_id=league.id,
        completed=True,)
    return render_template('results.html', results=results)


@app.route('/<league_name>/table')
def table(league_name):

    league = db.session.query(League).filter_by(
        slug=league_name).one()

    teams = db.session.query(Team).filter_by(
        league_id=league.id).order_by(
            Team.points.desc(),
            Team.goal_difference.desc())
    return render_template('tables.html', teams=teams)


@app.route('/angular')
def angular():
    return render_template('angular.html')
