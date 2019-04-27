import schedule
import time
import datetime
import requests
import hashlib
import json
import pymongo
import math

with open('config.json') as file_conf:
    conf = json.load(file_conf)

db_string = 'mongodb://{}:{}@{}:{}'.format(conf['mongo']['user'], conf['mongo']['pwd'], conf['mongo']['host'], conf['mongo']['port'])

client = pymongo.MongoClient(db_string)
fixtures = client.betapp.fixtures
results = client.betapp.results

MAPPER = {
    'Arsenal': 'Arsenal FC',
    'Bournemouth': 'AFC Bournemouth',
    'Brighton and Hove Albion': 'Brighton & Hove Albion FC',
    'Burnley': 'Burnley FC',
    'Cardiff City': 'Cardiff City FC',
    'Chelsea': 'Chelsea FC',
    'Crystal Palace': 'Crystal Palace FC',
    'Everton': 'Everton FC',
    'Fulham': 'Fulham FC',
    'Huddersfield Town': 'Huddersfield Town AFC',
    'Leicester City': 'Leicester City FC',
    'Liverpool': 'Liverpool FC',
    'Manchester City': 'Manchester City FC',
    'Manchester United': 'Manchester United FC',
    'Newcastle United': 'Newcastle United FC',
    'Southampton': 'Southampton FC',
    'Tottenham Hotspur': 'Tottenham Hotspur FC',
    'Watford': 'Watford FC',
    'West Ham United': 'West Ham United FC',
    'Wolverhampton Wanderers': 'Wolverhampton Wanderers FC'
}


def predict_result(odd_H, odd_A, odd_D, prob_down=0.17, prob_up=0.36):
    p1 = round(1 / (1 + odd_H/odd_A + odd_H/odd_D), 4)
    p2 = round(1 / (1 + odd_A/odd_H + odd_A/odd_D), 4)
    pX = round(1 / (1 + odd_D/odd_A + odd_D/odd_H), 4)
    if math.fabs(p1 - p2) <= prob_down:
        return p1, p2, pX, 'DRAW'
    elif (p1 - p2) >= prob_up:
        return p1, p2, pX, 'HOME_TEAM'
    elif (p2 - p1) >= prob_up:
        return p1, p2, pX, 'AWAY_TEAM'
    elif math.fabs(p1 - p2) > prob_down and math.fabs(p1 - p2) < prob_up:
        return p1, p2, pX, 'SKIP'


def gather_fixture_matches_and_add_to_db():

    api_key = conf['find_matches']['api_key']
    uri = conf['find_matches']['uri'].format(api_key)

    odds = requests.get(uri)
    result = odds.json()

    matched_count = 0
    modified_count = 0

    for match in result['data']:
        match_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(match['commence_time']))
        home_team = match['home_team']
        home_team_index = match['teams'].index(home_team)
        away_team = match['teams'][1-home_team_index]
        home_team = MAPPER[home_team]
        away_team = MAPPER[away_team]
        bets = []
        probs = []
        for bookmaker in match['sites']:
            odd1_H = bookmaker['odds']['h2h'][home_team_index]
            odd1_A = bookmaker['odds']['h2h'][1-home_team_index]
            odd1_D = bookmaker['odds']['h2h'][2]
            odd1_name = bookmaker['site_nice']
            p1, p2, pX, prediction = predict_result(odd1_H, odd1_A, odd1_D)
            _bets = {
                "bet_name": odd1_name,
                "bet_home": odd1_H,
                "bet_away": odd1_A,
                "bet_draw": odd1_D
            }
            _probs = {
                "prediction": prediction,
                "p1": p1,
                "p2": p2,
                "pX": pX
            }
            bets.append(_bets)
            probs.append(_probs)
        hashs = "{}, {} - {}".format(match_time[:10], home_team, away_team)
        match_hash = hashlib.md5(hashs.encode('utf-8')).hexdigest()[-16:]

        doc = {
              'match_time': datetime.datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S'),
              'home_team': home_team,
              'away_team': away_team,
              'bets': bets,
              'probabilities': probs,
              'match_hash': match_hash,
              'last_updated': time.strftime('%H:%M:%S')
        }

        update_one_output = fixtures.update_one({'match_hash': match_hash}, {'$set': doc}, upsert=True)
        matched_count += update_one_output.matched_count
        modified_count += update_one_output.modified_count


def gather_results_of_matches_and_add_to_db():

    date_from = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    date_to = datetime.date.today().strftime('%Y-%m-%d')

    uri = conf['find_results']['uri'].format(date_from, date_to)
    api_key = conf['find_results']['api_key']
    headers = {'X-Auth-Token': api_key}
    
    result = requests.get(uri, headers=headers)
    result = result.json()

    matched_count = 0
    modified_count = 0

    for item in result['matches']:
        match_time = item['utcDate']
        home_team = item['homeTeam']['name']
        away_team = item['awayTeam']['name']
        hashs = "{}, {} - {}".format(match_time[:10], home_team, away_team)
        match_hash = hashlib.md5(hashs.encode('utf-8')).hexdigest()[-16:]

        doc = {
                'score': {
                    'score_home': item['score']['fullTime']['homeTeam'],
                    'score_away': item['score']['fullTime']['awayTeam'],
                    'result': item['score']['winner'],
                    },
                'last_updated': time.strftime('%H:%M:%S')
                }

        find_one_output = fixtures.find_one({'match_hash': match_hash})
        if find_one_output:
            doc.update(find_one_output)

            delete_one_output = fixtures.delete_one({'match_hash': match_hash})

            update_one_output = results.update_one({'match_hash': match_hash}, {'$set': doc}, upsert=True)
            matched_count += update_one_output.matched_count
            modified_count += update_one_output.modified_count
        else:
            pass


schedule.every().day.at("14:00").do(gather_fixture_matches_and_add_to_db)
schedule.every().hour.do(gather_results_of_matches_and_add_to_db)

while True:
    schedule.run_pending()
    time.sleep(100)

