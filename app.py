import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from admin import admin
from models import Team, Team_Stats


@app.route('/')
def index():
    teams = db.session.query(Team).order_by(Team.name)
    return render_template('index.html', teams=teams)

@app.route('/add/<name>')
def add_team(name):
    team = Team(
        name=name
    )
    team_stats = Team_Stats(
        team_id = team.id,
    )
    team.team_stats = team_stats

    db.session.add(team)
    db.session.commit()
    teams = db.session.query(Team).order_by(Team.name)
    return render_template('index.html', teams=teams)

@app.route('/tables')
def tables():
    teams = db.session.query(Team).order_by(Team.points, Team.goal_difference)
    return render_template('tables.html', teams=teams)

@app.route('/angular')
def angular():
    return render_template('angular.html')
    
if __name__ == '__main__':
    app.run()
