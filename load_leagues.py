import argparse
import csv
from app import app, db
from models import League, Team

def import_league_data():
    parser = argparse.ArgumentParser(description='Load league data.')
    parser.add_argument('filename', type=str,
                help='filename for the csv containing the league data')
    args = parser.parse_args()

    with open(args.filename) as csv_file:
        reader = csv.DictReader(csv_file)
        try:
            for row in reader:
                league = League(
                    name=row['Name'],
                    display_name=row['DisplayName'])
                db.session.add(league)
            db.session.commit()
        except:
            print("Error")

def import_team_data():
    parser = argparse.ArgumentParser(description='Load team data.')
    parser.add_argument('filename', type=str,
                help='filename for the csv containing the team data')
    args = parser.parse_args()

    with open(args.filename) as csv_file:
        reader = csv.DictReader(csv_file)
        try:
            for row in reader:
                league_name=row['Division']
                league = db.session.query(League).filter(
                    League.name==league_name).one()               
                team = Team(
                    name=row['Name'],
                    league_id=league.id)
                league.teams.append(team)
                db.session.add(team)
            db.session.commit()
        except e:
            db.session.rollback()
            print("Error: {}".format(e))


if __name__ == '__main__':
    #import_league_data()
    import_team_data()
