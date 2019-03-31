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

def convert_team_name(nameTeam):
    nameTeam = nameTeam.replace(' FC', '')
    nameTeam = nameTeam.replace('AFC ', '')
    nameTeam = nameTeam.replace(' AFC', '')
    nameTeam = nameTeam.replace('&', 'and')
    return nameTeam


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


def find_matches():

    api_key = conf['find_matches']['api_key']
    uri = conf['find_matches']['uri'].format(api_key)

    odds = requests.get(uri)
    result = odds.json()

    matched_count = 0
    modified_count = 0

    for match in result['data']:
        match_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(match['commence_time']))
        home_team = match['home_team']
        index_ = match['teams'].index(home_team)
        away_team = match['teams'][1-index_]
        #away_team = [team for team in match['teams'] if team != home_team][0]
        bets = []
        probs = []
        for bookmaker in match['sites']:
            odd1_H, odd1_A, odd1_D, odd1_name = bookmaker['odds']['h2h'][index_], bookmaker['odds']['h2h'][1-index_], \
                                                bookmaker['odds']['h2h'][2], bookmaker['site_nice']
            p1, p2, pX, prediction = predict_result(odd1_H, odd1_A, odd1_D)
            _bets = {
                "bet_name": odd1_name,
                "bet_home": odd1_H,
                "bet_draw": odd1_A,
                "bet_away": odd1_D
            }
            _probs = {
                "prediction": prediction,
                "p1": p1,
                "p2": p2,
                "pX": pX
            }
            bets.append(_bets)
            probs.append(_probs)
        hashs = "{}, {} - {}".format(match_time, home_team, away_team)
        match_hash = hashlib.md5(hashs.encode('utf-8')).hexdigest()[-16:]

        doc = {
              'match_time': datetime.datetime.utcfromtimestamp(match['commence_time']).replace(tzinfo=datetime.timezone.utc),
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

    return 


def find_results():

    dateFrom = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    dateTo = datetime.date.today().strftime('%Y-%m-%d')

    uri = conf['find_results']['uri'].format(dateFrom, dateTo)
    api_key = conf['find_results']['api_key']
    headers = {'X-Auth-Token': api_key}
    
    result = requests.get(uri, headers=headers)
    result = result.json()

    matched_count = 0
    modified_count = 0
    
    for item in result['matches']:
        match_time = item['utcDate'].replace('T', ' ')[0:-1]
        home_team = convert_team_name(item['homeTeam']['name'])
        away_team = convert_team_name(item['awayTeam']['name'])
        hashs = "{}, {} - {}".format(match_time, home_team, away_team)
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

    return


schedule.every().day.at("08:00").do(find_matches)
schedule.every().hour.do(find_results)

while True:
    schedule.run_pending()
    time.sleep(5)
