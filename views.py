from flask import render_template

from app import app, db
from models import Fixture, Team

@app.route('/')
def index():
    teams = db.session.query(Team).order_by(Team.name)
    return render_template('index.html', teams=teams)

@app.route('/fixtures')
def fixtures():
    fixtures = db.session.query(Fixture).order_by(Fixture.date)
    return render_template('fixtures.html', fixtures=fixtures)

@app.route('/fixtures/<fixture_id>')
def fixture(fixture_id):
    fixture = db.session.query(Fixture).get(fixture_id)
    return render_template('fixture.html', fixture=fixture)

@app.route('/tables')
def tables():
    teams = db.session.query(Team).order_by(Team.points.desc(),
                                            Team.goal_difference.desc())
    return render_template('tables.html', teams=teams)

@app.route('/angular')
def angular():
    return render_template('angular.html')
