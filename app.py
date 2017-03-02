import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from admin import admin
from models import Fixture, Team, Team_Stats


@app.route('/')
def index():
    teams = db.session.query(Team).order_by(Team.name)
    return render_template('index.html', teams=teams)

@app.route('/fixtures')
def fixtures():
    fixtures = db.session.query(Fixture).order_by(Fixture.date)
    return render_template('fixtures.html', fixtures=fixtures)
    
@app.route('/tables')
def tables():
    teams = db.session.query(Team).order_by(Team.points.desc(),
                                            Team.goal_difference.desc())
    return render_template('tables.html', teams=teams)

@app.route('/angular')
def angular():
    return render_template('angular.html')
    
if __name__ == '__main__':
    app.run()
