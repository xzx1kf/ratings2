from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
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
    odds = relationship("Odds",
                        uselist=False,
                        back_populates="fixture")
    
    def __repr__(self):
        return 'Fixture(id={}, date={}, home_team={}, away_team={})'.format(
            self.id,
            self.date,
            self.home_team,
            self.away_team)
    
    def __str__(self):
        return '{:%d/%m/%y %H:%M} - {} vs {}'.format(
            self.date,
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
    teams = relationship("Team", order_by="desc(Team.points)")
    slug = db.Column(db.String(200))
    league_stats = relationship("League_Stats",
                                uselist=False,
                                back_populates="league")

    def __init__(self,
                 name="",
                 active=False,
                 start_date=datetime.today()):
        self.name = name
        self.active = active
        self.start_date = start_date

    def __repr__(self):
        return '<id: {}> {}'.format(self.id, self.name)

    def __str__(self):
        return '{}'.format(self.display_name)


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


class Odds(db.Model):
    __tablename__ = 'odds'
    __table_args__ = (UniqueConstraint('fixture_id'),)

    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, ForeignKey('fixture.id'))
    fixture = relationship("Fixture",
                           foreign_keys=[fixture_id],
                           uselist=False,
                           back_populates="odds")
    home = db.Column(db.Float)
    draw = db.Column(db.Float)
    away = db.Column(db.Float)
    over = db.Column(db.Float)
    under = db.Column(db.Float)

    def __init__(self, fixture, home=1, draw=1, away=1, over=1, under=1):
        self.fixture = fixture
        self.home = home
        self.draw = draw
        self.away = away
        self.over = over
        self.under = under
        
    def __repr__(self):
        return 'Odds(home={}, draw={}, away={}, over={}, under={})'.format(
            self.home,
            self.draw,
            self.away,
            self.over,
            self.under)

    
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

    def __init__(self, fixture, home_goals=0, away_goals=0, home_win=0,
                 away_win=0, draw=0, over=0, under=0):
        self.fixture = fixture
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.home_win = home_win
        self.away_win = away_win
        self.draw = draw
        self.over = over
        self.under = under

    def __repr__(self):
        return '<id: {}> {}'.format(self.id)


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    position = db.Column(db.Integer)
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

    def __str__(self):
        return '{}'.format(self.name)


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
