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
    prediction = relationship("Prediction",
                              uselist=False,
                              back_populates="fixture")

    def __repr__(self):
        return '<id: {}> {} - {} vs {}'.format(
            self.id,
            self.league.display_name,
            self.home_team.name,
            self.away_team.name,
        )


class League(db.Model):
    __tablename__ = 'league'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    display_name = db.Column(db.String())
    active = db.Column(db.Boolean())
    start_date = db.Column(db.DateTime())
    teams = relationship("Team")
    slug = db.Column(db.String(200))
    league_stats = relationship("League_Stats",
                                uselist=False,
                                back_populates="league")

    def __init__(self,
                 name,
                 active=False,
                 start_date=datetime.today()):
        self.name = name
        self.active = active
        self.start_date = start_date

    def __repr__(self):
        return '<id: {}> {}'.format(self.id, self.name)


class League_Stats(db.Model):
    __tablename__ = 'league_stats'

    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, ForeignKey('league.id'))
    league = relationship("League",
                          uselist=False,
                          back_populates="league_stats")
    avg_home_goals = db.Column(db.Float)
    avg_away_goals = db.Column(db.Float)

    def __init__(self, league):
        self.league = league

    def __repr__(self):
        return '<id: {}> {}'.format(self.id, self.league.name)


class Prediction(db.Model):
    __tablename__ = 'prediction'

    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, ForeignKey('fixture.id'))
    fixture = relationship("Fixture",
                           foreign_keys=[fixture_id],
                           uselist=False,
                           back_populates="prediction")
    home_goals = db.Column(db.Float)
    away_goals = db.Column(db.Float)
    home_win = db.Column(db.Float)
    away_win = db.Column(db.Float)
    draw = db.Column(db.Float)
    over = db.Column(db.Float)
    under = db.Column(db.Float)
    home_goals_pmf = db.Column(db.PickleType)
    away_goals_pmf = db.Column(db.PickleType)

    def __init__(self, fixture):
        self.fixture = fixture

    def __repr__(self):
        return '<id: {}> {}'.format(self.id)


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

    def __init__(self, name, league_id):
        self.name = name
        self.league_id = league_id

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
    home_attack_strength = db.Column(db.Float)
    home_defense_strength = db.Column(db.Float)
    away_attack_strength = db.Column(db.Float)
    away_defense_strength = db.Column(db.Float)

    team = relationship(
        "Team", uselist=False, back_populates="team_stats")

    def __init__(self, team):
        self.team = team

    def __repr__(self):
        return '<id: {}> team_id: {}'.format(self.id, self.team_id)
