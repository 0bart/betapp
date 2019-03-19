import schedule
import time
import datetime
import requests
import hashlib
import json
import pymongo
import math
import sys

with open('config.json') as file_conf:
    conf = json.load(file_conf)

db_string = 'mongodb://{}:{}@{}:{}'.format(conf['mongo']['user'], conf['mongo']['pwd'], conf['mongo']['host'], conf['mongo']['port'])

client = pymongo.MongoClient(db_string)
matches = client.matches.betMatches

def convert_team_name(nameTeam):
    nameTeam = nameTeam.replace(' FC', '')
    nameTeam = nameTeam.replace('AFC ', '')
    nameTeam = nameTeam.replace(' AFC', '')
    nameTeam = nameTeam.replace('&', 'and')
    return nameTeam


def predict_result(odd_H, odd_A, odd_D, prob_down=0.17, prob_up=0.36):
    p1 = 1 / (1 + odd_H/odd_A + odd_H/odd_D)
    p2 = 1 / (1 + odd_A/odd_H + odd_A/odd_D)
    pX = 1 / (1 + odd_D/odd_A + odd_D/odd_H)
    if math.fabs(p1 - p2) <= prob_down:
        return 'DRAW'
    elif (p1 - p2) >= prob_up:
        return 'HOME_TEAM'
    elif (p2 - p1) >= prob_up:
        return 'AWAY_TEAM'
    elif math.fabs(p1 - p2) > prob_down and math.fabs(p1 - p2) < prob_up:
        return 'SKIP'


def find_matches():

    print("I am looging matches")

    uri = conf['find_matches']['uri']
    api_key = conf['find_matches']['api_key']

    with open("results.json", "r") as result:
        results = json.load(result)

    matched_count = 0
    modified_count = 0

    for match in results['data']:
        match_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(match['commence_time']))
        home_team = match['home_team']
        index_ = match['teams'].index(home_team)
        away_team = match['teams'][1-index_]
        away_team = [team for team in match['teams'] if team != home_team][0]
        odd1_H, odd1_A, odd1_D, odd1_name = match['sites'][0]['odds']['h2h'][index_], match['sites'][0]['odds']['h2h'][1-index_], match['sites'][0]['odds']['h2h'][2], match['sites'][0]['site_nice']
        hashs = "{}, {} - {}".format(match_time, home_team, away_team)
        match_hash = hashlib.md5(hashs.encode('utf-8')).hexdigest()[-16:]
        prediction = predict_result(odd1_H, odd1_A, odd1_H)

        doc = {
              'match_time': datetime.datetime.utcfromtimestamp(match['commence_time']).replace(tzinfo=datetime.timezone.utc),
              'home_team': home_team,
              'away_team': away_team,
              'bet': {
                  'bet_name': odd1_name,
                  'bet_home': odd1_H,
                  'bet_away': odd1_A,
                  'bet_draw': odd1_D,
                  },
              'prediction': prediction,
              'score': {
                  'score_home': None,
                  'score_away': None,
                  'result': None,
                  },
              'match_hash': match_hash,
              'last_updated': datetime.datetime.now()
              }

        result = matches.update_one({'match_hash': match_hash}, {'$set': doc}, upsert = True)
        matched_count += result.matched_count
        modified_count += result.modified_count

    return 


def find_results():

    uri = conf['find_results']['uri']
    api_key = conf['find_results']['api_key']

    headers = { 'X-Auth-Token': api_key }
    
    results = requests.get(uri, headers=headers)
    results = results.json()

    matched_count = 0
    modified_count = 0
    
    for item in results['matches']:
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
                'last_updated': datetime.datetime.now(),
                }

        result = matches.update_one({'match_hash': match_hash}, {'$set':  doc})
        matched_count += result.matched_count
        modified_count += result.modified_count

    return


schedule.every(5).minutes.do(find_matches)
schedule.every(5).minutes.do(find_results)

while True:
    schedule.run_pending()
    print("I am in while loop")
    time.sleep(5)
