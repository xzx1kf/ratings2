from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    team_stats = relationship(
        "Team_Stats",
        uselist=False,
        back_populates="team"
    )

    def __init__(self, name=""):
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
