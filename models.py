from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Fixture(db.Model):
    __tablename__ = 'fixture'

    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, ForeignKey('league.id'))
    league = relationship("League")
    date = db.Column(db.DateTime())
    home_team_id = db.Column(db.Integer, ForeignKey('teams.id'))
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team_id = db.Column(db.Integer, ForeignKey('teams.id'))
    away_team = relationship("Team", foreign_keys=[away_team_id])
    completed = db.Column(db.Boolean, default=False)
    fulltime_result = db.Column(db.String())
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
        
    def __repr__(self):
        return '<id: {}> {} vs {}'.format(
            self.id,
            self.home_team_id,
            self.away_team_id,
            self.league_id,
        )

class League(db.Model):
    __tablename__ = 'league'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    display_name = db.Column(db.String())
    active = db.Column(db.Boolean())
    start_date = db.Column(db.DateTime())
    teams = relationship("Team")

    def __init__(self, name="", display_name="", active=False,
                 start_date=datetime.today()):
        self.name = name
        self.display_name = display_name
        self.active = active
        self.start_date = start_date

    def __repr__(self):
        return '<id: {}> {}'.format(self.id, self.name)

    
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    played = db.Column(db.Integer, default=0)
    won = db.Column(db.Integer, default=0)
    drawn = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    league_id = db.Column(db.Integer, ForeignKey('league.id'))

    team_stats = relationship(
        "Team_Stats",
        uselist=False,
        back_populates="team"
    )

    def __init__(self, name="", league_id=None):
        self.name = name

    def __repr__(self):
        return '<id: {}> {}'.format(self.id, self.name)


class Team_Stats(db.Model):
    __tablename__ = 'team_stats'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, ForeignKey('teams.id'))
    home_goals = db.Column(db.Integer, default=0)
    away_goals = db.Column(db.Integer, default=0)
    home_goals_conceded = db.Column(db.Integer, default=0)
    away_goals_conceded = db.Column(db.Integer, default=0)

    team = relationship(
        "Team", uselist=False, back_populates="team_stats")

    def __init__(self, home_goals=0, away_goals=0,
                 home_goals_conceded=0, away_goals_conceded=0):
        self.home_goals=home_goals
        self.away_goals=away_goals
        self.home_goals_conceded=home_goals_conceded
        self.away_goals_conceded=away_goals_conceded

    def __repr__(self):
        return '<id: {}> team_id: {}'.format(self.id, self.team_id)
