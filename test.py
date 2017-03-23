import os
import unittest
from datetime import datetime

from flask import url_for

from config import basedir
from app import app, db
from models import League, Team, Fixture
from utils import calculate

from sqlalchemy.exc import IntegrityError
from views import *


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
            basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

        self.league1 = League(name="Test League 1")
        self.league2 = League(name="Test League 2")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_league(self, name="Test League 1"):
        league = League(name=name, active=True)
        db.session.add(league)
        db.session.commit()
        return league, league.id

    def test_league_view(self):
        league, id = self.create_league()
        resp = self.app.get('/leagues')

        league = League.query.get(id)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(league.name.encode('utf-8'), resp.data)

    def test_no_leagues(self):
        response = self.app.get('/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No leagues to display.', response.data)
        
    def test_league_creation(self):
        league, _ = self.create_league()

        self.assertTrue(isinstance(league, League))
        self.assertEqual(league.__unicode__(), league.name)

    def test_league_name_must_be_unique(self):
        db.session.add(self.league1)
        db.session.commit()

        league2 = League(name="Test League 1")

        with self.assertRaises(IntegrityError):
            db.session.add(league2)
            db.session.commit()

    def test_league_slug_must_be_unique(self):
        db.session.add(self.league1)
        db.session.add(self.league2)
        db.session.commit()

        with self.assertRaises(IntegrityError):
            self.league2.slug = "Test League 1"
            db.session.commit()

    def test_navigate_to_league_fixtures(self):
        db.session.add(self.league1)
        db.session.commit()
        self.league1.slug = "testleague1"
        self.league1.active = True
        db.session.commit()

        team1 = Team("Team 1", league_id=self.league1.id)
        team2 = Team("Team 2", league_id=self.league1.id)
        
        db.session.add(team1)
        db.session.add(team2)
        db.session.commit()

        fixture = Fixture(home_team_id=team1.id, away_team_id=team2.id,
                          league_id=self.league1.id, date=datetime.today())

        db.session.add(fixture)
        db.session.commit()

        # These functions need to run so that stats are generated
        # for the league/teams.
        # TODO: Might want to change this functionality.
        calculate.league_tables()
        calculate.league_stats()
        calculate.team_stats(number_of_games=19)
        calculate.fixture_stats()

        rv = self.app.get('/testleague1/fixtures')
        self.assertEqual(rv.status_code, 200)

    def test_navigate_to_league_table(self):
        pass

if __name__ == '__main__':
    unittest.main()
