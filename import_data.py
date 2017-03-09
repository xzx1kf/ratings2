import argparse
import csv
import datetime
import sys
from app import app, db
from models import League, Team, Fixture

def import_ratings_data():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', help='type of data (league, team, fixture) to import')
    parser.add_argument(
        'file', help='file containing csv  data to import')
    args = parser.parse_args()

    if args.type == 'league':
        import_league_data(args.file)
    elif args.type == 'team':
        import_team_data(args.file)
    elif args.type == 'fixture':
        import_fixture_data(args.file)
        
def import_league_data(csv_file):
    with open(csv_file) as csv_file:
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

def import_team_data(csv_file):
    with open(csv_file) as csv_file:
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
        except:
            db.session.rollback()
            print("Error: {}".format(sys.exc_info()[0]))

def import_fixture_data(csv_file):
    with open(csv_file) as csv_file:
        reader = csv.DictReader(csv_file)
        try:
            for row in reader:
                league_name = row['Div']
                home_team_name = row['HomeTeam']
                away_team_name = row['AwayTeam']
                league = db.session.query(League).filter_by(
                    name = league_name).one()
                print(home_team_name)
                print(away_team_name)
                print(league_name)
                home_team = db.session.query(Team).filter_by(
                    name = home_team_name).one()
                away_team = db.session.query(Team).filter_by(
                    name = away_team_name).one()
                fixture_datetime = datetime.datetime.strptime(
                    row['Date'], '%d/%m/%y')
                fixture_datetime = fixture_datetime.replace(hour=15)

                fixture = Fixture(
                    date = fixture_datetime,
                    league_id = league.id,
                    home_team_id = home_team.id,
                    away_team_id = away_team.id,
                    completed = True,
                    fulltime_result = row['FTR'],
                    home_goals = row['FTHG'],
                    away_goals = row['FTAG'],
                )
                db.session.add(fixture)
            db.session.commit()
        except:
            db.session.rollback()
            print("Type: {}".format(sys.exc_info()[0]))
            print("Value: {}".format(sys.exc_info()[1]))
            print("Traceback: {}".format(sys.exc_info()[2]))
            

if __name__ == '__main__':
    import_ratings_data()
