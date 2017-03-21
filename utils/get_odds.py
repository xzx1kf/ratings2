import json
import requests
import urllib
import argparse
from getpass import getpass

from app import db
from models import Odds, Fixture

import sys

def get_session_token(username, password):
    payload = 'username=' + username + '&password=' + password
    headers = {
        'X-Application': 'SMDsyAVkt1mi6WVg',
        'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(
        'https://identitysso.betfair.com/api/certlogin',
        data=payload,
        cert=('./certs/client-2048.crt', './certs/client-2048.key'),
        headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        return response_json['sessionToken']
    else:
        print("Request failed.")


def call_api_ng(session_token, json_request):
    headers = {
        'X-Application': 'SMDsyAVkt1mi6WVg',
        'X-Authentication': session_token,
        'Content-Type': 'application/json'}

    url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'

    try:
        request = urllib.request.Request(
            url,
            json_request.encode('utf-8'),
            headers)
        response = urllib.request.urlopen(request)
        json_response = response.read()
        return json_response.decode('utf-8')
    except urllib.error.URLError as e:
        print("Oops no service available at {}".format(url))
    except urllib.error.HTTPError:
        print("Oops not a valid operation from the service {}".format(url))


def get_event_types(session_token):
    event_type_req = '{"jsonrpc": "2.0",'\
            '"method": "SportsAPING/v1.0/listEventTypes",'\
            '"params": {"filter":{ }}, "id": 1}'
    event_types_response = call_api_ng(session_token, event_type_req)
    event_types_loads = json.loads(event_types_response)
    try:
        event_type_results = event_types_loads['result']
        return event_type_results
    except:
        print('Exception from API-NG {}'.format(event_types_loads['error']))


def get_event_type_id(self, event_types, requestedEventTypeName):
    if(event_types is not None):
        for event in event_types:
            eventTypeName = event['eventType']['name']
            if(eventTypeName == requestedEventTypeName):
                return event['eventType']['id']
    else:
        print('Oops there is an issue with the input')

        
def get_competition_id(competition_results, competition_name):
    if (competition_results is not None):
        for competition in competition_results:
            name = competition['competition']['name']
            if (name == competition_name):
                return competition['competition']['id']
    else:
        print('Oops there is an issue with the input')

    
def get_competitions(session_token, eventTypeID):
    competitions_req = '{"jsonrpc": "2.0", '\
            '"method": "SportsAPING/v1.0/listCompetitions",'\
            '"params": {"filter":{ '\
            '"eventTypeIds" : ["'+str(eventTypeID)+'"],'\
            '"marketCountries":["GB"]  }}, "id": 1}'
    competitions_response = call_api_ng(session_token, competitions_req)
    competition_loads = json.loads(competitions_response)
    try:
        competition_results = competition_loads['result']
        return competition_results
    except:
        print('Exception from API-NG {}'.format(competition_loads['error']))

        
def get_event_id(session_token, competition_id, home_team, away_team):
    events_req = '{"jsonrpc": "2.0",'\
            '"method": "SportsAPING/v1.0/listEvents",'\
            '"params": {"filter":'\
            '{ "competitionIds" : ["'+str(competition_id)+'"],'\
            '"textQuery" : "'+home_team+' '+away_team+'"  }},'\
            '"id": 1}'
    events_response = call_api_ng(session_token, events_req)
    event_loads = json.loads(events_response)
    try:
        event_results = event_loads['result']
        return event_results[0]['event']['id']
    except:
        print('Exception from API-NG {}'.format(event_loads['error']))
        

def get_market_id(session_token, event_id):
    market_req = '{"jsonrpc": "2.0", '\
            '"method": "SportsAPING/v1.0/listMarketCatalogue",'\
            '"params": {"filter":{ "eventIds" : ["'+str(event_id)+'"],'\
            '"marketTypeCodes": ["MATCH_ODDS", "OVER_UNDER_25"] },'\
            '"marketProjection" : ["RUNNER_DESCRIPTION"],'\
            '"maxResults":"10" }, "id": 1}'
    market_response = call_api_ng(session_token, market_req)
    market_loads = json.loads(market_response)
    try:
        market_results = market_loads['result']
        return market_results[0]['marketId'], market_results
    except:
        print('Exception from API-NG {}'.format(market_loads['error']))

        
def get_market_book(session_token, market_id):
    market_req = '{"jsonrpc": "2.0",'\
            '"method": "SportsAPING/v1.0/listMarketBook",'\
            '"params": {"marketIds" : ["'+str(market_id)+'"],'\
            '"priceProjection":{"priceData":["EX_BEST_OFFERS"]}},'\
            '"id": 1}'
    market_response = call_api_ng(session_token, market_req)
    market_loads = json.loads(market_response)
    try:
        market_results = market_loads['result']
        return market_results
    except:
        print('Exception from API-NG'.format(market_loads['error']))

        
def get_odds():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='provide your betfair username')
    parser.add_argument('-p', '--password', action='store_true',
                        dest='password', help='provide your betfair password')
    args = parser.parse_args()

    if args.password:
        password = getpass()

    session_token = get_session_token(args.username, password)
            
    """Create odds for matches that haven't been played yet."""
    # Get all matches that haven't been played yet.
    fixtures = db.session.query(Fixture).filter_by(completed=False)
    # Get a list of all event types in betfair.
    event_types = get_event_types(session_token)
    # Search for the 'soccer' event type id.
    soccer_event_type_id = get_event_type_id(session_token,
                                             event_types,
                                             'Soccer')
    # Get all soccer competitions.
    soccer_competitions = get_competitions(session_token, soccer_event_type_id)

    # Find the competition ids for specific competitions.
    competition_ids = {}
    competition_ids['English Premier League'] = get_competition_id(
        soccer_competitions,
        'English Premier League')
    competition_ids['The Championship'] = get_competition_id(
        soccer_competitions,
        'The Championship')

    for fixture in fixtures:
        competition_name = fixture.league.betfair_name
        competition_id = competition_ids[competition_name]

        # Get the betfair event id for the match using the
        # home/away team names in the text search string.
        event_id = get_event_id(session_token,
                                competition_id,
                                fixture.home_team.betfair_name,
                                fixture.away_team.betfair_name)

        market_id, markets = get_market_id(session_token, event_id)

        # TODO: should these names be extracted from betfair?
        over_under_market_name = 'Over/Under 2.5 Goals'
        match_odds_market_name = 'Match Odds'
        under_25_goals = 'Under 2.5 Goals'
        over_25_goals = 'Over 2.5 Goals'

        if markets[0]['marketName'] == over_under_market_name:
            over_under_market = markets[0]
            match_odds_market = markets[1]
        else:
            over_under_market = markets[1]
            match_odds_market = markets[0]

        # Extract the match odds from the betfair market.
        prices = {}
        for runner in match_odds_market['runners']:
            prices[runner['selectionId']] = {}
            prices[runner['selectionId']] = {
                'name': runner['runnerName']}

        match_odds_market_book = get_market_book(
            session_token,
            match_odds_market['marketId'])

        try:
            for runner in match_odds_market_book[0]['runners']:
                prices[runner['selectionId']].update({
                    'odds': runner['ex']['availableToBack'][0]['price']
                })
        except:
            print('Failed to create odds for match "%s"' % (fixture))
            print('Unexpected error:', sys.exc_info()[0])
            continue

        # Extract the over/under odds from the betfair market
        over_under_prices = {}
        for runner in over_under_market['runners']:
            over_under_prices[runner['selectionId']] = {
                    'name': runner['runnerName']}

        under_25_odds = 0
        over_25_odds = 0
        over_under_market_book = get_market_book(
            session_token,
            over_under_market['marketId'])

        try:
            for runner in over_under_market_book[0]['runners']:
                if runner['ex']['availableToBack']:
                    over_under_prices[runner['selectionId']].update({
                        'odds': runner['ex']['availableToBack'][0]['price']
                    })
                else:
                    over_under_prices[runner['selectionId']].update({
                        'odds': 1.0
                    })
        except:
            print('Failed to create odds for match "%s"' % (fixture))
            print('Unexpected error:', sys.exc_info()[0])
            continue

        odds = db.session.query(Odds).filter_by(
            fixture_id=fixture.id).first()

        if odds:
            created = True
        else:
            created = False

        for k, v in prices.items():
            if v['name'] == fixture.home_team.betfair_name:
                odds.home = v['odds']
            elif v['name'] == fixture.away_team.betfair_name:
                odds.away = v['odds']
            else:
                odds.draw = v['odds']

        for selection_id, price_info in over_under_prices.items():
            if price_info['name'] == over_25_goals:
                odds.over = price_info['odds']
            elif price_info['name'] == under_25_goals:
                odds.under = price_info['odds']

        action = "updated"
        if created:
            action = "created"
        print('Successfully %s odds for fixture "%s"' % (action, fixture))
        
    db.session.commit()


if __name__ == '__main__':
    get_odds()
