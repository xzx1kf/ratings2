import os
import unittest
from datetime import datetime
import requests

from config import basedir
from app import app, db
from models import League, Team, Fixture

from sqlalchemy.exc import IntegrityError


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

    def test_can_add_league(self):
        db.session.add(self.league1)
        db.session.commit()

        leagues = db.session.query(League).all()
        self.assertTrue(len(leagues) == 1)
        self.assertEqual(leagues[0].name, "Test League 1")

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

    def test_empty_db(self):
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

        league = db.session.query(League).filter_by(
            slug=self.league1.slug,
            active=True).one()

        fixtures = db.session.query(Fixture).filter_by(
            completed=False,
            league_id=league.id).order_by(Fixture.date)

        rv = self.app.get('/testleague1/fixtures')
        print(rv.status_code)
        self.assertEqual(rv.status_code, "200")


if __name__ == '__main__':
    unittest.main()
